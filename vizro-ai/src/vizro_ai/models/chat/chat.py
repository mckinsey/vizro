"""Chat model."""

import json
from typing import Literal, Optional, Union

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, clientside_callback, dcc, html
from dash_extensions import SSE
from dash_extensions.streaming import sse_message, sse_options
from flask import Response, request
from pydantic import ConfigDict, Field, field_validator
from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models.types import CapturedCallable, validate_captured_callable

from vizro_ai.models.chat._constants import (
    HISTORY_CONTAINER,
    HISTORY_SECTION,
    INPUT_FIELD,
    INPUT_GROUP,
    INPUT_SECTION,
    MAIN_CONTAINER,
    MESSAGE_BUBBLE,
    ROOT_CONTAINER,
)
from vizro_ai.models.chat._utils import (
    _create_message_components,
    _flush_accumulated_text,
    _parse_sse_chunks,
)
from vizro_ai.processors import ChatMessage, ChatProcessor, EchoProcessor


class Chat(VizroBaseModel):
    """Chat component for interactive conversations with AI assistance.

    Args:
        type (Literal["chat"]): Defaults to `"chat"`.
        input_placeholder (str): Placeholder text for the input field. Defaults to `"Ask me a question..."`.
        input_height (str): Height of the input field. Defaults to `"80px"`.
        button_text (str): Text displayed on the send button. Defaults to `"Send"`.
        initial_message (Optional[str]): Initial message displayed in the chat. Defaults to `None`.
        height (str): Height of the chat component wrapper. Defaults to `"100%"`.
        storage_type (Literal["memory", "session", "local"]): Storage type for chat history
            persistence. Defaults to `"session"`.
        processor (Union[ChatProcessor, CapturedCallable]): Chat processor for generating responses.
            Can be a ChatProcessor instance or a captured callable that returns a ChatProcessor.
            Defaults to `EchoProcessor()`.

    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    type: Literal["chat"] = "chat"
    input_placeholder: str = Field(default="Ask me a question...", description="Placeholder text for the input field")
    input_height: str = Field(default="80px", description="Height of the input field")
    button_text: str = Field(default="Send", description="Text displayed on the send button")
    initial_message: Optional[str] = Field(default=None, description="Initial message displayed in the chat")
    height: str = Field(default="100%", description="Height of the chat component wrapper")
    storage_type: Literal["memory", "session", "local"] = Field(
        default="session", description="Storage type for chat history persistence"
    )

    processor: Union[ChatProcessor, CapturedCallable] = Field(
        default_factory=EchoProcessor,
        json_schema_extra={"mode": "processor", "import_path": "vizro_ai.processors"},
        description="Chat processor for generating responses. Can be a ChatProcessor instance or captured callable that returns a ChatProcessor.",
    )

    _validate_processor = field_validator("processor", mode="before")(validate_captured_callable)

    def plug(self, app):
        """Register streaming routes with the Dash app.

        Args:
            app: The Dash application instance.
        """

        @app.server.route(f"/streaming-{self.id}", methods=["POST"], endpoint=f"streaming_chat_{self.id}")
        def streaming_chat():
            try:
                data = request.json or {}
                user_prompt = data.get("prompt", "").strip()
                messages = json.loads(data.get("chat_history", "[]"))

                def response_stream():
                    try:
                        processor_instance = (
                            self.processor() if isinstance(self.processor, CapturedCallable) else self.processor
                        )
                        for chat_message in processor_instance.get_response(messages, user_prompt):
                            yield sse_message(chat_message.to_json())
                        # Send standard SSE completion signal
                        # https://github.com/emilhe/dash-extensions/blob/78d1de50d32f888e5f287cfedfa536fe314ab0b4/dash_extensions/streaming.py#L6
                        yield sse_message("[DONE]")
                    except Exception:
                        import logging

                        logging.error("An error occurred in response_stream:", exc_info=True)
                        error_msg = ChatMessage(type="error", content="An internal error has occurred.")
                        yield sse_message(error_msg.to_json())
                        yield sse_message("[DONE]")

                # Use Response with SSE content type
                response = Response(response_stream(), mimetype="text/event-stream")
                return response
            except Exception:
                import logging

                logging.error("An error occurred in streaming_chat:", exc_info=True)
                return Response("An internal error has occurred.", status=500)

    @_log_call
    def pre_build(self):
        """Register callbacks before building the component."""
        self._register_streaming_callback()

    def _register_streaming_callback(self):  # noqa: PLR0915
        """Register callbacks for chat functionality and user interactions."""

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
                if not self.initial_message:
                    return json.dumps([])
                initial_content = [{"type": "text", "content": self.initial_message}]
                initial_data = json.dumps([{"role": "assistant", "content": initial_content}])
                return initial_data
            return current_messages

        @callback(
            Output(f"{self.id}-history", "children", allow_duplicate=True),
            Input(f"{self.id}-messages", "data"),
            State(f"{self.id}-history", "children"),
            prevent_initial_call="initial_duplicate",
        )
        def rebuild_history_from_storage(messages_data, current_history):
            """Rebuild the visual chat history from stored messages on initial load only."""
            # Only rebuild if history is empty (initial load)
            if current_history:
                return dash.no_update

            if not messages_data:
                return []

            try:
                messages = json.loads(messages_data)
                history_divs = []

                for idx, message in enumerate(messages):
                    role = message.get("role", "")
                    content = message.get("content", "")

                    if role == "user":
                        div = html.Div(
                            content,
                            style={
                                **MESSAGE_BUBBLE,
                                "backgroundColor": "var(--surfaces-bg-card)",
                                "borderLeft": "4px solid #aaa9ba",
                            },
                        )
                    elif role == "assistant":
                        # Skip empty assistant messages (placeholders)
                        if not content:
                            continue
                        # Create assistant message div with parsed components
                        message_id = f"{self.id}-history-msg-{idx}"
                        div = html.Div(
                            _create_message_components(content, message_id),
                            style={
                                **MESSAGE_BUBBLE,
                                "backgroundColor": "var(--right-side-bg)",
                                "borderLeft": "4px solid #00b4ff",
                            },
                        )
                    else:
                        continue

                    history_divs.append(div)

                return history_divs
            except (json.JSONDecodeError, TypeError):
                return []

        @callback(
            Output(f"{self.id}-sse", "url"),
            Output(f"{self.id}-sse", "options"),
            Output(f"{self.id}-history", "children"),
            Output(f"{self.id}-messages", "data", allow_duplicate=True),
            Output(f"{self.id}-stream-buffer", "data", allow_duplicate=True),
            Output(f"{self.id}-completion-trigger", "data", allow_duplicate=True),
            Input(f"{self.id}-submit", "n_clicks"),
            Input(f"{self.id}-input", "n_submit"),
            State(f"{self.id}-input", "value"),
            State(f"{self.id}-messages", "data"),
            State(f"{self.id}-history", "children"),
            prevent_initial_call=True,
        )
        def start_streaming(n_clicks, n_submit, value, messages, current_history):
            """Start streaming when user submits a message."""
            if (not n_clicks and not n_submit) or not value or not value.strip():
                return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

            messages_array = json.loads(messages)
            user_message = {"role": "user", "content": value.strip()}
            messages_array.append(user_message)

            # Add placeholder assistant message immediately to ensure persistence
            assistant_placeholder = {"role": "assistant", "content": ""}
            messages_array.append(assistant_placeholder)

            updated_messages = json.dumps(messages_array)

            user_div = html.Div(
                value.strip(),
                style={
                    **MESSAGE_BUBBLE,
                    "backgroundColor": "var(--surfaces-bg-card)",
                    "borderLeft": "4px solid #aaa9ba",
                },
            )

            assistant_div = html.Div(
                id=f"{self.id}-streaming-content",
                children=html.Div(
                    id=f"{self.id}-streaming-components",
                    children=[],  # Will hold mixed content: streaming text and code blocks
                ),
                style={
                    **MESSAGE_BUBBLE,
                    "backgroundColor": "var(--right-side-bg)",
                    "borderLeft": "4px solid #00b4ff",
                },
            )

            # Update history with both divs (append to existing history)
            new_history = current_history or []
            new_history = [*new_history, user_div, assistant_div]

            return (
                f"/streaming-{self.id}",
                sse_options(
                    json.dumps(
                        {
                            "prompt": value.strip(),
                            "chat_history": json.dumps(messages_array),
                        }
                    ),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                ),
                new_history,
                updated_messages,
                "",  # Reset stream buffer
                False,  # Reset completion trigger
            )

        @callback(
            Output(f"{self.id}-streaming-components", "children"),
            Input(f"{self.id}-stream-buffer", "data"),
            prevent_initial_call=True,
        )
        def update_streaming_display(buffer_data):
            """Update the streaming display from the buffer data."""
            if not buffer_data:
                return []

            return _create_message_components(buffer_data, self.id)

        @callback(
            Output(f"{self.id}-stream-buffer", "data"),
            Output(f"{self.id}-completion-trigger", "data"),
            Input(f"{self.id}-sse", "animation"),
            Input(f"{self.id}-sse", "done"),
            prevent_initial_call=True,
        )
        def update_streaming_buffer(animation, done):
            """Update streaming buffer with parsed SSE data and detect completion."""
            if not animation:
                return dash.no_update, dash.no_update

            messages = _parse_sse_chunks(animation)
            if not messages:
                return dash.no_update, dash.no_update

            content_items = []
            current_text = ""

            for msg in messages:
                msg_type = msg.get("type", "text")
                msg_content = msg.get("content", "")
                msg_metadata = msg.get("metadata", {})

                if msg_type == "code":
                    current_text = _flush_accumulated_text(current_text, content_items)
                    content_items.append(
                        {
                            "type": "code",
                            "content": msg_content,
                            "metadata": msg_metadata,
                        }
                    )
                elif msg_type == "plotly_graph":
                    current_text = _flush_accumulated_text(current_text, content_items)
                    content_items.append({"type": "plotly_graph", "content": msg_content, "metadata": msg_metadata})
                else:
                    current_text += msg_content

            current_text = _flush_accumulated_text(current_text, content_items)

            # Use SSE done property for completion detection
            if done:
                return content_items, True  # content, trigger_completion

            return content_items, dash.no_update

        # Add callback to update messages store when completion is triggered
        @callback(
            Output(f"{self.id}-messages", "data", allow_duplicate=True),
            Output(f"{self.id}-completion-trigger", "data", allow_duplicate=True),
            Input(f"{self.id}-completion-trigger", "data"),
            State(f"{self.id}-stream-buffer", "data"),
            State(f"{self.id}-messages", "data"),
            prevent_initial_call="initial_duplicate",
        )
        def update_messages_store_on_completion(completion_triggered, content, messages):
            """Update messages store with final content when streaming completes."""
            if not completion_triggered or not content:
                return dash.no_update, dash.no_update

            # Store structured content to preserve plotly graphs and other rich content
            structured_content = content if isinstance(content, list) else [{"type": "text", "content": str(content)}]

            messages_array = json.loads(messages)
            # Find and update the last assistant message (placeholder) instead of adding new one
            updated = False
            for i in range(len(messages_array) - 1, -1, -1):
                if messages_array[i].get("role") == "assistant":
                    messages_array[i]["content"] = structured_content
                    updated = True
                    break

            if not updated:
                # Fallback: add new message if no placeholder found
                assistant_message = {"role": "assistant", "content": structured_content}
                messages_array.append(assistant_message)

            final_messages = json.dumps(messages_array)
            return final_messages, False  # Reset completion trigger

        # this clientside callback scrolls the chat history so
        # that the user message is visible.
        # ideally the user message is at the current screen,
        # but this version scrolls to the offset of the user message top.
        clientside_callback(
            f"""
            function(n_clicks, n_submit) {{
                if (!n_clicks && !n_submit) return window.dash_clientside.no_update;
                setTimeout(() => {{
                    const historyDiv = document.getElementById('{self.id}-history');
                    const children = historyDiv?.children;
                    const userMessage = children?.[children.length - 2];
                    if (userMessage) historyDiv.scrollTop = userMessage.offsetTop;
                }}, 200);
                return window.dash_clientside.no_update;
            }}
            """,
            Output(f"{self.id}-history", "data-smart-scroll"),
            Input(f"{self.id}-submit", "n_clicks"),
            Input(f"{self.id}-input", "n_submit"),
        )

    @_log_call
    def build(self):
        """Build the chat component layout."""
        components = []

        components.extend(self._build_data_stores())
        components.append(self._build_chat_interface())
        components.append(SSE(id=f"{self.id}-sse", concat=True, animate_chunk=20, animate_delay=5))

        return html.Div(
            components,
            style={
                **ROOT_CONTAINER,
                "height": self.height,
            },
        )

    def _build_data_stores(self):
        """Build the data store components for the chat."""
        return [
            dcc.Store(id=f"{self.id}-messages", storage_type=self.storage_type),
            dcc.Store(id=f"{self.id}-stream-buffer", data=""),
            dcc.Store(id=f"{self.id}-completion-trigger", data=False),
        ]

    def _build_chat_interface(self):
        """Build the main chat interface."""
        return html.Div(
            [
                html.Div(
                    html.Div(
                        id=f"{self.id}-history",
                        style=HISTORY_CONTAINER,
                    ),
                    style=HISTORY_SECTION,
                ),
                html.Div(
                    dbc.InputGroup(
                        [
                            dbc.Textarea(
                                id=f"{self.id}-input",
                                placeholder=self.input_placeholder,
                                autoFocus=True,
                                style={
                                    **INPUT_FIELD,
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
                        style=INPUT_GROUP,
                    ),
                    style=INPUT_SECTION,
                ),
            ],
            style=MAIN_CONTAINER,
        )
