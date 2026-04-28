"""Shared base class and helpers for chat actions."""

from __future__ import annotations

import base64
import inspect
import json
from collections.abc import Callable
from pathlib import PurePosixPath
from typing import Any

import dash
import dash_mantine_components as dmc
from dash import ClientsideFunction, Input, Output, Patch, State, callback, clientside_callback, html, no_update
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from vizro.actions._abstract_action import _AbstractAction
from vizro.managers import model_manager
from vizro.models._models_utils import _log_call
from vizro.models.types import _IdOrIdProperty

from .._constants import (
    CSS_ASSISTANT_MESSAGE,
    CSS_FILE_CHIP,
    CSS_FILE_CHIP_REMOVE,
    CSS_FILE_CHIP_SUBTITLE,
    CSS_FILE_CHIP_TEXT,
    CSS_FILE_CHIP_THUMB,
    CSS_FILE_CHIP_THUMB_ICON,
    CSS_FILE_CHIP_TITLE,
    CSS_FILE_CHIP_UPLOADING,
    CSS_FILE_PREVIEW,
    CSS_LOADING_MESSAGE,
    CSS_MESSAGE_BUBBLE,
    CSS_MESSAGE_WRAPPER,
    CSS_USER_MESSAGE,
    CSS_USER_TEXT,
)

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
