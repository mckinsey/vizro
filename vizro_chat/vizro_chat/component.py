"""Vizro chat component."""

import json
from typing import ClassVar, Literal, Optional

import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html
from flask import Response, request
from pydantic import ConfigDict
from vizro._vizro import Vizro
from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call

from vizro_chat.processors import ChatProcessor, EchoProcessor


class VizroChatComponent(VizroBaseModel):
    """A chat component for Vizro dashboards."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    type: Literal["chat"] = "chat"
    id: str
    messages: ClassVar[list[dict[str, str]]] = [{"role": "assistant", "content": "Hello! How can I help you today?"}]
    input_placeholder: str = "Ask me a question..."
    input_height: str = "80px"
    button_text: str = "Send"
    vizro_app: Optional[Vizro] = None
    processor: ChatProcessor = EchoProcessor()  # Default to echo processor

    @_log_call
    def pre_build(self):
        """Register routes before building."""
        if self.vizro_app:
            # Register the streaming route
            @self.vizro_app.dash.server.route(
                f"/streaming-{self.id}", methods=["POST"], endpoint=f"streaming_chat_{self.id}"
            )
            def streaming_chat():
                try:
                    data = request.json
                    user_prompt = data["prompt"]
                    messages = json.loads(data.get("chat_history", "[]"))

                    def response_stream():
                        yield from self.processor.get_response(messages, user_prompt)

                    return Response(response_stream(), mimetype="text/event-stream")
                except Exception as e:
                    return {"error": str(e)}, 500

            # Register the clientside callback
            self.vizro_app.dash.clientside_callback(
                """
                (function() {
                    // Register the namespace if it doesn't exist
                    if (!window.dash_clientside) { window.dash_clientside = {}; }
                    if (!window.dash_clientside.chat) { window.dash_clientside.chat = {}; }

                    window.dash_clientside.chat.streaming_GPT = function(n_clicks, n_submit, value, messages) {
                        // Check if either button was clicked or Enter was pressed
                        if ((!n_clicks && !n_submit) || !value || !messages) {
                            return [messages, value];  // Return both values if no action
                        }

                        try {
                            const messages_json = JSON.stringify(JSON.parse(messages));

                            // Get component ID from the triggered input's ID
                            const triggeredId = window.dash_clientside.callback_context.triggered[0].prop_id;
                            const componentId = triggeredId.split('-')[0];

                            const chatHistory = document.getElementById(`${componentId}-history`);

                            // Add user message
                            const messages_array = JSON.parse(messages_json);
                            messages_array.push({"role": "user", "content": value});

                            // Create user message div first
                            const userDiv = document.createElement('div');
                            userDiv.textContent = value;
                            userDiv.style.backgroundColor = "var(--mantine-color-dark-light-hover)";
                            userDiv.style.color = "var(--text-primary)";
                            userDiv.style.padding = "10px 15px";
                            userDiv.style.maxWidth = "70%";
                            userDiv.style.marginRight = "auto";
                            userDiv.style.marginBottom = "15px";
                            userDiv.style.whiteSpace = "pre-wrap";
                            userDiv.style.wordBreak = "break-word";
                            userDiv.style.width = "fit-content";
                            userDiv.style.minWidth = "100px";
                            userDiv.style.lineHeight = "1.25";
                            userDiv.style.letterSpacing = "0.2px";
                            userDiv.style.borderLeft = "2px solid #00b4ff";

                            if (chatHistory) {
                                chatHistory.appendChild(userDiv);
                                chatHistory.scrollTop = chatHistory.scrollHeight;
                            }

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
                                    body: JSON.stringify({ // Send user prompt and chat history
                                        prompt: value,
                                        chat_history: JSON.stringify(messages_array.slice(0, -1))
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
                                                messages_array.push({"role": "assistant", "content": text.trim()});
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
                    };

                    return function(n_clicks, n_submit, value, messages) {
                        return window.dash_clientside.chat.streaming_GPT(n_clicks, n_submit, value, messages);
                    }
                })()
                """,
                [
                    Output(f"{self.id}-messages", "data", allow_duplicate=True),
                    Output(f"{self.id}-input", "value", allow_duplicate=True),
                ],
                [
                    Input(f"{self.id}-submit", "n_clicks"),
                    Input(f"{self.id}-input", "n_submit"),
                ],
                [
                    State(f"{self.id}-input", "value"),
                    State(f"{self.id}-messages", "data"),
                ],
                prevent_initial_call=True,
            )

    @_log_call
    def build(self):
        """Build the component UI."""
        # Build UI
        component = html.Div(
            [
                dcc.Store(id=f"{self.id}-messages", data=json.dumps(self.messages)),
                html.Div(
                    [
                        html.Div(
                            id=f"{self.id}-history",
                            style={
                                "overflowY": "auto",
                                "padding": "20px",
                                "gap": "10px",
                                "width": "100%",
                                "flex": "1 1 auto",
                                "display": "flex",
                                "flexDirection": "column",
                            },
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
                            style={
                                "padding": "20px",
                                "flex": "0 0 auto",
                            },
                        ),
                    ],
                    style={
                        "display": "flex",
                        "flexDirection": "column",
                        "height": "100%",
                        "width": "100%",
                        "backgroundColor": "var(--mantine-color-dark-light)",
                    },
                ),
            ],
            style={
                "width": "90%",
                "height": "90%",
                "padding": "20px",
                "display": "flex",
            },
        )
        return component
