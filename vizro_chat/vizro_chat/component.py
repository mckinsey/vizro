"""Vizro chat component."""

import json
from typing import Literal, Optional

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html, callback
from flask import Response, request
from pydantic import ConfigDict
from vizro._vizro import Vizro
from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call

from vizro_chat.processors import ChatProcessor, EchoProcessor, OpenAIProcessor

# Common style definitions
CHAT_CONTAINER_STYLE = {
    "display": "flex",
    "flexDirection": "column",
    "height": "100%",
    "width": "100%",
    "backgroundColor": "var(--mantine-color-dark-light)",
    "position": "relative",
}

CHAT_HISTORY_STYLE = {
    "overflowY": "auto",
    "padding": "20px",
    "gap": "10px",
    "width": "100%",
    "flex": "1 1 auto",
    "display": "flex",
    "flexDirection": "column",
}

CHAT_INPUT_CONTAINER_STYLE = {
    "padding": "20px",
    "flex": "0 0 auto",
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
    "backgroundColor": "var(--mantine-color-dark-light-hover)",
    "color": "var(--text-primary)",
    "padding": "10px 15px",
    "maxWidth": "70%",
    "marginLeft": "0",
    "marginRight": "auto",
    "marginBottom": "15px",
    "whiteSpace": "pre-wrap",
    "wordBreak": "break-word",
    "width": "fit-content",
    "minWidth": "100px",
    "lineHeight": "1.25",
    "letterSpacing": "0.2px",
}

# JavaScript for client-side streaming
STREAMING_CALLBACK_JS = """
function(n_clicks, n_submit, value, messages, api_settings) {
    // Check for initial load or no action
    if (n_clicks === null && n_submit === null) {
        return [messages, ""];
    }

    // Check if either button was clicked or Enter was pressed
    if ((!n_clicks && !n_submit) || !messages) {
        return [messages, value];  // Return both values if no action
    }

    // Check if input is empty or only whitespace
    if (!value || !value.trim()) {
        return [messages, ""];  // Clear input but don't send request
    }

    try {
        const messages_json = JSON.stringify(JSON.parse(messages));
        const triggeredId = window.dash_clientside.callback_context.triggered[0].prop_id;
        const componentId = triggeredId.split('-')[0];
        const chatHistory = document.getElementById(`${componentId}-history`);
        const messages_array = JSON.parse(messages_json);
        
        // Add user message to messages array
        messages_array.push({"role": "user", "content": value});

        // Clear the input field
        const inputField = document.getElementById(`${componentId}-input`);
        if (inputField) {
            inputField.value = '';
        }

        // Start streaming in background
        setTimeout(() => {
            // Create streaming message div
            const streamingDiv = document.createElement('div');
            streamingDiv.style.backgroundColor = "var(--mantine-color-dark-light-hover)";
            streamingDiv.style.color = "var(--text-primary)";
            streamingDiv.style.padding = "10px 15px";
            streamingDiv.style.maxWidth = "70%";
            streamingDiv.style.marginRight = "auto";
            streamingDiv.style.marginBottom = "15px";
            streamingDiv.style.whiteSpace = "pre-wrap";
            streamingDiv.style.wordBreak = "break-word";
            streamingDiv.style.width = "fit-content";
            streamingDiv.style.minWidth = "100px";
            streamingDiv.style.lineHeight = "1.25";
            streamingDiv.style.letterSpacing = "0.2px";
            streamingDiv.style.borderLeft = "2px solid #aaa9ba";

            if (chatHistory) {
                chatHistory.appendChild(streamingDiv);
                chatHistory.scrollTop = chatHistory.scrollHeight;
            }

            // Start streaming
            fetch(`/streaming-${componentId}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    prompt: value.trim(),
                    chat_history: JSON.stringify(messages_array.slice(0, -1)),
                    api_settings: api_settings
                }),
            }).then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let text = "";

                function readChunk() {
                    reader.read().then(({done, value}) => {
                        if (done) {
                            // Add assistant's response to messages array and trigger update
                            messages_array.push({"role": "assistant", "content": text.trim()});
                            window.dash_clientside.no_update = false;
                            window.dispatchEvent(new CustomEvent('dash-update-component', {
                                detail: {
                                    output: `${componentId}-messages.data`,
                                    value: JSON.stringify(messages_array)
                                }
                            }));
                            return;
                        }

                        const chunk = decoder.decode(value);
                        text += chunk;
                        streamingDiv.textContent = text;

                        if (chatHistory) {
                            chatHistory.scrollTop = chatHistory.scrollHeight;
                        }

                        readChunk();
                    });
                }

                readChunk();
            }).catch(error => {
                console.error("Streaming error:", error);
                streamingDiv.textContent = "Error: Could not get response from server.";
            });
        }, 0);

        // Return updated messages and empty string to clear input
        return [JSON.stringify(messages_array), ""];
    } catch (error) {
        console.error("Streaming error:", error);
        return [messages_json, value];  // Keep input on error
    }
}
"""

class VizroChatComponent(VizroBaseModel):
    """A chat component for Vizro dashboards.
    
    This component provides interactive chat functionality that can be
    integrated into Vizro dashboards. It supports different processors
    for handling chat responses, including simple echoing and OpenAI integration.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    type: Literal["chat"] = "chat"
    id: str
    input_placeholder: str = "Ask me a question..."
    input_height: str = "80px"
    button_text: str = "Send"
    vizro_app: Optional[Vizro] = None
    processor: ChatProcessor = EchoProcessor()  # Default to echo processor
    show_settings: bool = True  # Parameter to control settings visibility

    @property
    def messages(self) -> list[dict[str, str]]:
        """Get initial messages list."""
        return []

    @_log_call
    def pre_build(self):
        """Register routes and callbacks before building the component."""
        if self.vizro_app:
            self._register_streaming_route()
            self._register_settings_callbacks()
            self._register_streaming_callback()
            
    def _register_streaming_route(self):
        """Register the streaming endpoint for the chat component."""
        @self.vizro_app.dash.server.route(
            f"/streaming-{self.id}", methods=["POST"], endpoint=f"streaming_chat_{self.id}"
        )
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
                if api_settings and isinstance(self.processor, OpenAIProcessor):
                    api_key = api_settings.get("api_key")
                    api_base = api_settings.get("api_base")
                    if api_key:  # Only initialize if we have an API key
                        self.processor.initialize_client(
                            api_key=api_key,
                            api_base=api_base
                        )

                def response_stream():
                    try:
                        for chunk in self.processor.get_response(messages, user_prompt):
                            yield chunk
                    except Exception as e:
                        yield f"Error: {str(e)}"

                return Response(response_stream(), mimetype="text/event-stream")
            except Exception as e:
                return Response(f"Error: {str(e)}", status=500)

    def _register_settings_callbacks(self):
        """Register callbacks for managing API settings."""
        @self.vizro_app.dash.callback(
            Output(f"{self.id}-settings", "is_open"),
            Input(f"{self.id}-settings-icon", "n_clicks"),
            [State(f"{self.id}-settings", "is_open")],
        )
        def toggle_settings(n_clicks, is_open):
            """Callback for opening and closing offcanvas settings component."""
            return not is_open if n_clicks else is_open

        @self.vizro_app.dash.callback(
            Output(f"{self.id}-api-key", "type"),
            Input(f"{self.id}-api-key-toggle", "value"),
        )
        def show_api_key(value):
            """Callback to show or hide API key."""
            return "text" if value else "password"

        @self.vizro_app.dash.callback(
            Output(f"{self.id}-api-base", "type"),
            Input(f"{self.id}-api-base-toggle", "value"),
        )
        def show_api_base(value):
            """Callback to show or hide API base URL."""
            return "text" if value else "password"

        @self.vizro_app.dash.callback(
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
            if not api_key or api_key.strip() == "":
                return {"api_key": "", "api_base": api_base}, "No API Key provided."
            
            return {"api_key": api_key, "api_base": api_base}, "API Key added."

        @self.vizro_app.dash.callback(
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
        # Add callback to initialize messages if empty
        @self.vizro_app.dash.callback(
            Output(f"{self.id}-messages", "data"),
            Input(f"{self.id}-messages", "data"),
        )
        def initialize_messages(current_messages):
            """Initialize messages if they don't exist."""
            if not current_messages:
                print(f"Initializing messages for {self.id}")  # Debug log
                return json.dumps([{"role": "assistant", "content": "Hello! How can I help you today?"}])
            print(f"Messages already exist for {self.id}: {current_messages}")  # Debug log
            return current_messages

        # Add callback to update chat history display
        @self.vizro_app.dash.callback(
            Output(f"{self.id}-history", "children"),
            Input(f"{self.id}-messages", "data"),
        )
        def update_chat_history(messages_json):
            """Update the chat history display from stored messages."""
            if not messages_json:
                return []
            
            try:
                # Only render messages when there's no chat history displayed yet
                history_div = html.Div(id=f"{self.id}-history")
                if not history_div.children:
                    messages = json.loads(messages_json)
                    chat_elements = []
                    
                    for msg in messages:
                        is_user = msg["role"] == "user"
                        chat_elements.append(
                            html.Div(
                                msg["content"],
                                style={
                                    **MESSAGE_STYLE,
                                    "borderLeft": f"2px solid {'#00b4ff' if is_user else '#aaa9ba'}",
                                }
                            )
                        )
                    
                    return chat_elements
                return dash.no_update
            except Exception as e:
                print(f"Error updating chat history: {e}")
                return []

        # Modify the streaming callback JavaScript
        self.vizro_app.dash.clientside_callback(
            """
            function(n_clicks, n_submit, value, messages, api_settings) {
                if (n_clicks === null && n_submit === null) return [messages, "", null];
                if ((!n_clicks && !n_submit) || !messages) return [messages, value, null];
                if (!value || !value.trim()) return [messages, "", null];

                try {
                    const messages_array = JSON.parse(messages);
                    const userMessage = {"role": "user", "content": value.trim()};

                    const triggeredId = window.dash_clientside.callback_context.triggered[0].prop_id;
                    const componentId = triggeredId.split('-')[0];
                    const chatHistory = document.getElementById(`${componentId}-history`);

                    // Create a temporary div for the user message
                    const tempUserDiv = document.createElement('div');
                    tempUserDiv.style.backgroundColor = "var(--mantine-color-dark-light-hover)";
                    tempUserDiv.style.color = "var(--text-primary)";
                    tempUserDiv.style.padding = "10px 15px";
                    tempUserDiv.style.maxWidth = "70%";
                    tempUserDiv.style.marginLeft = "0";
                    tempUserDiv.style.marginRight = "auto";
                    tempUserDiv.style.marginBottom = "15px";
                    tempUserDiv.style.whiteSpace = "pre-wrap";
                    tempUserDiv.style.wordBreak = "break-word";
                    tempUserDiv.style.width = "fit-content";
                    tempUserDiv.style.minWidth = "100px";
                    tempUserDiv.style.lineHeight = "1.25";
                    tempUserDiv.style.letterSpacing = "0.2px";
                    tempUserDiv.style.borderLeft = "2px solid #00b4ff";
                    tempUserDiv.textContent = value.trim();

                    if (chatHistory) {
                        chatHistory.appendChild(tempUserDiv);
                        chatHistory.scrollTop = chatHistory.scrollHeight;
                    }

                    let resolvePromise;
                    const updatePromise = new Promise((resolve) => {
                        resolvePromise = resolve;
                    });

                    // Start streaming after a short delay to allow the UI to update
                    setTimeout(() => {
                        // Create a temporary container for the streaming message
                        const tempContainer = document.createElement('div');
                        tempContainer.style.backgroundColor = "var(--mantine-color-dark-light-hover)";
                        tempContainer.style.color = "var(--text-primary)";
                        tempContainer.style.padding = "10px 15px";
                        tempContainer.style.maxWidth = "70%";
                        tempContainer.style.marginLeft = "0";
                        tempContainer.style.marginRight = "auto";
                        tempContainer.style.marginBottom = "15px";
                        tempContainer.style.whiteSpace = "pre-wrap";
                        tempContainer.style.wordBreak = "break-word";
                        tempContainer.style.width = "fit-content";
                        tempContainer.style.minWidth = "100px";
                        tempContainer.style.lineHeight = "1.25";
                        tempContainer.style.letterSpacing = "0.2px";
                        tempContainer.style.borderLeft = "2px solid #aaa9ba";
                        tempContainer.setAttribute('data-streaming', 'true');

                        if (chatHistory) {
                            chatHistory.appendChild(tempContainer);
                            chatHistory.scrollTop = chatHistory.scrollHeight;
                        }

                        // Start streaming
                        fetch(`/streaming-${componentId}`, {
                            method: "POST",
                            headers: {"Content-Type": "application/json"},
                            body: JSON.stringify({
                                prompt: value.trim(),
                                chat_history: JSON.stringify(messages_array),  // Send current messages without new user message
                                api_settings: api_settings
                            }),
                        }).then(response => {
                            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                            const reader = response.body.getReader();
                            const decoder = new TextDecoder();
                            let text = "";

                            function readChunk() {
                                reader.read().then(({done, value}) => {
                                    if (done) {
                                        const assistantMessage = {"role": "assistant", "content": text.trim()};
                                        
                                        // Remove both temporary divs
                                        if (tempUserDiv && tempUserDiv.parentNode) {
                                            tempUserDiv.parentNode.removeChild(tempUserDiv);
                                        }
                                        if (tempContainer && tempContainer.parentNode) {
                                            tempContainer.parentNode.removeChild(tempContainer);
                                        }
                                        
                                        // Keep the temporary divs and just update the messages array
                                        // for persistence (won't cause re-render)
                                        messages_array.push(userMessage);
                                        messages_array.push(assistantMessage);
                                        resolvePromise([
                                            JSON.stringify(messages_array),
                                            "",
                                            null
                                        ]);
                                        return;
                                    }

                                    const chunk = decoder.decode(value);
                                    text += chunk;
                                    if (tempContainer) {
                                        tempContainer.textContent = text;
                                        chatHistory.scrollTop = chatHistory.scrollHeight;
                                    }

                                    readChunk();
                                });
                            }

                            readChunk();
                        }).catch(error => {
                            console.error("Streaming error:", error);
                            if (tempContainer) {
                                tempContainer.textContent = "Error: Could not get response from server.";
                            }
                            resolvePromise([JSON.stringify(messages_array), "", null]);
                        });
                    }, 50);  // Small delay to ensure smooth UI update

                    // Return the promise that will resolve with the final update
                    return updatePromise;
                } catch (error) {
                    console.error("Error:", error);
                    return [messages, value, null];
                }
            }
            """,
            [
                Output(f"{self.id}-messages", "data", allow_duplicate=True),
                Output(f"{self.id}-input", "value", allow_duplicate=True),
                Output(f"{self.id}-stream-complete", "data"),
            ],
            [
                Input(f"{self.id}-submit", "n_clicks"),
                Input(f"{self.id}-input", "n_submit"),
            ],
            [
                State(f"{self.id}-input", "value"),
                State(f"{self.id}-messages", "data"),
                State(f"{self.id}-api-settings", "data"),
            ],
            prevent_initial_call='initial_duplicate',
        )

    @_log_call
    def build(self):
        """Build the complete chat component UI."""
        # Create data stores
        stores = self._build_data_stores()
        
        # Build the chat interface components
        settings_icon = self._build_settings_icon()
        settings_offcanvas = self._build_settings_offcanvas()
        chat_interface = self._build_chat_interface()
        
        # Assemble the complete component
        chat_component = html.Div(
            stores + [
                settings_icon,
                settings_offcanvas,
                chat_interface
            ],
            style={
                "width": "90%",
                "height": "90%",
                "padding": "20px",
                "display": "flex",
            },
        )

        return chat_component
    
    def _build_data_stores(self):
        """Build the data store components for the chat."""
        return [
            dcc.Store(
                id=f"{self.id}-api-settings",
                storage_type='session'
            ),
            dcc.Store(
                id=f"{self.id}-messages",
                storage_type='session'
            ),
            dcc.Store(  # Modified store for handling streaming completion
                id=f"{self.id}-stream-complete",
                storage_type='memory',
                data=None,  # Initialize with None
            ),
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
                    style=SETTINGS_ICON_STYLE
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
                            placeholder="(optional) API base",
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
                # Add a loading component to handle initial load
                dbc.Spinner(
                html.Div(
                    id=f"{self.id}-history",
                    style=CHAT_HISTORY_STYLE,
                    ),
                    color="primary",
                ),
                html.Div(
                    [
                        dbc.InputGroup(
                            [
                                dbc.Textarea(
                                    id=f"{self.id}-input",
                                    placeholder=self.input_placeholder,
                                    style={
                                        "height": self.input_height,
                                        "resize": "none",
                                    },
                                    n_submit=0,
                                ),
                                dbc.Button(
                                    self.button_text,
                                    outline=True,
                                    color="secondary",
                                    className="me-1",
                                    id=f"{self.id}-submit",
                                    style={
                                        "height": self.input_height,
                                    },
                                ),
                            ]
                        )
                    ],
                    style=CHAT_INPUT_CONTAINER_STYLE,
                ),
            ],
            style=CHAT_CONTAINER_STYLE,
        )
