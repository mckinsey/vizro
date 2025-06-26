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

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models.types import _IdProperty
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

# Code block styling for markdown with Claude-style clipboard buttons
CODE_BLOCK_STYLE = """
/* Force code block styling with maximum specificity */
pre,
div pre,
.dash-graph pre,
.markdown-container pre,
div.markdown-container pre,
[class*="markdown"] pre {
    background: #1e1e1e !important;
    background-color: #1e1e1e !important;
    padding: 10px !important;
    margin: 0 !important;
    border-radius: 6px !important;
    border: 1px solid #333 !important;
    overflow-x: auto !important;
    position: relative !important;
    color: #e5e5e5 !important;
}

.markdown-container code,
div.markdown-container code {
    background: var(--surfaces-bg-card) !important;
    padding: 2px 4px !important;
    border-radius: 3px !important;
    font-family: 'Monaco', 'SF Mono', 'Consolas', monospace !important;
}

.markdown-container pre code,
div.markdown-container pre code {
    background: transparent !important;
    padding: 0 !important;
}

/* Claude-style clipboard button with higher specificity */
.code-clipboard-btn,
div .code-clipboard-btn {
    position: absolute !important;
    top: 5px !important;
    right: 5px !important;
    background: rgba(255, 255, 255, 0.1) !important;
    border: none !important;
    border-radius: 4px !important;
    padding: 4px 6px !important;
    cursor: pointer !important;
    font-size: 14px !important;
    color: var(--text-secondary, #888) !important;
    opacity: 0 !important;
    transition: all 0.15s ease !important;
    user-select: none !important;
    z-index: 1001 !important;
    width: auto !important;
    height: auto !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

.markdown-container pre:hover .code-clipboard-btn,
div.markdown-container pre:hover .code-clipboard-btn {
    opacity: 1 !important;
}

.code-clipboard-btn:hover,
div .code-clipboard-btn:hover {
    background: rgba(255, 255, 255, 0.2) !important;
    color: var(--text-primary, #fff) !important;
}

.code-clipboard-btn:active,
div .code-clipboard-btn:active {
    transform: scale(0.9) !important;
}

.code-clipboard-btn.copied,
div .code-clipboard-btn.copied {
    color: #10b981 !important;
    opacity: 1 !important;
    background: rgba(16, 185, 129, 0.1) !important;
}
"""


def parse_sse_chunks(animation_data):
    """Parse SSE animation data and return complete JSON objects."""
    if not animation_data:
        return []
    
    try:
        if isinstance(animation_data, list):
            return [json.loads(msg) for msg in animation_data]
        elif isinstance(animation_data, str):
            # Handle concatenated JSON objects
            chunks = animation_data.replace('}{', '}\n{')
            lines = [line.strip() for line in chunks.splitlines() if line.strip()]
            return [json.loads(line) for line in lines if line]
        else:
            return [json.loads(animation_data)]
    except (json.JSONDecodeError, TypeError):
        return []


def render_streaming_message(component_id):
    """Create a streaming message container with smooth rendering."""
    markdown_id = f"{component_id}-streaming-markdown"
    return html.Div([
        # Stores for managing the streaming state
        dcc.Store(id=f"{component_id}-stream-buffer", data=""),
        dcc.Store(id=f"{component_id}-render-buffer", data=""),
        dcc.Store(id=f"{component_id}-render-position", data=0),
        
        # Timer for smooth rendering
        dcc.Interval(
            id=f"{component_id}-render-timer", 
            interval=33,  # ~30fps for smooth animation
            n_intervals=0,
            disabled=True
        ),
        
        # The content container with code block styling
        dcc.Markdown(
            id=markdown_id,
            children="",
            className="markdown-container",
            style={
                "minHeight": "20px",
                "margin": 0,
            },
            # Enable code highlighting and custom styling
            # highlight_config={"theme": "dark"},
        ),
    ])


class Chat(VizroBaseModel):
    """A chat component for Vizro dashboards that implements the plugin interface.

    This component provides interactive chat functionality that can be
    integrated into Vizro dashboards. It supports different processors
    for handling chat responses, including simple echoing and OpenAI integration.

    To use this component, it must be passed as a plugin to Vizro to properly
    register its streaming routes.

    Args:
        type (Literal["chat"]): Defaults to `"chat"`.
        id (str): Unique identifier for the component.
        input_placeholder (str): Placeholder text for the input field. Defaults to `"Ask me a question..."`.
        input_height (str): Height of the input field. Defaults to `"80px"`.
        button_text (str): Text displayed on the send button. Defaults to `"Send"`.
        initial_message (str): Initial message displayed in the chat. Defaults to `"Hello! How can I help you today?"`.
        processor (ChatProcessor): Chat processor for generating responses. Defaults to `EchoProcessor()`.
        
    Example:
        ```python
        import vizro.models as vm
        from vizro import Vizro
        import vizro_ai.models as vam
        
        # Create component
        chat_component = vam.Chat(id="my_chat")
        
        # Register component type
        vm.Page.add_type("components", vam.Chat)
        
        # Create dashboard
        dashboard = vm.Dashboard(pages=[vm.Page(components=[chat_component])])
        
        # Pass component as plugin to Vizro
        Vizro(plugins=[chat_component]).build(dashboard).run()
        ```
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    type: Literal["chat"] = "chat"
    id: str
    input_placeholder: str = Field(default="Ask me a question...", description="Placeholder text for the input field")
    input_height: str = Field(default="80px", description="Height of the input field")
    button_text: str = Field(default="Send", description="Text displayed on the send button")
    initial_message: str = Field(default="Hello! How can I help you today!", description="Initial message displayed in the chat")
    height: str = Field(default="100%", description="Height of the chat component wrapper")
    processor: ChatProcessor = Field(default_factory=EchoProcessor, description="Chat processor for generating responses")

    @property 
    def _action_outputs(self) -> dict[str, _IdProperty]:
        """Define action outputs for the chat component."""
        return {"__default__": f"{self.id}-history.children"}

    @property
    def _action_inputs(self) -> dict[str, _IdProperty]:
        """Define action inputs for the chat component."""
        return {"input": f"{self.id}-input.value"}

    def plug(self, app):
        """Plugin method called by Dash to register routes and other app-level configurations.
        
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

                if not user_prompt:
                    raise ValueError("Empty prompt")

                # Initialize processor with API settings if available
                api_settings = data.get("api_settings", {})
                if api_settings and hasattr(self.processor, "initialize_client"):
                    api_key = api_settings.get("api_key")
                    api_base = api_settings.get("api_base")
                    if api_key:
                        self.processor.initialize_client(api_key=api_key, api_base=api_base)

                def response_stream():
                    try:
                        for chat_message in self.processor.get_response(messages, user_prompt):
                            yield sse_message(chat_message.to_json())
                        yield sse_message()  # Final empty message to signal completion
                    except Exception as e:
                        error_msg = ChatMessage(type="error", content=f"Error: {e!s}")
                        yield sse_message(error_msg.to_json())

                return Response(response_stream(), mimetype="text/event-stream")
            except Exception as e:
                return Response(f"Error: {e!s}", status=500)

    @_log_call
    def pre_build(self):
        """Register callbacks before building the component."""
        self._register_streaming_callback()

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
            Output(f"{self.id}-stream-buffer", "data", allow_duplicate=True),
            Output(f"{self.id}-render-position", "data", allow_duplicate=True),
            Input(f"{self.id}-submit", "n_clicks"),
            Input(f"{self.id}-input", "n_submit"),
            State(f"{self.id}-input", "value"),
            State(f"{self.id}-messages", "data"),
            State(f"{self.id}-history", "children"),
            prevent_initial_call=True,
        )
        def start_streaming(n_clicks, n_submit, value, messages, current_history):
            if (not n_clicks and not n_submit) or not value or not value.strip():
                return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

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

            # Create assistant div for streaming
            assistant_div = html.Div(
                id=f"{self.id}-streaming-content",
                children=render_streaming_message(self.id),  # Streaming container
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
                json.dumps(messages_array),
                "",  # Reset stream buffer
                0,   # Reset render position
            )

                # Client-side callback for smooth streaming rendering
        clientside_callback(
            """
            function(n_intervals, stream_buffer, render_position, timer_disabled) {
                // Stop processing if timer is disabled
                if (timer_disabled || !stream_buffer || stream_buffer.length === 0) {
                    return [window.dash_clientside.no_update, window.dash_clientside.no_update];
                }
                
                // Safe markdown parsing - handle incomplete code blocks
                function safeParseMarkdown(content) {
                    const fenceCount = (content.match(/```/g) || []).length;
                    if (fenceCount % 2 !== 0) {
                        // Find last complete fence pair
                        const lines = content.split('\\n');
                        let fenceIndices = [];
                        for (let i = 0; i < lines.length; i++) {
                            if (lines[i].trim().startsWith('```')) {
                                fenceIndices.push(i);
                            }
                        }
                        if (fenceIndices.length >= 2 && fenceIndices.length % 2 !== 0) {
                            const safeCutoff = fenceIndices[fenceIndices.length - 1];
                            return lines.slice(0, safeCutoff).join('\\n');
                        }
                    }
                    return content;
                }
                
                const safeContent = safeParseMarkdown(stream_buffer);
                const targetLength = safeContent.length;
                
                if (render_position < targetLength) {
                    // Add 2-4 characters per frame for smooth streaming
                    const charsToAdd = Math.min(Math.max(2, Math.floor(targetLength / 100)), 4);
                    const newPosition = Math.min(render_position + charsToAdd, targetLength);
                    const displayContent = safeContent.slice(0, newPosition);
                    
                    return [newPosition, displayContent];
                }
                
                // Animation complete - return no update to stop triggering
                return [window.dash_clientside.no_update, window.dash_clientside.no_update];
            }
            """,
            [Output(f"{self.id}-render-position", "data"),
             Output(f"{self.id}-streaming-markdown", "children")],
            Input(f"{self.id}-render-timer", "n_intervals"),
            [State(f"{self.id}-stream-buffer", "data"),
             State(f"{self.id}-render-position", "data"),
             State(f"{self.id}-render-timer", "disabled")]
        )

        # Callback to disable timer when rendering is complete
        @callback(
            Output(f"{self.id}-render-timer", "disabled", allow_duplicate=True),
            Input(f"{self.id}-render-position", "data"),
            State(f"{self.id}-stream-buffer", "data"),
            prevent_initial_call=True,
        )
        def disable_timer_when_complete(render_position, stream_buffer):
            if not stream_buffer:
                return True
            
            # If we've rendered all the content, disable the timer
            if render_position >= len(stream_buffer):
                return True
            
            return dash.no_update

        # Add clientside callback to handle clipboard functionality for code blocks
        clientside_callback(
            """
            function(children) {
                setTimeout(function() {
                    // Remove existing clipboard buttons
                    const existingButtons = document.querySelectorAll('.code-clipboard-btn');
                    existingButtons.forEach(btn => btn.remove());
                    
                    // Find all code blocks with multiple selectors
                    const codeBlocks = document.querySelectorAll('pre, .markdown-container pre, [class*="markdown"] pre');
                    
                    // Debug: log what we found
                    console.log('Found code blocks:', codeBlocks.length);
                    
                    codeBlocks.forEach(function(pre, index) {
                        // Debug: log the element
                        console.log('Processing code block:', pre);
                        
                        // Force styling directly on the element
                        pre.style.background = '#1e1e1e';
                        pre.style.backgroundColor = '#1e1e1e';
                        pre.style.padding = '10px';
                        pre.style.margin = '0';
                        pre.style.borderRadius = '6px';
                        pre.style.border = '1px solid #333';
                        pre.style.position = 'relative';
                        pre.style.color = '#e5e5e5';
                        // Skip if button already exists
                        if (pre.querySelector('.code-clipboard-btn')) return;
                        
                        // Create clipboard button with SVG icon (Claude-style)
                        const clipboardBtn = document.createElement('button');
                        clipboardBtn.className = 'code-clipboard-btn';
                        clipboardBtn.title = 'Copy code';
                        
                        // Clean clipboard SVG icon
                        clipboardBtn.innerHTML = `
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                                <rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect>
                                <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path>
                            </svg>
                        `.replace(/\\s+/g, ' ').trim();
                        
                        // Ensure proper positioning 
                        clipboardBtn.style.position = 'absolute';
                        clipboardBtn.style.top = '5px';
                        clipboardBtn.style.right = '5px';
                        clipboardBtn.style.zIndex = '1001';
                        
                        // Add click handler
                        clipboardBtn.onclick = function(e) {
                            e.stopPropagation();
                            const code = pre.querySelector('code');
                            if (code) {
                                const codeText = code.textContent || code.innerText;
                                navigator.clipboard.writeText(codeText).then(function() {
                                    // Visual feedback - checkmark icon
                                    clipboardBtn.innerHTML = `
                                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <polyline points="20,6 9,17 4,12"></polyline>
                                        </svg>
                                    `.replace(/\\s+/g, ' ').trim();
                                    clipboardBtn.classList.add('copied');
                                    
                                    setTimeout(function() {
                                        clipboardBtn.innerHTML = `
                                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                                                <rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect>
                                                <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path>
                                            </svg>
                                        `.replace(/\\s+/g, ' ').trim();
                                        clipboardBtn.classList.remove('copied');
                                    }, 1500);
                                }).catch(function(err) {
                                    console.error('Failed to copy: ', err);
                                    clipboardBtn.innerHTML = `
                                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <circle cx="12" cy="12" r="10"></circle>
                                            <line x1="15" y1="9" x2="9" y2="15"></line>
                                            <line x1="9" y1="9" x2="15" y2="15"></line>
                                        </svg>
                                    `.replace(/\\s+/g, ' ').trim();
                                    setTimeout(function() {
                                        clipboardBtn.innerHTML = `
                                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                                                <rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect>
                                                <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path>
                                            </svg>
                                        `.replace(/\\s+/g, ' ').trim();
                                    }, 1500);
                                });
                            }
                        };
                        
                        // Append button to code block
                        pre.appendChild(clipboardBtn);
                    });
                }, 100);
                return window.dash_clientside.no_update;
            }
            """,
            Output(f"{self.id}-streaming-markdown", "style"),
            Input(f"{self.id}-streaming-markdown", "children")
        )

        @callback(
            Output(f"{self.id}-stream-buffer", "data"),
            Output(f"{self.id}-render-timer", "disabled"),
            Input(f"{self.id}-sse", "animation"),
            prevent_initial_call=True,
        )
        def update_streaming_buffer(animation):
            if not animation:
                return dash.no_update, dash.no_update

            messages = parse_sse_chunks(animation)
            if not messages:
                return "", True

            # Build content from scratch each time (no accumulation to avoid duplication)
            aggregated_content = ""
            for msg in messages:
                msg_type = msg.get("type", "text")
                msg_content = msg.get("content", "")
                
                if msg_type == "code":
                    aggregated_content += f"```{msg_content}```\n\n"
                else:
                    aggregated_content += msg_content
            
            return aggregated_content, False

        # Add callback to update messages store after streaming completes
        @callback(
            Output(f"{self.id}-messages", "data", allow_duplicate=True),
            Output(f"{self.id}-render-timer", "disabled", allow_duplicate=True),
            Output(f"{self.id}-render-position", "data", allow_duplicate=True),
            Input(f"{self.id}-sse", "completed"),
            State(f"{self.id}-stream-buffer", "data"),
            State(f"{self.id}-messages", "data"),
            prevent_initial_call="initial_duplicate",
        )
        def update_messages_store(completed, content, messages):
            if not completed or not content:
                return dash.no_update, dash.no_update, dash.no_update

            messages_array = json.loads(messages)
            assistant_message = {"role": "assistant", "content": content}
            messages_array.append(assistant_message)
            return json.dumps(messages_array), True, 0

    @_log_call
    def build(self):
        """Build the chat component layout."""
        components = []
        
        # Add CSS styling for code blocks
        components.append(dcc.Markdown(
            f"<style>{CODE_BLOCK_STYLE}</style>",
            dangerously_allow_html=True
        ))
        
        components.extend(self._build_data_stores())
        components.append(self._build_chat_interface())
        components.append(SSE(id=f"{self.id}-sse", concat=True, animate_chunk=5, animate_delay=10))
        
        return html.Div(
            components,
            style={
                **WRAPPER,
                "height": self.height,
            },
        )

    def _build_data_stores(self):
        """Build the data store components for the chat."""
        return [
            dcc.Store(id=f"{self.id}-messages", storage_type="session"),
            dcc.Store(id=f"{self.id}-stream-buffer", data=""),
            dcc.Store(id=f"{self.id}-render-position", data=0),
            dcc.Interval(
                id=f"{self.id}-render-timer", 
                interval=33,  # ~30fps
                n_intervals=0,
                disabled=True
            ),
        ]

    def _build_chat_interface(self):
        """Build the main chat interface."""
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