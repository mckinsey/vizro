"""Floating chat popup for Vizro dashboards.

Provides `add_chat_popup()` to inject a chatbot-style floating widget at the dashboard level.
Call it after `app.build(dashboard)` and before `app.run()`.

Example usage::

    from vizro_experimental.chat.popup import add_chat_popup

    app = Vizro()
    app.build(dashboard)

    add_chat_popup(app, title="Analytics Assistant")
    app.run()

"""

from __future__ import annotations

import base64
import json
from collections.abc import Callable
from typing import Any, Literal

import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import plotly
from dash import ClientsideFunction, Input, Output, Patch, State, callback, clientside_callback, dcc, html
from dash.exceptions import PreventUpdate
from dash_extensions import SSE
from dash_extensions.streaming import sse_message, sse_options
from dash_iconify import DashIconify
from flask import Response, request

from .._constants import (
    BORDER_RADIUS,
    CSS_BUTTON_ROW,
    CSS_HISTORY_CONTAINER,
    CSS_HISTORY_SECTION,
    CSS_INPUT_INNER,
    CSS_INPUT_SECTION,
    CSS_LEFT_BUTTONS,
    CSS_ROOT,
    ICON_BUTTON_SIZE,
)
from ..actions._base_chat_action import (
    _kwargs_for_generate_response,
    _message_to_html,
    _register_loading_indicator_callback,
    _register_send_icon_toggle_callback,
)
from ..actions.streaming_chat_action import _StreamingRequest
from ..models.types import _parse_store_messages


def add_chat_popup(  # noqa: PLR0913
    app,
    generate_response: Callable | None = None,
    model=None,
    streaming: bool = True,
    chat_id: str = "chat_popup",
    placeholder: str = "How can I help you?",
    title: str = "Chat Assistant",
    color: str | None = None,
    reasoning_effort: Literal["low", "medium", "high"] = "medium",
) -> None:
    """Add a floating chat popup to a Vizro dashboard.

    Call this after ``app.build(dashboard)`` and before ``app.run()``.
    The popup appears as a floating button in the bottom-right corner.
    Clicking it opens a chat panel that works independently of dashboard pages.

    When called without *generate_response*, automatically creates a data-aware
    dashboard agent that discovers datasets from ``data_manager`` and answers
    questions using an LLM.

    Args:
        app: The Vizro app instance (after calling ``app.build(dashboard)``).
        generate_response: Optional function ``(messages, **kwargs) -> str | Iterator[str]``.
            *messages* is parsed history: each dict has ``role`` and ``content`` (decoded JSON).
            Return a string for non-streaming, or yield strings for streaming.
            When omitted, a built-in dashboard agent is created automatically.
        model: A LangChain chat model instance for the built-in dashboard agent
            (e.g. ``ChatOpenAI(model="gpt-5.4-mini-2026-03-17")``).
            Only used when *generate_response* is not provided.
            Defaults to ``ChatOpenAI(model="gpt-5.4-mini-2026-03-17",
            use_responses_api=True)``. Pass a pre-configured instance if you
            need non-default settings such as ``store=False`` for zero retention.
        streaming: Set ``True`` when *generate_response* yields chunks.
        chat_id: Unique DOM ID prefix. Change if you need multiple popups.
        placeholder: Placeholder text shown in the input field.
        title: Title displayed in the popup header bar.
        color: Color for the floating toggle button (any CSS color or Mantine color).
            Defaults to Mantine's primary color if not set.
        reasoning_effort: How hard the default gpt-5.4-mini model should reason
            before answering. One of ``"low"`` (fastest), ``"medium"`` (default,
            balanced), ``"high"`` (most thorough). Only used when both
            *generate_response* and *model* are ``None`` (i.e. the built-in
            dashboard agent is created with its default model). Pass ``"high"``
            for complex multi-hop or causal questions; drop to ``"low"`` for
            the snappiest interactive Q&A.

    """
    if generate_response is None:
        from .dashboard_agent import create_dashboard_agent, make_generate_response

        agent, _context = create_dashboard_agent(model=model, reasoning_effort=reasoning_effort)
        generate_response = make_generate_response(agent)

    chat_panel = _build_chat_panel(chat_id, placeholder, title, streaming)
    toggle_button = _build_toggle_button(chat_id, color=color)

    # Append to the MantineProvider's first child (dashboard-container)
    app.dash.layout.children[0].children.append(chat_panel)
    app.dash.layout.children[0].children.append(toggle_button)

    _setup_toggle_callback(chat_id)
    _setup_restore_callback(chat_id)
    _setup_clear_callback(chat_id)
    _setup_chat_ui_callbacks(chat_id)
    _register_loading_indicator_callback(chat_id)
    _register_send_icon_toggle_callback(chat_id)

    if streaming:
        _setup_streaming_callbacks(chat_id)
        _setup_streaming_endpoint(app, chat_id, generate_response)
        _setup_streaming_action(chat_id)
    else:
        _setup_non_streaming_action(chat_id, generate_response)


# ---------------------------------------------------------------------------
# Build helpers
# ---------------------------------------------------------------------------


def _build_toggle_button(chat_id: str, color: str | None = None) -> dmc.Affix:
    """Build the floating Affix toggle button."""
    icon_props: dict[str, Any] = {
        "id": f"{chat_id}-toggle-button",
        "variant": "filled",
        "size": "xl",
        "radius": "xl",
        "className": "chat-popup-toggle",
        "n_clicks": 0,
    }
    if color:
        icon_props["color"] = color

    return dmc.Affix(
        [
            dmc.ActionIcon(
                DashIconify(icon="material-symbols-light:chat-outline", width=28, height=28),
                **icon_props,
            ),
            dbc.Tooltip("Open chat assistant", target=f"{chat_id}-toggle-button", placement="left"),
        ],
        position={"bottom": 20, "right": 20},
        zIndex=300,
        id=f"{chat_id}-affix",
    )


def _build_chat_panel(chat_id: str, placeholder: str, title: str, streaming: bool) -> html.Div:
    """Build the popup chat panel."""
    header = dmc.Group(
        [
            dmc.Group(
                [
                    dmc.Text(title, fw=600, size="lg"),
                ],
                gap="xs",
            ),
            dmc.ActionIcon(
                DashIconify(icon="material-symbols-light:close", width=20, height=20),
                id=f"{chat_id}-close-button",
                variant="subtle",
                color="grey",
                n_clicks=0,
                radius="xl",
            ),
            dbc.Tooltip("Close chat", target=f"{chat_id}-close-button"),
        ],
        justify="space-between",
        className="chat-popup-header",
    )

    messages_area = html.Div(
        [
            html.Div(
                [
                    html.Div(id=f"{chat_id}-hidden-messages", children=[], style={"display": "none"}),
                    html.Div(id=f"{chat_id}-rendered-messages", className=CSS_HISTORY_CONTAINER),
                ],
            )
        ],
        className=CSS_HISTORY_SECTION,
    )

    input_area = html.Div(
        [
            html.Div(
                [
                    dmc.Textarea(
                        id=f"{chat_id}-chat-input",
                        placeholder=placeholder,
                        autosize=True,
                        size="md",
                        minRows=1,
                        maxRows=4,
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
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    dmc.ActionIcon(
                                        DashIconify(icon="material-symbols-light:delete-outline", width=24, height=24),
                                        id=f"{chat_id}-clear-button",
                                        variant="subtle",
                                        color="grey",
                                        n_clicks=0,
                                        radius=BORDER_RADIUS,
                                        style={"width": ICON_BUTTON_SIZE, "height": ICON_BUTTON_SIZE},
                                    ),
                                    dbc.Tooltip("Clear chat history", target=f"{chat_id}-clear-button"),
                                ],
                                className=CSS_LEFT_BUTTONS,
                            ),
                            dmc.ActionIcon(
                                DashIconify(
                                    icon="material-symbols-light:send-outline",
                                    width=32,
                                    height=32,
                                    id=f"{chat_id}-send-icon",
                                ),
                                id=f"{chat_id}-send-button",
                                variant="subtle",
                                color="grey",
                                n_clicks=0,
                                radius=BORDER_RADIUS,
                                style={"width": ICON_BUTTON_SIZE, "height": ICON_BUTTON_SIZE},
                            ),
                            dbc.Tooltip("Send message", target=f"{chat_id}-send-button"),
                        ],
                        className=CSS_BUTTON_ROW,
                    ),
                ],
                className=CSS_INPUT_INNER,
            ),
        ],
        className=CSS_INPUT_SECTION,
    )

    children = [
        header,
        html.Div([messages_area, input_area], className=CSS_ROOT),
        dcc.Store(id=f"{chat_id}-store", data=[], storage_type="session"),
        # Stubs: popup has no upload UI, but the loading-indicator callback (shared with the
        # Chat component) writes to these on send, so they must exist in the layout.
        dcc.Store(id=f"{chat_id}-file-store", data=[], storage_type="session"),
        html.Div(id=f"{chat_id}-data-info", style={"display": "none"}),
    ]

    if streaming:
        children.append(SSE(id=f"{chat_id}-sse", concat=True, animate_chunk=10, animate_delay=5))

    return html.Div(
        children,
        id=f"{chat_id}-panel",
        className="chat-popup-panel",
    )


# ---------------------------------------------------------------------------
# Callback helpers
# ---------------------------------------------------------------------------


def _setup_toggle_callback(chat_id: str) -> None:
    """Toggle popup open/close on button clicks."""
    clientside_callback(
        ClientsideFunction("vizroChatComponent", "togglePanel"),
        Output(f"{chat_id}-panel", "className"),
        Input(f"{chat_id}-toggle-button", "n_clicks"),
        State(f"{chat_id}-panel", "className"),
        prevent_initial_call=True,
    )
    clientside_callback(
        ClientsideFunction("vizroChatComponent", "closePanel"),
        Output(f"{chat_id}-panel", "className", allow_duplicate=True),
        Input(f"{chat_id}-close-button", "n_clicks"),
        prevent_initial_call=True,
    )


def _setup_restore_callback(chat_id: str) -> None:
    """Restore chat history from session store when the panel is opened."""

    @callback(
        Output(f"{chat_id}-hidden-messages", "children", allow_duplicate=True),
        Input(f"{chat_id}-panel", "className"),
        State(f"{chat_id}-store", "data"),
        prevent_initial_call=True,
    )
    def _restore_on_open(class_name, messages):
        if "chat-popup-panel-open" not in (class_name or ""):
            raise PreventUpdate
        if not messages:
            raise PreventUpdate
        return [_message_to_html(msg) for msg in messages]


def _setup_clear_callback(chat_id: str) -> None:
    """Clear chat history on clear button click."""
    clientside_callback(
        ClientsideFunction("vizroChatComponent", "clearChat"),
        [
            Output(f"{chat_id}-store", "data", allow_duplicate=True),
            Output(f"{chat_id}-hidden-messages", "children", allow_duplicate=True),
        ],
        Input(f"{chat_id}-clear-button", "n_clicks"),
        prevent_initial_call=True,
    )


def _setup_chat_ui_callbacks(chat_id: str) -> None:
    """Register clientside callbacks for markdown rendering and Enter key."""
    clientside_callback(
        ClientsideFunction("vizroChatComponent", "renderMessagesInPopup"),
        Output(f"{chat_id}-rendered-messages", "children"),
        Input(f"{chat_id}-hidden-messages", "children"),
        prevent_initial_call=True,
    )

    clientside_callback(
        ClientsideFunction("vizroChatComponent", "setupEnterKeyHandler"),
        Output(f"{chat_id}-chat-input", "id", allow_duplicate=True),
        Input(f"{chat_id}-chat-input", "value"),
        State(f"{chat_id}-chat-input", "id"),
        prevent_initial_call=True,
    )


def _setup_non_streaming_action(chat_id: str, generate_response: Callable) -> None:
    """Register the main action callback for non-streaming responses."""

    @callback(
        [
            Output(f"{chat_id}-store", "data"),
            Output(f"{chat_id}-hidden-messages", "children", allow_duplicate=True),
            Output(f"{chat_id}-chat-input", "value", allow_duplicate=True),
        ],
        Input(f"{chat_id}-send-button", "n_clicks"),
        [
            State(f"{chat_id}-chat-input", "value"),
            State(f"{chat_id}-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def _handle_send(n_clicks, prompt, messages):
        if not prompt or not prompt.strip():
            raise PreventUpdate

        latest_input = {"role": "user", "content_json": json.dumps(prompt)}
        messages.append(latest_input)

        store = Patch()
        store.append(latest_input)

        result = generate_response(_parse_store_messages(messages))
        content_json = json.dumps(result, cls=plotly.utils.PlotlyJSONEncoder)
        latest_output = {"role": "assistant", "content_json": content_json}
        store.append(latest_output)

        html_messages = [_message_to_html(msg) for msg in messages]
        html_messages.append(_message_to_html(latest_output))

        return [store, html_messages, ""]


def _setup_streaming_callbacks(chat_id: str) -> None:
    """Register clientside callback for SSE chunk processing."""
    clientside_callback(
        ClientsideFunction("vizroChatComponent", "processStreamingChunk"),
        [
            Output(f"{chat_id}-hidden-messages", "children", allow_duplicate=True),
            Output(f"{chat_id}-store", "data", allow_duplicate=True),
        ],
        Input(f"{chat_id}-sse", "animation"),
        [
            State(f"{chat_id}-hidden-messages", "children"),
            State(f"{chat_id}-store", "data"),
        ],
        prevent_initial_call=True,
    )


def _setup_streaming_endpoint(app, chat_id: str, generate_response: Callable) -> None:
    """Register Flask SSE streaming route."""
    CHUNK_DELIMITER = "|END|"
    base_pathname = app.dash.config.requests_pathname_prefix.rstrip("/")

    @app.dash.server.route(
        f"{base_pathname}/streaming-{chat_id}",
        methods=["POST"],
        endpoint=f"streaming_popup_{chat_id}",
    )
    def _streaming_chat():
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
            generate_response,
            uploaded_files=validated.uploaded_files,
            payload_extras=payload_extras,
        )

        def event_stream():
            for chunk in generate_response(_parse_store_messages(messages), **gr_kw):
                encoded = base64.b64encode(chunk.encode("utf-8")).decode("utf-8")
                yield sse_message(encoded + CHUNK_DELIMITER)
            yield sse_message()

        return Response(event_stream(), mimetype="text/event-stream")


def _setup_streaming_action(chat_id: str) -> None:
    """Register the main action callback for streaming responses."""

    @callback(
        [
            Output(f"{chat_id}-store", "data"),
            Output(f"{chat_id}-sse", "url"),
            Output(f"{chat_id}-sse", "options"),
        ],
        Input(f"{chat_id}-send-button", "n_clicks"),
        [
            State(f"{chat_id}-chat-input", "value"),
            State(f"{chat_id}-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def _handle_send_streaming(n_clicks, prompt, messages):
        if not prompt or not prompt.strip():
            raise PreventUpdate

        latest_input = {"role": "user", "content_json": json.dumps(prompt)}
        messages.append(latest_input)

        store = Patch()
        store.append(latest_input)
        store.append({"role": "assistant", "content_json": json.dumps("")})

        # hidden-messages / chat-input are owned by the loading-indicator callback;
        # processStreamingChunk swaps the loader for the assistant bubble on first chunk.
        sse_req = _StreamingRequest(prompt=prompt, messages=messages, uploaded_files=None)
        base_pathname = dash.get_app().config.requests_pathname_prefix.rstrip("/")

        return [
            store,
            f"{base_pathname}/streaming-{chat_id}",
            sse_options(sse_req),
        ]
