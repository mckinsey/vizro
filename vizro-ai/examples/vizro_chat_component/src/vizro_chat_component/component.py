"""Vizro chat component."""

import json
import time
import pathlib
from typing import Literal
import re

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, clientside_callback, dcc, html
from dash_extensions import SSE
from dash_extensions.streaming import sse_message, sse_options
from flask import Response, request
from pydantic import ConfigDict

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro_chat_component.processors import ChatProcessor, EchoProcessor

CHAT_CONTAINER_STYLE = {
    "width": "100%",
    "position": "relative",
}

CHAT_HISTORY_STYLE = {
    "width": "50%",
    "paddingBottom": "100px",
    "paddingLeft": "5px",
}

CHAT_INPUT_CONTAINER_STYLE = {
    "borderRadius": "10px",
    "height": "80px",
    "backgroundColor": "var(--surfaces-bg-card)",
    "zIndex": "1",
    "position": "fixed",
    "bottom": "20px",
    "width": "50%",
    "maxWidth": "760px",
}

SETTINGS_ICON_STYLE = {
    "cursor": "pointer",
    "position": "absolute",
    "bottom": "20px",
    "left": "20px",
    "zIndex": 1000,
    "color": "var(--text-secondary)",
}

SETTINGS_FEEDBACK_STYLE = {
    "marginLeft": "10px",
    "color": "var(--text-primary)",
}

SETTINGS_BUTTON_CONTAINER_STYLE = {
    "display": "flex",
    "alignItems": "center",
    "marginTop": "1rem",
}

TOGGLE_CONTAINER_STYLE = {
    "display": "flex",
    "alignItems": "center",
    "paddingLeft": "10px",
    "minWidth": "50px",
}

MESSAGE_STYLE = {
    "color": "var(--text-primary)",
    "padding": "10px 15px",
    "maxWidth": "96%",
    "marginLeft": "0",
    "marginRight": "auto",
    "marginBottom": "15px",
    "whiteSpace": "pre-wrap",
    "wordBreak": "break-word",
    "width": "fit-content",
    "minWidth": "100px",
    "lineHeight": "1.5",
    "letterSpacing": "0.2px",
    "borderRadius": "10px",
}

TEXTAREA_STYLE = {
    "height": "80px",  # This will be overridden by self.input_height
    "resize": "none",
    "borderBottomLeftRadius": "10px",
    "borderTopLeftRadius": "10px",
    "boxShadow": "none",  # Remove box-shadow
    "border": "1px solid var(--border-subtleAlpha01)",  # Optional: add subtle border
}

# Helper to split concatenated JSON objects and return complete objects and incomplete tail

def split_json_objects(s):
    s = s.replace('}{', '}\n{')
    lines = [line for line in s.splitlines() if line.strip()]
    complete = []
    incomplete = ""
    for line in lines:
        try:
            obj = json.loads(line)
            complete.append(obj)
        except Exception:
            incomplete = line  # Save the last incomplete line
            break
    return complete, incomplete

def render_message(message, idx):
    msg_type = message.get("type")
    content = message.get("content", "")
    block_id = idx
    interval = 20  # ms per tick, adjust for speed
    chars_per_tick = 2
    max_intervals = len(content) // chars_per_tick + 2
    key = f"block-{block_id}-{hash(content)}"  # Unique and stable for each block/content

    if msg_type == "code":
        # Use Markdown for code blocks
        code_content = f"```{content}\n```"
        code_container_id = f"block-visible-{block_id}"
        return html.Div([
            dcc.Store(id=f"block-full-{block_id}", data=code_content),
            dcc.Interval(id=f"block-interval-{block_id}", interval=interval, n_intervals=0, max_intervals=max_intervals),
            html.Div([
                dcc.Markdown(id=code_container_id, style={"background": "var(--surfaces-bg-card)", "padding": "10px", "margin": 0}),
                dcc.Clipboard(
                    target_id=code_container_id,
                    title="Copy code",
                    style={
                        "position": "absolute",
                        "top": 5,
                        "right": 5,
                        "fontSize": 18,
                        # "zIndex": 10,
                        # "background": "var(--surfaces-bg-card)",
                        # "borderRadius": "5px",
                        # "boxShadow": "0 1px 4px rgba(0,0,0,0.08)",
                        "padding": "2px 4px"
                    },
                ),
            ], style={"position": "relative"}),
            html.Br()
        ], key=key)
    else:
        # Default: use Markdown for everything else
        return html.Div([
            dcc.Store(id=f"block-full-{block_id}", data=content),
            dcc.Interval(id=f"block-interval-{block_id}", interval=interval, n_intervals=0, max_intervals=max_intervals),
            dcc.Markdown(id=f"block-visible-{block_id}")
        ], key=key)

class VizroChatComponent(VizroBaseModel):
    """A chat component for Vizro dashboards.

    This component provides interactive chat functionality that can be
    integrated into Vizro dashboards. It supports different processors
    for handling chat responses, including simple echoing and OpenAI integration.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    type: Literal["vizro_chat_component"] = "vizro_chat_component"
    id: str
    input_placeholder: str = "Ask me a question..."
    input_height: str = "80px"
    button_text: str = "Send"
    initial_message: str = "Hello! How can I help you today?"
    processor: ChatProcessor = EchoProcessor()  # Default to echo processor
    show_settings: bool = True  # Parameter to control settings visibility

    @property
    def messages(self) -> list[dict[str, str]]:
        """Get initial messages list."""
        return []

    @_log_call
    def pre_build(self):
        """Register routes and callbacks before building the component."""
        self._register_streaming_route()
        self._register_settings_callbacks()
        self._register_streaming_callback()

    def _register_streaming_route(self):
        """Register the streaming endpoint for the chat component."""

        @dash.get_app().server.route(f"/streaming-{self.id}", methods=["POST"], endpoint=f"streaming_chat_{self.id}")
        def streaming_chat():
            try:
                data = request.json
                if not data:
                    raise ValueError("No data received")

                user_prompt = data.get("prompt", "").strip()
                if not user_prompt:
                    raise ValueError("Empty prompt")

                messages = json.loads(data.get("chat_history", "[]"))

                # Get API settings if available
                api_settings = data.get("api_settings") or {}
                if api_settings and hasattr(self.processor, "initialize_client"):
                    api_key = api_settings.get("api_key")
                    api_base = api_settings.get("api_base")
                    if api_key:  # Only initialize if we have an API key
                        self.processor.initialize_client(api_key=api_key, api_base=api_base)

                def response_stream():
                    try:
                        for chunk in self.processor.get_response(messages, user_prompt):
                            # time.sleep(0.1)
                            print(sse_message(chunk))
                            yield sse_message(chunk)
                        yield sse_message()  # Final empty message to signal completion
                    except Exception as e:
                        yield sse_message(f"Error: {e!s}")

                return Response(response_stream(), mimetype="text/event-stream")
            except Exception as e:
                return Response(f"Error: {e!s}", status=500)

    def _register_settings_callbacks(self):
        """Register callbacks for managing API settings."""

        @callback(
            Output(f"{self.id}-settings", "is_open"),
            Input(f"{self.id}-settings-icon", "n_clicks"),
            [State(f"{self.id}-settings", "is_open")],
        )
        def toggle_settings(n_clicks, is_open):
            """Callback for opening and closing offcanvas settings component."""
            return not is_open if n_clicks else is_open

        @callback(
            Output(f"{self.id}-api-key", "type"),
            Input(f"{self.id}-api-key-toggle", "value"),
        )
        def show_api_key(value):
            """Callback to show or hide API key."""
            return "text" if value else "password"

        @callback(
            Output(f"{self.id}-api-base", "type"),
            Input(f"{self.id}-api-base-toggle", "value"),
        )
        def show_api_base(value):
            """Callback to show or hide API base URL."""
            return "text" if value else "password"

        @callback(
            [
                Output(f"{self.id}-api-settings", "data"),
                Output(f"{self.id}-settings-feedback", "children"),
            ],
            Input(f"{self.id}-save-settings", "n_clicks"),
            [
                State(f"{self.id}-api-key", "value"),
                State(f"{self.id}-api-base", "value"),
            ],
        )
        def save_settings(n_clicks, api_key, api_base):
            """Save API settings and provide user feedback."""
            if n_clicks is None:
                return dash.no_update, dash.no_update

            # Check if API key is provided
            if not api_key or not api_key.strip():
                return {"api_key": "", "api_base": api_base}, "No API Key provided."

            return {"api_key": api_key, "api_base": api_base}, "API Key added."

        @callback(
            [
                Output(f"{self.id}-api-key", "value"),
                Output(f"{self.id}-api-base", "value"),
            ],
            Input(f"{self.id}-settings", "is_open"),
            State(f"{self.id}-api-settings", "data"),
        )
        def load_settings(is_open, saved_settings):
            """Load saved settings into inputs when OffCanvas is opened."""
            if not is_open or not saved_settings:
                return "", ""
            return saved_settings.get("api_key", ""), saved_settings.get("api_base", "")

    def _register_streaming_callback(self):
        """Register callbacks for chat functionality."""

        # Add callback to clear input immediately on submit
        @callback(
            Output(f"{self.id}-input", "value"),
            [
                Input(f"{self.id}-submit", "n_clicks"),
                Input(f"{self.id}-input", "n_submit"),
            ],
            State(f"{self.id}-input", "value"),
            prevent_initial_call=True,
        )
        def clear_input(n_clicks, n_submit, value):
            """Clear input field immediately when user submits."""
            if (n_clicks or n_submit) and value and value.strip():
                return ""
            return dash.no_update

        # Add callback to initialize messages if empty
        @callback(
            Output(f"{self.id}-messages", "data"),
            Input(f"{self.id}-messages", "data"),
        )
        def initialize_messages(current_messages):
            """Initialize messages if they don't exist."""
            if not current_messages:
                return json.dumps([{"role": "assistant", "content": self.initial_message}])
            return current_messages

        # Add callback to handle SSE URL and options
        @callback(
            Output(f"{self.id}-sse", "url"),
            Output(f"{self.id}-sse", "options"),
            Output(f"{self.id}-history", "children"),
            Output(f"{self.id}-messages", "data", allow_duplicate=True),
            Input(f"{self.id}-submit", "n_clicks"),
            Input(f"{self.id}-input", "n_submit"),
            State(f"{self.id}-input", "value"),
            State(f"{self.id}-messages", "data"),
            State(f"{self.id}-api-settings", "data"),
            State(f"{self.id}-history", "children"),
            prevent_initial_call=True,
        )
        def start_streaming(n_clicks, n_submit, value, messages, api_settings, current_history):
            if (not n_clicks and not n_submit) or not value or not value.strip():
                return dash.no_update, dash.no_update, dash.no_update, dash.no_update

            messages_array = json.loads(messages)
            user_message = {"role": "user", "content": value.strip()}
            messages_array.append(user_message)

            # Create user message div
            user_div = html.Div(
                value.strip(),
                style={
                    **MESSAGE_STYLE,
                    "backgroundColor": "var(--surfaces-bg-card)",
                    "borderLeft": "4px solid #aaa9ba",
                }
            )

            # Create assistant div for streaming (remove spinner)
            assistant_div = html.Div(
                [],  # Empty initially, will be filled by streaming content
                style={
                    **MESSAGE_STYLE,
                    "backgroundColor": "var(--right-side-bg)",
                    "borderLeft": "4px solid #00b4ff",
                }
            )

            # Update history with both divs
            new_history = current_history or []
            new_history = new_history + [user_div, assistant_div]

            return (
                f"/streaming-{self.id}",
                sse_options(
                    json.dumps({
                        "prompt": value.strip(),
                        "chat_history": json.dumps(messages_array),
                        "api_settings": api_settings
                    }),
                    headers={"Content-Type": "application/json"},
                    method="POST"
                ),
                new_history,
                json.dumps(messages_array)
            )

        # Register clientside callbacks for up to 20 blocks using string IDs
        for i in range(50):
            clientside_callback(
                """
                function(n_intervals, full_content) {
                    if (!full_content) return '';
                    var charsPerTick = 2;
                    var charsToShow = Math.min(full_content.length, n_intervals * charsPerTick);
                    return full_content.slice(0, charsToShow);
                }
                """,
                Output(f'block-visible-{i}', 'children'),
                Input(f'block-interval-{i}', 'n_intervals'),
                State(f'block-full-{i}', 'data')
            )

        @callback(
            Output(f"{self.id}-streaming-content", "children"),
            Output(f"{self.id}-history", "children", allow_duplicate=True),
            Input(f"{self.id}-sse", "animation"),
            State(f"{self.id}-history", "children"),
            State(f"{self.id}-streaming-content", "children"),
            prevent_initial_call=True,
        )
        def update_streaming_content(animation, current_history, prev_content):
            if not animation:
                return dash.no_update, dash.no_update

            messages = []
            try:
                if isinstance(animation, list):
                    messages = [json.loads(msg) for msg in animation]
                elif isinstance(animation, str):
                    complete, _ = split_json_objects(animation)
                    messages = complete
                else:
                    messages = [json.loads(animation)]
            except Exception as e:
                content = prev_content if prev_content is not None else html.Div(animation)
                if current_history and len(current_history) > 0:
                    current_history[-1]["props"]["children"] = content
                    return content, current_history
                return content, dash.no_update

            # Get the already rendered blocks (if any)
            already_rendered = []
            if current_history and len(current_history) > 0:
                already_rendered = current_history[-1]["props"].get("children", [])
                if not isinstance(already_rendered, list):
                    already_rendered = [already_rendered]

            # Only render new blocks
            new_blocks = [render_message(msg, idx) for idx, msg in enumerate(messages[len(already_rendered):], start=len(already_rendered))]
            content = already_rendered + new_blocks

            if current_history and len(current_history) > 0:
                current_history[-1]["props"]["children"] = content
                return content, current_history
            return content, dash.no_update

        # Add callback to update messages store after streaming completes
        @callback(
            Output(f"{self.id}-messages", "data", allow_duplicate=True),
            Input(f"{self.id}-sse", "completed"),
            State(f"{self.id}-streaming-content", "children"),
            State(f"{self.id}-messages", "data"),
            prevent_initial_call="initial_duplicate",
        )
        def update_messages_store(completed, content, messages):
            if not completed or not content:
                return dash.no_update

            messages_array = json.loads(messages)
            assistant_message = {"role": "assistant", "content": content}
            messages_array.append(assistant_message)
            return json.dumps(messages_array)

    @_log_call
    def build(self):
        """Build the chat component layout."""
        components = []
        components.extend(self._build_data_stores())
        components.append(self._build_settings_icon())
        components.append(self._build_settings_offcanvas())
        components.append(self._build_chat_interface())
        components.append(SSE(id=f"{self.id}-sse", concat=True, animate_chunk=5, animate_delay=10))
        
        return html.Div(
            components,
            style=CHAT_CONTAINER_STYLE,
        )

    def _build_data_stores(self):
        """Build the data store components for the chat."""
        return [
            dcc.Store(id=f"{self.id}-api-settings", storage_type="session"),
            dcc.Store(id=f"{self.id}-messages", storage_type="session"),
        ]

    def _build_settings_icon(self):
        """Build the settings icon component."""
        if not self.show_settings:
            return html.Div()

        return html.Div(
            children=[
                html.Span(
                    "vpn_key",
                    className="material-symbols-outlined",
                    id=f"{self.id}-settings-icon",
                    style=SETTINGS_ICON_STYLE,
                ),
            ],
        )

    def _build_settings_offcanvas(self):
        """Build the settings offcanvas component."""
        return dbc.Offcanvas(
            id=f"{self.id}-settings",
            title="Chat Settings",
            children=[
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("API Key"),
                        dbc.Input(
                            placeholder="API key",
                            type="password",
                            id=f"{self.id}-api-key",
                        ),
                        html.Div(
                            dbc.Checklist(
                                id=f"{self.id}-api-key-toggle",
                                options=[{"label": "", "value": 1}],
                                value=[],
                                switch=True,
                                inline=True,
                            ),
                            style=TOGGLE_CONTAINER_STYLE,
                        ),
                    ],
                    className="mb-3",
                ),
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("API base"),
                        dbc.Input(
                            placeholder="(optional) API Base",
                            type="password",
                            id=f"{self.id}-api-base",
                        ),
                        html.Div(
                            dbc.Checklist(
                                id=f"{self.id}-api-base-toggle",
                                options=[{"label": "", "value": 1}],
                                value=[],
                                switch=True,
                                inline=True,
                            ),
                            style=TOGGLE_CONTAINER_STYLE,
                        ),
                    ],
                    className="mb-3",
                ),
                html.Div(
                    [
                        dbc.Button(
                            "Save Settings",
                            id=f"{self.id}-save-settings",
                            color="primary",
                        ),
                        html.Div(
                            id=f"{self.id}-settings-feedback",
                            style=SETTINGS_FEEDBACK_STYLE,
                        ),
                    ],
                    style=SETTINGS_BUTTON_CONTAINER_STYLE,
                ),
            ],
            is_open=False,
        )

    def _build_chat_interface(self):
        """Build the main chat interface."""
        return html.Div(
            [
                html.Div(
                    html.Div(
                        id=f"{self.id}-history",
                        style=CHAT_HISTORY_STYLE,
                    ),
                    style={
                        "display": "flex",
                        "justifyContent": "center",
                        "width": "100%",
                    },
                ),
                # Hidden div for streaming content
                html.Div(id=f"{self.id}-streaming-content", style={"display": "none"}),
                html.Div(
                    dbc.InputGroup(
                        [
                            dbc.Textarea(
                                id=f"{self.id}-input",
                                placeholder=self.input_placeholder,
                                autoFocus=True,
                                style={
                                    **TEXTAREA_STYLE,
                                    "height": self.input_height,
                                },
                                n_submit=0,
                                className="no-focus-shadow",
                            ),
                            dbc.Button(
                                self.button_text,
                                outline=True,
                                color="secondary",
                                id=f"{self.id}-submit",
                                style={
                                    "height": self.input_height,
                                    "borderBottomRightRadius": "10px",
                                    "borderTopRightRadius": "10px",
                                },
                            ),
                        ],
                        style=CHAT_INPUT_CONTAINER_STYLE,
                    ),
                    style={
                        "display": "flex",
                        "justifyContent": "center",
                        "width": "100%",
                    },
                ),
            ],
            style=CHAT_CONTAINER_STYLE,
        )
