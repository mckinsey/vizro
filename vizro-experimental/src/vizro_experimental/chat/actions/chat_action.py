"""Non-streaming chat action for synchronous response generation."""

from __future__ import annotations

import json
from typing import Any

import plotly
from dash import Patch, html, no_update

from ..models.types import Message, _parse_store_messages
from ._base_chat_action import _BaseChatAction, _kwargs_for_generate_response


class ChatAction(_BaseChatAction):
    """Non-streaming chat action for synchronous response generation.

    Subclass this to create custom chat actions that return complete responses.

    Example:
        ```python
        class my_chat(ChatAction):
            def generate_response(self, messages):
                return "Hello from my chat!"
        ```

    """

    def generate_response(self, messages: list[Message], **kwargs: Any) -> str | html.Div:
        """Generate a chat response.

        Args:
            messages: Parsed history: each item has ``role`` and ``content`` (decoded from store ``content_json``).
            **kwargs: Optional ``uploaded_files`` or other kwargs only if your implementation accepts them.

        Returns:
            Response content as string or Dash component (will be JSON-serialized automatically).

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
        """Execute the chat action callback.

        Args:
            prompt: User's input text.
            messages: Store-shaped history (`role` + `content_json`); mutated in place when sending.
            uploaded_files: File-store payload from ``{chat_id}-file-store.data`` (always wired).

        Returns:
            List of outputs for store, hidden-messages, and chat-input.

        """
        if not prompt or not prompt.strip():
            return [no_update] * len(self.outputs)

        latest_input = {"role": "user", "content_json": json.dumps(prompt)}
        messages.append(latest_input)

        store = Patch()
        store.append(latest_input)

        gr_kw = _kwargs_for_generate_response(
            self.generate_response, uploaded_files=uploaded_files, payload_extras=None
        )
        result = self.generate_response(_parse_store_messages(messages), **gr_kw)
        # Serialize the result - handles both strings and Dash components
        content_json = json.dumps(result, cls=plotly.utils.PlotlyJSONEncoder)
        latest_output = {"role": "assistant", "content_json": content_json}
        store.append(latest_output)

        html_messages = [self.message_to_html(msg) for msg in messages]
        html_messages.append(self.message_to_html(latest_output))

        return [store, html_messages, no_update]

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
        ]
