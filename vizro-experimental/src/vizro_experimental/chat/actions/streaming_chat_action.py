"""Streaming chat action that pushes response chunks over SSE."""

from __future__ import annotations

import base64
import json
from collections.abc import Callable, Iterator
from typing import Any

import dash
from dash import ClientsideFunction, Input, Output, Patch, State, clientside_callback, no_update
from dash_extensions.streaming import sse_message, sse_options
from flask import Response, request
from pydantic import BaseModel, ConfigDict, Field
from vizro.models._models_utils import _log_call

from ..models.types import Message, _parse_store_messages
from ._base_chat_action import _BaseChatAction, _kwargs_for_generate_response

# Wire-protocol contract shared with the clientside `processStreamingChunk` JS.
# Each chunk is base64-encoded (to survive special characters in the SSE byte
# stream) and suffixed with this delimiter so the JS can split a coalesced SSE
# buffer back into chunks. Keep in sync with static/js/chat.js.
_CHUNK_DELIMITER = "|END|"


class _StreamingRequest(BaseModel):
    """Request payload for streaming chat endpoint.

    Args:
        prompt (str): The user's input prompt.
        messages (list[dict[str, Any]]): Store-shaped history: each dict has ``role`` and ``content_json``.
            Implementations of :meth:`StreamingChatAction.generate_response` receive parsed messages only
            (``role`` + ``content``), decoded from this wire format inside the framework.

    """

    # ``extra="ignore"`` drops unknown JSON keys at validation. This pairs with the
    # ``_kwargs_for_generate_response`` change that no longer treats ``**kwargs`` in
    # an action signature as a wildcard for forwarding extras (VULN-002 hardening).
    # If a custom action needs to receive extra fields from the SSE body, subclass
    # this model with explicit named fields rather than re-enabling ``extra="allow"``.
    model_config = ConfigDict(extra="ignore")

    prompt: str = Field(description="The user's input prompt.")
    messages: list[dict[str, Any]] = Field(
        description="Store-shaped message dicts with 'role' and 'content_json' keys (wire format)."
    )
    uploaded_files: list[dict[str, Any]] | None = Field(
        default=None,
        description="Optional file-store payload from the chat upload (same shape as dcc.Store data).",
    )


def _register_streaming_chunk_callback(chat_id: str) -> None:
    """Register the clientside callback that decodes SSE chunks into the message store."""
    clientside_callback(
        ClientsideFunction("vizroChatComponent", "processStreamingChunk"),
        [
            Output(f"{chat_id}-hidden-messages", "children", allow_duplicate=True),
            Output(f"{chat_id}-store", "data", allow_duplicate=True),
        ],
        Input(f"{chat_id}-sse", "animation"),
        [State(f"{chat_id}-hidden-messages", "children"), State(f"{chat_id}-store", "data")],
        prevent_initial_call=True,
        hidden=True,
    )


def _register_streaming_endpoint(
    server: Any,
    chat_id: str,
    generate_response: Callable[..., Iterator[str]],
    *,
    base_pathname: str,
    endpoint_name: str,
) -> None:
    """Register the Flask SSE route that streams ``generate_response`` chunks."""

    @server.route(f"{base_pathname}/streaming-{chat_id}", methods=["POST"], endpoint=endpoint_name)
    def _streaming_chat() -> Response:
        # _StreamingRequest's extra="ignore" + _kwargs_for_generate_response's
        # named-only forwarding together close mass-parameter-assignment (VULN-002).
        try:
            validated = _StreamingRequest(**(request.get_json() or {}))
        except Exception:
            return Response("Invalid request", status=400)
        gr_kw = _kwargs_for_generate_response(
            generate_response,
            uploaded_files=validated.uploaded_files,
            payload_extras=validated.model_extra or {},
        )

        def event_stream() -> Iterator[str]:
            for chunk in generate_response(_parse_store_messages(validated.messages), **gr_kw):
                encoded = base64.b64encode(chunk.encode("utf-8")).decode("utf-8")
                yield sse_message(encoded + _CHUNK_DELIMITER)
            yield sse_message()

        return Response(event_stream(), mimetype="text/event-stream")


class StreamingChatAction(_BaseChatAction):
    """Streaming chat action for real-time response generation via SSE.

    Subclass this to create custom chat actions that stream responses in real-time.

    Example:
        ```python
        class my_streaming_chat(StreamingChatAction):
            def generate_response(self, messages):
                for chunk in ["Hello", " ", "World!"]:
                    yield chunk
        ```

    """

    @_log_call
    def pre_build(self) -> None:
        """Set up streaming callbacks and endpoint during pre-build phase."""
        super().pre_build()
        _register_streaming_chunk_callback(self._chat_id)
        base_pathname = dash.get_app().config.requests_pathname_prefix.rstrip("/")
        _register_streaming_endpoint(
            dash.get_app().server,
            self._chat_id,
            self.generate_response,
            base_pathname=base_pathname,
            endpoint_name=f"streaming_chat_{self._chat_id}",
        )

    def generate_response(self, messages: list[Message], **kwargs: Any) -> Iterator[str]:
        """Generate a streaming chat response.

        Args:
            messages: Parsed history: each item has ``role`` and ``content`` (decoded from store ``content_json``).
            **kwargs: Optional ``uploaded_files`` or other kwargs only if your implementation accepts them.

        Yields:
            Text chunks to stream to the client.

        Raises:
            NotImplementedError: Must be implemented by subclass.

        """
        raise NotImplementedError("Subclasses must implement generate_response()")

    def function(
        self,
        prompt: str,
        messages: list[dict[str, Any]],
        uploaded_files: list[dict[str, str]] | None = None,
    ) -> list[Any]:
        """Execute the streaming chat action callback.

        Args:
            prompt: User's input text.
            messages: Store-shaped history (`role` + `content_json`); mutated in place when sending.
            uploaded_files: File-store payload at send time. Snapshotted into the new user message
                as ``attachments`` so the bubble renders them and the file-store can clear.

        Returns:
            List of outputs for store, hidden-messages, chat-input, SSE url, SSE options,
            file-store, and data-info (matching ``self.outputs``).

        """
        if not prompt or not prompt.strip():
            return [no_update] * len(self.outputs)

        latest_input: dict[str, Any] = {"role": "user", "content_json": json.dumps(prompt)}
        if uploaded_files:
            latest_input["attachments"] = uploaded_files
        messages.append(latest_input)

        store = Patch()
        store.append(latest_input)

        # For streaming: add empty assistant placeholder, then start SSE
        placeholder_msg = {"role": "assistant", "content_json": json.dumps("")}
        store.append(placeholder_msg)

        html_messages = [self.message_to_html(msg) for msg in messages]
        html_messages.append(self.message_to_html(placeholder_msg))

        sse_request = _StreamingRequest(prompt=prompt, messages=messages, uploaded_files=uploaded_files)

        # Get the base pathname to support deployments with URL prefixes
        base_pathname = dash.get_app().config.requests_pathname_prefix.rstrip("/")

        return [
            store,
            html_messages,
            no_update,
            f"{base_pathname}/streaming-{self._chat_id}",
            sse_options(sse_request),
            [],
            "",
        ]

    @property
    def outputs(self) -> list[str]:
        """Define callback outputs for this action.

        Returns:
            List of output component references.

        """
        return [
            f"{self._chat_id}-store.data",
            f"{self._chat_id}-hidden-messages.children",
            f"{self._chat_id}-chat-input.value",
            f"{self._chat_id}-sse.url",
            f"{self._chat_id}-sse.options",
            f"{self._chat_id}-file-store.data",
            f"{self._chat_id}-data-info.children",
        ]
