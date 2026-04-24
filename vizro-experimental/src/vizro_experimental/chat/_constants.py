"""Vizro chat component with action-based architecture."""

from __future__ import annotations

import base64
import inspect
import json
from pathlib import PurePosixPath
from typing import Annotated, Any, Callable, Iterator, Literal, Union

import dash
import dash_mantine_components as dmc
import plotly
from dash import ClientsideFunction, Input, Output, Patch, State, callback, clientside_callback, dcc, html, no_update
from dash.exceptions import PreventUpdate
from dash_extensions import SSE
from dash_extensions.streaming import sse_message, sse_options
from dash_iconify import DashIconify
from flask import Response, request
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, model_validator

from vizro.actions._abstract_action import _AbstractAction
from vizro.managers import model_manager
from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call, make_actions_chain
from vizro.models.types import _IdOrIdProperty
from vizro_chat_component.messages import Message, _parse_store_messages

# -------------------- CSS Class Names --------------------
# These correspond to classes defined in static/css/chat.css
CSS_MESSAGE_BUBBLE = "chat-message-bubble"
CSS_USER_MESSAGE = "chat-user-message"
CSS_ASSISTANT_MESSAGE = "chat-assistant-message"
CSS_MESSAGE_WRAPPER = "chat-message-wrapper"
CSS_USER_TEXT = "chat-user-text"
CSS_ROOT = "chat-root"
CSS_HISTORY_SECTION = "chat-history-section"
CSS_HISTORY_CONTAINER = "chat-history-container"
CSS_INPUT_SECTION = "chat-input-section"
CSS_INPUT_INNER = "chat-input-inner"
CSS_LOADING_MESSAGE = "chat-loading-message"
CSS_FILE_PREVIEW = "chat-file-preview"
CSS_DATA_INFO = "chat-data-info"
CSS_BUTTON_ROW = "chat-button-row"
CSS_LEFT_BUTTONS = "chat-left-buttons"
CSS_EXAMPLE_QUESTION_ITEM = "chat-example-question-item"
CSS_EXAMPLE_MENU_DROPDOWN = "chat-example-menu-dropdown"
CSS_FILE_CHIP = "chat-file-chip"
CSS_FILE_CHIP_THUMB = "chat-file-chip-thumb"
CSS_FILE_CHIP_THUMB_ICON = "chat-file-chip-thumb-icon"
CSS_FILE_CHIP_TEXT = "chat-file-chip-text"
CSS_FILE_CHIP_TITLE = "chat-file-chip-title"
CSS_FILE_CHIP_SUBTITLE = "chat-file-chip-subtitle"
CSS_FILE_CHIP_REMOVE = "chat-file-chip-remove"
CSS_FILE_CHIP_UPLOADING = "chat-file-chip-uploading"

# Chat input controls: 36x36 hit target pairs with a 24px glyph (Vizro-core default size,
# see vizro-core figures.css). Smaller than 32 felt cramped next to the Figma reference.
ICON_BUTTON_SIZE = "36px"

_BYTES_PER_KB = 1024
_BYTES_PER_MB = 1024 * 1024


def _is_image_content(content: str) -> bool:
    return content.startswith("data:image/")


def _file_meta_label(filename: str, content: str) -> str:
    """Return a 'TYPE · SIZE' label, e.g. 'PDF · 1.28 MB'."""
    ext = PurePosixPath(filename).suffix.lstrip(".").upper()
    size = _format_size(_decoded_size(content))
    return " · ".join(part for part in (ext, size) if part)


def _decoded_size(content: str) -> int:
    if "," not in content:
        return 0
    try:
        return len(base64.b64decode(content.split(",", 1)[1], validate=False))
    except (ValueError, TypeError):
        return 0


def _format_size(n: int) -> str:
    if n <= 0:
        return ""
    if n < _BYTES_PER_KB:
        return f"{n} B"
    if n < _BYTES_PER_MB:
        return f"{n / _BYTES_PER_KB:.0f} KB"
    return f"{n / _BYTES_PER_MB:.2f} MB"


# Constants still needed for inline styles (e.g., Plotly graph sizing, buttons)
BORDER_RADIUS = "0px"
COLOR_TEXT_SECONDARY = "var(--text-secondary)"
PLOT_WIDTH = "600px"
PLOT_HEIGHT = "400px"


def _coerce_chat_actions(value: Any) -> Any:
    """Accept a single action or a list (empty omits validation pass-through for [])."""
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _kwargs_for_generate_response(
    generate_response_method: Callable[..., Any],
    *,
    uploaded_files: list[dict[str, Any]] | None,
    payload_extras: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build kwargs for ``generate_response`` so unsupported parameters are not passed."""
    sig = inspect.signature(generate_response_method)
    params = sig.parameters
    has_var_kw = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values())
    out: dict[str, Any] = {}
    if "uploaded_files" in params or has_var_kw:
        out["uploaded_files"] = uploaded_files
    if payload_extras:
        for key, value in payload_extras.items():
            if key == "uploaded_files":
                continue
            if key in params or has_var_kw:
                out[key] = value
    return out


def _loading_bubble() -> html.Div:
    """Dots-loader placeholder shown while an assistant reply is in flight."""
    return html.Div(
        html.Div(
            dmc.Loader(size="sm", type="dots"),
            className=f"{CSS_MESSAGE_BUBBLE} {CSS_ASSISTANT_MESSAGE} {CSS_LOADING_MESSAGE}",
        ),
        className=CSS_MESSAGE_WRAPPER,
    )


def _message_to_html(message: dict[str, str]) -> html.Div:
    """Convert a store message dict to the HTML structure expected by ``renderMessages``.

    Args:
        message: Dict with 'role' and 'content_json' keys.

    Returns:
        Dash HTML Div component representing the message.

    """
    role = message["role"]
    content = json.loads(message["content_json"])

    if role == "user":
        return html.Div(
            html.Div(
                html.Div(str(content) if content else "", className=CSS_USER_TEXT),
                className=f"{CSS_MESSAGE_BUBBLE} {CSS_USER_MESSAGE}",
            ),
            className=CSS_MESSAGE_WRAPPER,
        )
    elif isinstance(content, str):
        return html.Div(
            [
                html.Div("assistant", style={"display": "none"}),
                html.Div(content),
            ]
        )
    else:
        return html.Div(
            html.Div(content, className=f"{CSS_MESSAGE_BUBBLE} {CSS_ASSISTANT_MESSAGE}"),
            className=CSS_MESSAGE_WRAPPER,
        )


def _register_send_icon_toggle_callback(chat_id: str) -> None:
    """Swap the send glyph between outlined (empty input) and filled (has text).

    Mirrors the "active send" affordance used by ChatGPT / Claude / Gemini so the
    button reads as interactive the moment the user starts typing.
    """
    clientside_callback(
        """
        function(value) {
            const hasText = typeof value === 'string' && value.trim().length > 0;
            return hasText ? 'material-symbols-light:send' : 'material-symbols-light:send-outline';
        }
        """,
        Output(f"{chat_id}-send-icon", "icon"),
        Input(f"{chat_id}-chat-input", "value"),
    )


def _register_loading_indicator_callback(
    chat_id: str,
    message_to_html: Callable[[dict[str, str]], html.Div] = _message_to_html,
) -> None:
    """Register the send-click callback that appends the user bubble + loading dots.

    Shared by ``_BaseChatAction`` and ``add_chat_popup``. ``message_to_html`` is a hook
    so subclasses that override ``_BaseChatAction.message_to_html`` still take effect.
    """

    @callback(
        Output(f"{chat_id}-hidden-messages", "children", allow_duplicate=True),
        Output(f"{chat_id}-chat-input", "value", allow_duplicate=True),
        Input(f"{chat_id}-send-button", "n_clicks"),
        State(f"{chat_id}-chat-input", "value"),
        prevent_initial_call=True,
    )
    def _update_with_user_input(_, prompt):
        if not prompt or not prompt.strip():
            raise PreventUpdate
        html_messages = Patch()
        html_messages.append(message_to_html({"role": "user", "content_json": json.dumps(prompt)}))
        html_messages.append(_loading_bubble())
        return html_messages, ""


# -------------------- Base Classes --------------------


class _BaseChatAction(_AbstractAction):
    """Base class with shared chat functionality for Chat component actions.

    Chat DOM ids and Dash runtime bindings are derived from the parent ``Chat`` model
    (``self._parent_model.id``), set by Vizro when the action is listed in ``Chat.actions``.
    """

    @property
    def _chat_id(self) -> str:
        """Dash id prefix for this chat instance (same as parent ``Chat.id``)."""
        return self._parent_model.id

    @property
    def _runtime_args(self) -> dict[str, _IdOrIdProperty]:
        """Map built-in chat kwargs onto Dash state without extra Pydantic fields.

        Authors can list ``prompt`` and ``messages`` on ``function`` to receive those live UI
        values (when present in the signature). ``uploaded_files`` is always bound to the
        file store. Vizro's default ``_runtime_args`` only auto-fills from model ``Field``s
        that match the signature, so we inject the standard ``{chat_id}-…`` bindings here
        instead of requiring a field per wire-up.
        """
        merged = dict(super()._runtime_args)
        cid = self._chat_id
        params = self._parameters
        chat_defaults: dict[str, str] = {
            "prompt": f"{cid}-chat-input.value",
            "messages": f"{cid}-store.data",
        }
        for key, dotted in chat_defaults.items():
            if key in params and key not in merged:
                merged[key] = dotted
        # File store is always mounted in Chat layout; wire uploads for every callback.
        merged.setdefault("uploaded_files", f"{cid}-file-store.data")
        return merged

    @_log_call
    def pre_build(self):
        self._setup_chat_callbacks()
        _register_loading_indicator_callback(self._chat_id, message_to_html=self.message_to_html)
        _register_send_icon_toggle_callback(self._chat_id)
        self._setup_file_upload_callbacks()

    def _setup_chat_callbacks(self):
        """Set up generic chat UI callbacks."""
        # Parse markdown and render code blocks with syntax highlighting
        clientside_callback(
            ClientsideFunction("vizroChatComponent", "renderMessages"),
            Output(f"{self._chat_id}-rendered-messages", "children"),
            Input(f"{self._chat_id}-hidden-messages", "children"),
            prevent_initial_call=True,
        )

        # Handle Enter key for submission (allow Shift+Enter for new lines)
        clientside_callback(
            ClientsideFunction("vizroChatComponent", "setupEnterKeyHandler"),
            Output(f"{self._chat_id}-chat-input", "id", allow_duplicate=True),  # Dummy output
            Input(f"{self._chat_id}-chat-input", "value"),
            State(f"{self._chat_id}-chat-input", "id"),
            prevent_initial_call=True,
        )

        # Horrible hack to restore chat history when you change page and return.
        page = model_manager._get_model_page(self)

        @callback(
            [
                Output(f"{self._chat_id}-hidden-messages", "children", allow_duplicate=True),
                Output(
                    "vizro_version", "children", allow_duplicate=True
                ),  # Extremely horrible hack we should change, just done here to make
                # sure callback triggers (must have prevent_initial_call=True).
                Output(f"{self._chat_id}-data-info", "children", allow_duplicate=True),
            ],
            Input(*page._action_triggers["__default__"].split(".")),
            [
                State(f"{self._chat_id}-store", "data"),
                State(f"{self._chat_id}-file-store", "data"),
            ],
            prevent_initial_call=True,
        )
        def on_page_load(_, store, files):
            html_messages = [self.message_to_html(message) for message in store]
            file_preview = self._create_file_preview(files) if files else ""
            return html_messages, dash.no_update, file_preview

    def _setup_file_upload_callbacks(self):
        @callback(
            Output(f"{self._chat_id}-file-store", "data"),
            Output(f"{self._chat_id}-data-info", "children"),
            Input(f"{self._chat_id}-upload", "contents"),
            State(f"{self._chat_id}-upload", "filename"),
            State(f"{self._chat_id}-file-store", "data"),
            prevent_initial_call=True,
        )
        def process_upload(new_contents, new_filenames, existing_files):
            """Store uploaded files."""
            if new_contents is None:
                return no_update, no_update

            if not isinstance(new_contents, list):
                new_contents = [new_contents]
                new_filenames = [new_filenames]

            # Append new files to existing ones
            all_files = existing_files or []
            all_files.extend({"content": c, "filename": f} for c, f in zip(new_contents, new_filenames))

            return all_files, self._create_file_preview(all_files)

        @callback(
            Output(f"{self._chat_id}-file-store", "data", allow_duplicate=True),
            Output(f"{self._chat_id}-data-info", "children", allow_duplicate=True),
            Input({"type": f"{self._chat_id}-remove-file", "index": dash.ALL}, "n_clicks"),
            State(f"{self._chat_id}-file-store", "data"),
            prevent_initial_call=True,
        )
        def remove_file(n_clicks, files):
            """Remove a specific uploaded file by index."""
            if not n_clicks or not any(n_clicks):
                return no_update, no_update

            ctx = dash.callback_context
            if not ctx.triggered:
                return no_update, no_update

            # Get the index of the file to remove
            triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
            index = json.loads(triggered_id)["index"]

            # Remove the file at the specified index
            if files and 0 <= index < len(files):
                files = files[:index] + files[index + 1 :]
                if not files:
                    return [], ""
                return files, self._create_file_preview(files)

            return no_update, no_update

    def _create_file_preview(self, files: list[dict[str, Any]]) -> html.Div:
        """Create file preview UI component for multiple files.

        Args:
            files: List of file dicts with ``filename`` and ``content`` (base64 data URL).
                Each entry may also carry an optional ``status`` key ("ready" by default,
                or "uploading" to render the transient placeholder chip).

        Returns:
            Dash HTML Div containing one chip per file.

        """
        chips = [self._file_chip(f, i) for i, f in enumerate(files)]
        return html.Div(chips, className=CSS_FILE_PREVIEW)

    def _file_chip(self, file: dict[str, Any], index: int) -> html.Div:
        """Render a single file chip (thumbnail + two-line label + corner remove)."""
        status = file.get("status", "ready")
        filename = file.get("filename", "")
        content = file.get("content") or ""

        if status == "uploading":
            thumb = html.Div(dmc.Loader(size="sm"), className=f"{CSS_FILE_CHIP_THUMB} {CSS_FILE_CHIP_THUMB_ICON}")
            title, subtitle = "Uploading file…", "fetching name…"
            chip_class = f"{CSS_FILE_CHIP} {CSS_FILE_CHIP_UPLOADING}"
            remove_button: list[Any] = []
        else:
            if _is_image_content(content):
                thumb = html.Img(src=content, alt=filename, className=CSS_FILE_CHIP_THUMB)
            else:
                thumb = html.Div(
                    DashIconify(icon="material-symbols-light:description-outline", width=24, height=24),
                    className=f"{CSS_FILE_CHIP_THUMB} {CSS_FILE_CHIP_THUMB_ICON}",
                )
            title = filename
            subtitle = _file_meta_label(filename, content)
            chip_class = CSS_FILE_CHIP
            remove_button = [
                dmc.ActionIcon(
                    DashIconify(icon="material-symbols-light:close", width=12, height=12),
                    id={"type": f"{self._chat_id}-remove-file", "index": index},
                    n_clicks=0,
                    size="xs",
                    radius="xl",
                    className=CSS_FILE_CHIP_REMOVE,
                )
            ]

        return html.Div(
            [
                thumb,
                html.Div(
                    [
                        html.Div(title, className=CSS_FILE_CHIP_TITLE, title=title),
                        html.Div(subtitle, className=CSS_FILE_CHIP_SUBTITLE),
                    ],
                    className=CSS_FILE_CHIP_TEXT,
                ),
                *remove_button,
            ],
            className=chip_class,
        )

    def message_to_html(self, message: dict[str, str]) -> html.Div:
        """Convert a message dict to HTML structure.

        Override this method for custom rendering logic.

        Args:
            message: Dict with 'role' and 'content_json' keys.

        Returns:
            Dash HTML Div component representing the message.

        """
        return _message_to_html(message)


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

    def generate_response(self, messages: list[Message], **kwargs: Any) -> Union[str, html.Div]:
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


# -------------------- Chat Component --------------------


class Chat(VizroBaseModel):
    """Chat component for conversational AI interfaces.

    Args:
        type (Literal["chat"]): Defaults to `"chat"`.
        actions (list[_BaseChatAction] | _BaseChatAction): One action or a list of actions. Defaults to `[]`.
        placeholder (str): Placeholder text for the input field. Defaults to `"How can I help you?"`.
        file_upload (bool): Enable file upload functionality. Defaults to `False`.
        example_questions (list[str]): List of example questions to show in a popup menu. Defaults to `[]`.

    """

    type: Literal["chat"] = "chat"
    actions: Annotated[list[_BaseChatAction], BeforeValidator(_coerce_chat_actions)] = Field(
        default_factory=list,
        description="Chat action(s) to handle responses. Pass one action or a list.",
    )
    placeholder: str = Field(default="How can I help you?", description="Placeholder text for the input field.")
    file_upload: bool = Field(default=False, description="Enable file upload functionality.")
    example_questions: list[str] = Field(default=[], description="List of example questions to show in a popup menu.")

    _make_actions_chain = model_validator(mode="after")(make_actions_chain)

    @property
    def _action_triggers(self) -> dict[str, str]:
        """Define action triggers for the chat component.

        Returns:
            Dict mapping trigger names to component property references.

        """
        return {"__default__": f"{self.id}-send-button.n_clicks"}

    @_log_call
    def pre_build(self) -> None:
        """Set up callbacks for example questions during pre-build phase."""
        if self.example_questions:
            self._setup_example_questions_callback()

    def _setup_example_questions_callback(self) -> None:
        """Set up callback to fill chat input when example question is clicked."""
        # Store the questions list for use in the callback
        questions = self.example_questions

        @callback(
            Output(f"{self.id}-chat-input", "value", allow_duplicate=True),
            Input({"type": f"{self.id}-example-question", "index": dash.ALL}, "n_clicks"),
            prevent_initial_call=True,
        )
        def fill_example_question(n_clicks):
            """Fill chat input with the clicked example question."""
            if not n_clicks or not any(n_clicks):
                raise PreventUpdate

            ctx = dash.callback_context
            if not ctx.triggered:
                raise PreventUpdate

            # Get the index of the clicked question
            triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
            index = json.loads(triggered_id)["index"]

            if 0 <= index < len(questions):
                return questions[index]

            raise PreventUpdate

    def _build_upload_stores(self) -> list[dcc.Store]:
        """Build stores for file upload.

        Returns:
            List of dcc.Store components for file upload state.

        """
        return [dcc.Store(id=f"{self.id}-file-store", storage_type="session")]

    def _build_example_questions_menu(self) -> dmc.Menu:
        """Build the example questions popup menu.

        Returns:
            Dash Mantine Menu component with example questions.

        """
        menu_items = [
            dmc.MenuItem(
                question,
                id={"type": f"{self.id}-example-question", "index": i},
                className=CSS_EXAMPLE_QUESTION_ITEM,
            )
            for i, question in enumerate(self.example_questions)
        ]

        return dmc.Menu(
            [
                dmc.MenuTarget(
                    dmc.ActionIcon(
                        [
                            DashIconify(icon="material-symbols-light:chat-outline", width=24, height=24),
                            DashIconify(icon="material-symbols-light:keyboard-arrow-up", width=14, height=14),
                        ],
                        variant="subtle",
                        color="grey",
                        radius=BORDER_RADIUS,
                        style={"width": "48px", "height": ICON_BUTTON_SIZE},
                        id=f"{self.id}-example-questions-button",
                    )
                ),
                dmc.MenuDropdown(
                    menu_items,
                    className=CSS_EXAMPLE_MENU_DROPDOWN,
                ),
            ],
            position="top-start",
            shadow="md",
        )

    def _build_input_area(self) -> html.Div:
        """Build the input area with optional file upload button.

        Returns:
            Dash HTML Div containing the input area components.

        """
        # File upload button
        upload_button = dcc.Upload(
            id=f"{self.id}-upload",
            children=dmc.ActionIcon(
                DashIconify(icon="material-symbols-light:attach-file-add", width=24, height=24),
                variant="subtle",
                color="grey",
                radius=BORDER_RADIUS,
                style={"width": ICON_BUTTON_SIZE, "height": ICON_BUTTON_SIZE},
            ),
            style={"width": "fit-content", "display": "block" if self.file_upload else "none"},
            multiple=True,
        )

        # Example questions menu button
        example_questions_menu = (
            self._build_example_questions_menu() if self.example_questions else html.Div(style={"display": "none"})
        )

        # Build children list explicitly
        inner_children = []

        inner_children.append(html.Div(id=f"{self.id}-data-info", className=CSS_DATA_INFO))

        # Textarea - Mantine components need inline styles for internal styling
        inner_children.append(
            dmc.Textarea(
                id=f"{self.id}-chat-input",
                placeholder=self.placeholder,
                autosize=True,
                size="md",
                minRows=1,
                maxRows=6,
                radius=0,
                styles={
                    "input": {
                        "borderLeft": "none",
                        "borderRight": "none",
                        "borderTop": "none",
                        "borderRadius": "0",
                        "resize": "none",
                        "backgroundColor": "var(--bs-body-bg)",
                        "fontSize": "var(--chat-font-size)",
                        "lineHeight": "var(--chat-line-height)",
                        "color": "var(--text-primary)",
                    }
                },
                style={"width": "100%"},
                value="",
            )
        )

        # Left buttons group (file upload + example questions)
        left_buttons = html.Div(
            [upload_button, example_questions_menu],
            className=CSS_LEFT_BUTTONS,
        )

        # Button row
        inner_children.append(
            html.Div(
                [
                    left_buttons,
                    dmc.ActionIcon(
                        # Send glyph rendered at 32 (vs 24 on peers): the paper-plane only fills
                        # ~75% of its 24-unit viewBox, so equal px reads smaller.
                        DashIconify(
                            icon="material-symbols-light:send-outline",
                            width=32,
                            height=32,
                            id=f"{self.id}-send-icon",
                        ),
                        id=f"{self.id}-send-button",
                        variant="subtle",
                        color="grey",
                        n_clicks=0,
                        radius=BORDER_RADIUS,
                        style={"width": ICON_BUTTON_SIZE, "height": ICON_BUTTON_SIZE},
                    ),
                ],
                className=CSS_BUTTON_ROW,
            )
        )

        return html.Div(
            [
                html.Div(
                    inner_children,
                    className=CSS_INPUT_INNER,
                )
            ],
            className=CSS_INPUT_SECTION,
        )

    @_log_call
    def build(self) -> html.Div:
        """Build the chat component layout.

        Returns:
            Dash HTML Div containing the complete chat interface.

        """
        return html.Div(
            [
                *self._build_upload_stores(),
                # Messages container
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(id=f"{self.id}-hidden-messages", children=[], style={"display": "none"}),
                                html.Div(id=f"{self.id}-rendered-messages", className=CSS_HISTORY_CONTAINER),
                            ],
                            id=f"{self.id}-chat-messages-container",
                        )
                    ],
                    className=CSS_HISTORY_SECTION,
                ),
                # Input area
                self._build_input_area(),
                # Store for conversation history
                dcc.Store(id=f"{self.id}-store", data=[], storage_type="session"),
                # Server-Sent Events for streaming support
                SSE(id=f"{self.id}-sse", concat=True, animate_chunk=10, animate_delay=5),
            ],
            className=CSS_ROOT,
        )
