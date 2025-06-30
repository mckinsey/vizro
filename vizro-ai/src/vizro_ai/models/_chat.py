"""Vizro-AI chat model following vizro-core patterns."""

import json
from typing import Literal, Optional

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, clientside_callback, dcc, html
from dash_extensions import SSE
from dash_extensions.streaming import sse_message, sse_options
from flask import Response, request
from pydantic import ConfigDict, Field
import plotly.graph_objects as go

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro_ai.models._processors import ChatMessage, ChatProcessor, EchoProcessor

# Styling constants
WRAPPER = {
    "width": "100%",
    "height": "100%",
    "display": "flex",
    "flexDirection": "column",
}

CHAT_CONTAINER_STYLE = {
    "display": "flex",
    "flexDirection": "column",
    "flex": "1",
    "width": "100%",
    "height": "100%",
}

CHAT_INPUT_WRAPPER_STYLE = {
    "display": "flex",
    "justifyContent": "center",
    "width": "100%",
    "marginTop": "auto",
}

CHAT_INPUT_CONTAINER_STYLE = {
    "borderRadius": "10px",
    "height": "80px",
    "backgroundColor": "var(--surfaces-bg-card)",
    "zIndex": "1",
    "width": "100%",
    "maxWidth": "760px",
}

CHAT_HISTORY_WRAPPER_STYLE = {
    "display": "flex",
    "justifyContent": "center",
    "width": "100%",
    "flex": "1",
    "overflow": "hidden",
}

CHAT_HISTORY_STYLE = {
    "width": "100%",
    "paddingBottom": "20px",
    "paddingLeft": "5px",
    "maxWidth": "760px",
    "overflow": "auto",
}

CODE_BLOCK_CONTAINER_STYLE = {
    "position": "relative",
    "backgroundColor": "var(--surfaces-bg-card)",
    "borderRadius": "10px",
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
    "boxShadow": "none",
    "border": "1px solid var(--border-subtleAlpha01)",
}


def parse_sse_chunks(animation_data) -> list[dict]:
    """Parse SSE animation data and return complete JSON objects.
    
    Args:
        animation_data: Raw SSE data from the streaming endpoint
        
    Returns:
        List of parsed JSON objects from the SSE stream
    """
    if not animation_data:
        return []
    
    try:
        if isinstance(animation_data, list):
            return [json.loads(msg) for msg in animation_data if msg]
        elif isinstance(animation_data, str):
            # Handle concatenated JSON objects by finding complete JSON boundaries
            chunks = []
            buffer = ""
            brace_count = 0
            in_string = False
            escape_next = False
            
            for char in animation_data:
                buffer += char
                
                # Track if we're inside a string to ignore braces there
                if not escape_next:
                    if char == '"' and not in_string:
                        in_string = True
                    elif char == '"' and in_string:
                        in_string = False
                    elif char == '\\':
                        escape_next = True
                        continue
                else:
                    escape_next = False
                    continue
                
                # Count braces only outside of strings
                if not in_string:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        
                        # When brace count returns to 0, we have a complete JSON object
                        if brace_count == 0 and buffer.strip():
                            try:
                                chunks.append(json.loads(buffer))
                                buffer = ""
                            except json.JSONDecodeError:
                                # If we can't parse it, keep accumulating
                                pass
            
            return chunks
        else:
            return [json.loads(animation_data)]
    except (json.JSONDecodeError, TypeError):
        return []
    

def create_code_block_component(code_content, code_id) -> html.Div:
    """Create a consistent code block component with clipboard functionality.
    
    Args:
        code_content: The code content to display
        code_id: Unique ID for the code block
        
    Returns:
        Dash HTML component with code block and clipboard button
    """
    return html.Div([
        dcc.Clipboard(
            target_id=code_id,
            className="code-clipboard",
            style={
                "position": "absolute",
                "top": "8px",
                "right": "8px",
                "opacity": 0.7,
                "zIndex": 1000,
                "transition": "opacity 0.2s ease",
                "padding": "4px 6px",
                "cursor": "pointer",
            },
            title="Copy code"
        ),
        dcc.Markdown(
            f"```\n{code_content}\n```",
            id=code_id,
            className="markdown-container code-block-container",
            style={
                "fontFamily": "monospace",
                "padding": "10px",
                }
        ),
    ], style=CODE_BLOCK_CONTAINER_STYLE)





class Chat(VizroBaseModel):
    """A chat component for Vizro dashboards that implements the plugin interface.

    This component provides interactive chat functionality that can be
    integrated into Vizro dashboards. It supports different processors
    for handling chat responses, including simple echoing and OpenAI integration.

    To use this component, it must be passed as a plugin to Vizro to properly
    register its streaming routes.

    Args:
        type (Literal["chat"]): Defaults to `"chat"`.
        input_placeholder (str): Placeholder text for the input field. Defaults to `"Ask me a question..."`.
        input_height (str): Height of the input field. Defaults to `"80px"`.
        button_text (str): Text displayed on the send button. Defaults to `"Send"`.
        initial_message (str): Initial message displayed in the chat. Defaults to `"Hello! How can I help you today?"`.
        height (str): Height of the chat component wrapper. Defaults to `"100%"`.
        storage_type (Literal["memory", "session", "local"]): Storage type for chat history persistence. Defaults to `"session"`.
        processor (ChatProcessor): Chat processor for generating responses. Defaults to `EchoProcessor()`.
        
    Example:
        ```python
        import vizro.models as vm
        from vizro import Vizro
        import vizro_ai.models as vam
        
        # Create component
        chat_component = vam.Chat(processor=vam.EchoProcessor())
        
        # Register component type
        vm.Page.add_type("components", vam.Chat)
        
        # Create dashboard
        dashboard = vm.Dashboard(pages=[vm.Page(components=[chat_component])])
        
        # Pass component as plugin to Vizro
        Vizro(plugins=[chat_component]).build(dashboard).run()
        ```
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # TODO: make initial_message optional
    type: Literal["chat"] = "chat"
    input_placeholder: str = Field(default="Ask me a question...", description="Placeholder text for the input field")
    input_height: str = Field(default="80px", description="Height of the input field")
    button_text: str = Field(default="Send", description="Text displayed on the send button")
    initial_message: str = Field(default="Hello! How can I help you today!", description="Initial message displayed in the chat")
    height: str = Field(default="100%", description="Height of the chat component wrapper")
    storage_type: Literal["memory", "session", "local"] = Field(default="session", description="Storage type for chat history persistence")
    processor: ChatProcessor = Field(default_factory=EchoProcessor, description="Chat processor for generating responses")

    def plug(self, app):
        """Register streaming routes with the Dash app.
        
        This method is called automatically when the component is passed as a plugin
        to Dash (via Vizro). It registers the streaming endpoint needed for the chat
        functionality.
        
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
                        for chat_message in self.processor.get_response(messages, user_prompt):
                            yield sse_message(chat_message.to_json())
                        # Send standard SSE completion signal
                        # https://github.com/emilhe/dash-extensions/blob/78d1de50d32f888e5f287cfedfa536fe314ab0b4/dash_extensions/streaming.py#L6
                        yield sse_message("[DONE]")
                    except Exception as e:
                        error_msg = ChatMessage(type="error", content=f"Error: {e!s}")
                        yield sse_message(error_msg.to_json())
                        yield sse_message("[DONE]")

                # Use Response with SSE content type
                response = Response(response_stream(), mimetype="text/event-stream")
                return response
            except Exception as e:
                return Response(f"Error: {e!s}", status=500)

    @_log_call
    def pre_build(self):
        """Register callbacks before building the component."""
        self._register_streaming_callback()

    def _register_streaming_callback(self):
        """Register callbacks for chat functionality."""
        
        # TODO: double check whether this is needed, if so, move to other place
        def create_message_components(content, message_id):
            """Parse markdown content and create components with dcc.Clipboard for code blocks."""
            import re
            
            # Simple regex to find code blocks
            code_pattern = r'```(.*?)```'
            parts = re.split(code_pattern, content, flags=re.DOTALL)
            
            components = []
            for i, part in enumerate(parts):
                if i % 2 == 0:  # Text content
                    if part.strip():
                        components.append(
                            dcc.Markdown(
                                part,
                                className="markdown-container",
                                style={"margin": 0}
                            )
                        )
                else:  # Code content
                    code_id = f"{message_id}-code-{i // 2}"
                    components.append(create_code_block_component(part.strip(), code_id))
                    components.append(html.Br())
            
            return html.Div(components) if components else ""

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
                initial_data = json.dumps([{"role": "assistant", "content": self.initial_message}])
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
                        # Create user message div
                        div = html.Div(
                            content,
                            style={
                                **MESSAGE_STYLE,
                                "backgroundColor": "var(--surfaces-bg-card)",
                                "borderLeft": "4px solid #aaa9ba",
                            }
                        )
                    elif role == "assistant":
                        # Skip empty assistant messages (placeholders)
                        if not content.strip():
                            continue
                        # Create assistant message div with parsed components
                        message_id = f"{self.id}-history-msg-{idx}"
                        div = html.Div(
                            create_message_components(content, message_id),
                            style={
                                **MESSAGE_STYLE,
                                "backgroundColor": "var(--right-side-bg)",
                                "borderLeft": "4px solid #00b4ff",
                            }
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

            # Create user message div
            user_div = html.Div(
                value.strip(),
                style={
                    **MESSAGE_STYLE,
                    "backgroundColor": "var(--surfaces-bg-card)",
                    "borderLeft": "4px solid #aaa9ba",
                }
            )

            # Create assistant div for streaming
            assistant_div = html.Div(
                id=f"{self.id}-streaming-content",
                children=html.Div(
                    id=f"{self.id}-streaming-components",
                    children=[],  # Will hold mixed content: streaming text and code blocks
                ),
                style={
                    **MESSAGE_STYLE,
                    "backgroundColor": "var(--right-side-bg)",
                    "borderLeft": "4px solid #00b4ff",
                }
            )

            # Update history with both divs (append to existing history)
            new_history = current_history or []
            new_history = new_history + [user_div, assistant_div]

            return (
                f"/streaming-{self.id}",
                sse_options(
                    json.dumps({
                        "prompt": value.strip(),
                        "chat_history": json.dumps(messages_array),
                    }),
                    headers={"Content-Type": "application/json"},
                    method="POST"
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
            
            components = []
            for item in buffer_data:
                if item["type"] == "text":
                    components.append(
                        dcc.Markdown(
                            item["content"],
                            className="markdown-container",
                            style={"margin": 0}
                        )
                    )
                elif item["type"] == "code":
                    code_id = f"{self.id}-code-{item['index']}"
                    components.append(create_code_block_component(item["content"], code_id))
                    components.append(html.Br())
                elif item["type"] == "plotly_graph":
                    fig_data = json.loads(item["content"])
                    components.append(
                        dcc.Graph(
                            figure=go.Figure(fig_data),
                        )
                    )
                    components.append(html.Br())
            
            return components

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

            messages = parse_sse_chunks(animation)
            if not messages:
                return dash.no_update, dash.no_update

            # Build structured content for mixed text/code display
            content_items = []
            current_text = ""
            code_block_index = 0
            graph_index = 0
            
            for msg in messages:
                msg_type = msg.get("type", "text")
                msg_content = msg.get("content", "")
                msg_metadata = msg.get("metadata", {})
                
                if msg_type == "code":
                    # If we have accumulated text, add it first
                    if current_text:
                        content_items.append({
                            "type": "text",
                            "content": current_text
                        })
                        current_text = ""
                    
                    # Add code block as a separate item
                    content_items.append({
                        "type": "code",
                        "content": msg_content,
                        "index": code_block_index
                    })
                    code_block_index += 1
                elif msg_type == "plotly_graph":
                    # If we have accumulated text, add it first
                    if current_text:
                        content_items.append({
                            "type": "text",
                            "content": current_text
                        })
                        current_text = ""
                    
                    # Add graph as a separate item
                    content_items.append({
                        "type": "plotly_graph",
                        "content": msg_content,
                        "index": graph_index,
                        "metadata": msg_metadata
                    })
                    graph_index += 1
                else:
                    # Accumulate text content
                    current_text += msg_content
            
            # Add any remaining text
            if current_text:
                content_items.append({
                    "type": "text",
                    "content": current_text
                })
            
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

            # Convert structured content back to markdown for storage
            markdown_content = ""
            if isinstance(content, list):
                for item in content:
                    if item["type"] == "text":
                        markdown_content += item["content"]
                    elif item["type"] == "code":
                        # Store code blocks in markdown format
                        markdown_content += f"\n```\n{item['content']}\n```\n"
                    elif item["type"] == "plotly_graph":
                        # Store graphs as special markdown blocks with JSON data
                        title = item.get("metadata", {}).get("title", "Chart")
                        markdown_content += f"\n**{title}**\n*[Interactive chart rendered in chat]*\n\n"
            else:
                # Fallback for string content
                markdown_content = content

            messages_array = json.loads(messages)
            # Find and update the last assistant message (placeholder) instead of adding new one
            updated = False
            for i in range(len(messages_array) - 1, -1, -1):
                if messages_array[i].get("role") == "assistant":
                    messages_array[i]["content"] = markdown_content.strip()
                    updated = True
                    break
            
            if not updated:
                # Fallback: add new message if no placeholder found
                assistant_message = {"role": "assistant", "content": markdown_content.strip()}
                messages_array.append(assistant_message)
            
            final_messages = json.dumps(messages_array)
            return final_messages, False  # Reset completion trigger
        
        # this clientside callback scrolls the chat history so
        # that the user message is visible.
        # ideally the user message is at the current screen,
        # but this version scrolls to the offset of the user message top.
        clientside_callback(
            """
            function(n_clicks, n_submit) {
                if (!n_clicks && !n_submit) return window.dash_clientside.no_update;
                setTimeout(() => {
                    const historyDiv = document.getElementById('%s-history');
                    const children = historyDiv?.children;
                    const userMessage = children?.[children.length - 2];
                    if (userMessage) historyDiv.scrollTop = userMessage.offsetTop;
                }, 200);
                return window.dash_clientside.no_update;
            }
            """ % self.id,
            Output(f"{self.id}-history", "data-smart-scroll"),
            Input(f"{self.id}-submit", "n_clicks"),
            Input(f"{self.id}-input", "n_submit")
        )

    @_log_call
    def build(self):
        """Build the chat component layout.
        
        Returns:
            Dash HTML component containing the complete chat interface
        """
        components = []

        components.extend(self._build_data_stores())
        components.append(self._build_chat_interface())
        components.append(SSE(id=f"{self.id}-sse", concat=True, animate_chunk=20, animate_delay=5))
        
        return html.Div(
            components,
            style={
                **WRAPPER,
                "height": self.height,
            },
        )

    def _build_data_stores(self):
        """Build the data store components for the chat.
        
        Returns:
            List of dcc.Store components for chat data persistence
        """
        return [
            dcc.Store(id=f"{self.id}-messages", storage_type=self.storage_type),
            dcc.Store(id=f"{self.id}-stream-buffer", data=""),
            dcc.Store(id=f"{self.id}-completion-trigger", data=False),
        ]

    def _build_chat_interface(self):
        """Build the main chat interface.
        
        Returns:
            Dash HTML component containing the chat history and input area
        """
        return html.Div(
            [
                html.Div(
                    html.Div(
                        id=f"{self.id}-history",
                        style=CHAT_HISTORY_STYLE,
                    ),
                    style=CHAT_HISTORY_WRAPPER_STYLE,
                ),
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
                    style=CHAT_INPUT_WRAPPER_STYLE,
                ),
            ],
            style=CHAT_CONTAINER_STYLE,
        ) 