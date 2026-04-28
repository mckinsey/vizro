"""Streaming chat action that pushes response chunks over SSE."""

from __future__ import annotations

import base64
import json
from collections.abc import Iterator
from typing import Any

import dash
from dash import ClientsideFunction, Input, Output, Patch, State, clientside_callback, no_update
from dash_extensions.streaming import sse_message, sse_options
from flask import Response, request
from pydantic import BaseModel, ConfigDict, Field
from vizro.models._models_utils import _log_call

from ..models.types import Message, _parse_store_messages
from ._base_chat_action import _BaseChatAction, _kwargs_for_generate_response


class _StreamingRequest(BaseModel):
    """Request payload for streaming chat endpoint.

    Args:
        prompt (str): The user's input prompt.
        messages (list[dict[str, Any]]): Store-shaped history: each dict has ``role`` and ``content_json``.
            Implementations of :meth:`StreamingChatAction.generate_response` receive parsed messages only
            (``role`` + ``content``), decoded from this wire format inside the framework.

    """

    model_config = ConfigDict(extra="allow")

    prompt: str = Field(description="The user's input prompt.")
    messages: list[dict[str, Any]] = Field(
        description="Store-shaped message dicts with 'role' and 'content_json' keys (wire format)."
    )
    uploaded_files: list[dict[str, Any]] | None = Field(
        default=None,
        description="Optional file-store payload from the chat upload (same shape as dcc.Store data).",
    )


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

    def _setup_streaming_callbacks(self) -> None:
        """SSE streaming decoding and accumulation."""
        clientside_callback(
            ClientsideFunction("vizroChatComponent", "processStreamingChunk"),
            [
                Output(f"{self._chat_id}-hidden-messages", "children", allow_duplicate=True),
                Output(f"{self._chat_id}-store", "data", allow_duplicate=True),
            ],
            Input(f"{self._chat_id}-sse", "animation"),
            [State(f"{self._chat_id}-hidden-messages", "children"), State(f"{self._chat_id}-store", "data")],
            prevent_initial_call=True,
        )

    @_log_call
    def pre_build(self) -> None:
        """Set up streaming callbacks and endpoint during pre-build phase."""
        super().pre_build()
        self._setup_streaming_callbacks()
        self._setup_streaming_endpoint()

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

    def _setup_streaming_endpoint(self) -> None:
        """Set up streaming endpoint for SSE."""
        CHUNK_DELIMITER = "|END|"
        # Get the base pathname to support deployments with URL prefixes
        base_pathname = dash.get_app().config.requests_pathname_prefix.rstrip("/")

        @dash.get_app().server.route(
            f"{base_pathname}/streaming-{self._chat_id}", methods=["POST"], endpoint=f"streaming_chat_{self._chat_id}"
        )
        def streaming_chat():
            data = request.get_json()
            # Validate the request payload through Pydantic to ensure required fields
            # (messages, prompt) are present and correctly typed. This prevents malformed
            # requests from reaching generate_response and mitigates mass parameter
            # assignment — only fields that pass _StreamingRequest validation are forwarded.
            try:
                validated = _StreamingRequest(**data)
            except Exception:
                return Response("Invalid request", status=400)
            messages = validated.messages
            payload_extras = validated.model_extra or {}
            gr_kw = _kwargs_for_generate_response(
                self.generate_response,
                uploaded_files=validated.uploaded_files,
                payload_extras=payload_extras,
            )

            def event_stream():
                for chunk in self.generate_response(_parse_store_messages(messages), **gr_kw):
                    # Encode chunk as base64 to handle any special characters
                    encoded_chunk = base64.b64encode(chunk.encode("utf-8")).decode("utf-8")
                    # Need a robust delimiter for clientside parsing
                    yield sse_message(encoded_chunk + CHUNK_DELIMITER)

                # Send SSE completion signal
                yield sse_message()

            return Response(event_stream(), mimetype="text/event-stream")

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
            uploaded_files: Data from ``{chat_id}-file-store.data`` (included in the SSE POST body when set).

        Returns:
            List of outputs for store, hidden-messages, chat-input, SSE url, and SSE options.

        """
        if not prompt or not prompt.strip():
            return [no_update] * len(self.outputs)

        latest_input = {"role": "user", "content_json": json.dumps(prompt)}
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
        ]
