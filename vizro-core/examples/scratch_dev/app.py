import base64
from typing import Annotated, Optional, Any, Literal
import json

import dash
import plotly
from dash import html, dcc, callback, Output, Input, State, Patch, clientside_callback, no_update
import dash_mantine_components as dmc
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from dash_extensions import SSE
from dash_extensions.streaming import sse_message, sse_options
from dotenv import load_dotenv
from flask import Response, request
from openai import OpenAI, BaseModel
from pydantic import Tag, Field, model_validator
import anthropic
import pandas as pd

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions._abstract_action import _AbstractAction
from vizro.managers import model_manager
from vizro.models import VizroBaseModel
from vizro.models._models_utils import make_actions_chain
from vizro.models.types import ActionType
from vizro.models._models_utils import _log_call


load_dotenv()

# -------------------- Style Constants --------------------
# Common style values for consistency
BORDER_RADIUS = "0px"
# Spacing from design system
SPACING_SM = "8px"  # Small gaps
SPACING_MD = "12px"  # Medium gaps (was 15px, updated to design spec)
SPACING_LG = "24px"  # Large gaps (was 20px, updated to design spec)

# Typography from design system
FONT_FAMILY = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
FONT_SIZE_EDITORIAL = "16px"  # Body editorial 01 - for main message content
FONT_SIZE_HELP = "12px"  # Help text
LINE_HEIGHT_EDITORIAL = "24px"  # 150% of 16px
LETTER_SPACING_EDITORIAL = "-0.002em"

COLOR_TEXT_PRIMARY = "var(--text-primary)"
COLOR_TEXT_SECONDARY = "var(--text-secondary)"

MAX_CHAT_WIDTH = "788px"  # from design system

# Plot dimensions - consistent width for all charts
PLOT_WIDTH = "600px"
PLOT_HEIGHT = "400px"

# Message bubble styling - aligned with design system
MESSAGE_BUBBLE = {
    "maxWidth": "100%",
    "paddingTop": "10px",
    "paddingBottom": "10px",
    "marginBottom": SPACING_MD,
    "borderRadius": BORDER_RADIUS,
    "fontFamily": FONT_FAMILY,  # Inter font from design
    "lineHeight": LINE_HEIGHT_EDITORIAL,  # 24px from design (was 1.65rem)
    "letterSpacing": LETTER_SPACING_EDITORIAL,  # -0.002em from design (was 0.2px)
    "whiteSpace": "pre-wrap",
    "wordBreak": "break-word",
    "display": "inline-block",  # Allow natural sizing based on content
    "color": COLOR_TEXT_PRIMARY,  # rgba(20, 23, 33, 0.88) from design
}

# User message specific styling
USER_MESSAGE_STYLE = {
    **MESSAGE_BUBBLE,
    "backgroundColor": "var(--surfaces-bg-card)",
    "marginLeft": "0",  # Align to the left
    "marginRight": "auto",
    "paddingLeft": "15px",
    "paddingRight": "15px",
}

# Assistant message specific styling
ASSISTANT_MESSAGE_STYLE = {
    **MESSAGE_BUBBLE,
    "backgroundColor": "var(--bs-body-bg)",
    "marginLeft": "0",  # Align to the left
    "marginRight": "auto",
}

# Container styles
HISTORY_CONTAINER = {
    "minWidth": MAX_CHAT_WIDTH,
    "maxWidth": MAX_CHAT_WIDTH,
    "width": "100%",
    "paddingBottom": SPACING_LG,
    "paddingLeft": "5px",
    "paddingRight": "5px",
    "overflowY": "auto",
    "overflowX": "hidden",  # Prevent horizontal scroll
    "height": "100%",
    "display": "flex",
    "flexDirection": "column",
    "margin": "0 auto",  # Center the container
}

HISTORY_SECTION = {
    "display": "flex",
    "justifyContent": "center",
    "width": "100%",
    "flex": "1",
    "overflow": "hidden",
    "paddingTop": SPACING_MD,
}

INPUT_SECTION = {
    "display": "flex",
    "justifyContent": "center",
    "width": "100%",
    "marginTop": "auto",
    "paddingBottom": SPACING_LG,
    "paddingLeft": "10px",
    "paddingRight": "10px",
}

# -------------------- Base Classes --------------------


class StreamingRequest(BaseModel):
    """Request payload for streaming chat endpoint."""

    prompt: str
    messages: Any  # List of message dicts with 'role' and 'content' keys


class _BaseChatAction(_AbstractAction):
    """Base class with shared chat functionality."""

    parent_id: str = Field(description="ID of the parent Chat component.")
    prompt: str = Field(default_factory=lambda data: f"{data['parent_id']}-chat-input.value")
    messages: str = Field(default_factory=lambda data: f"{data['parent_id']}-store.data")

    @_log_call
    def pre_build(self):
        if self.parent_id != self._parent_model.id:
            raise ValueError(
                f"{self.__class__.__name__} has parent_id='{self.parent_id}' but is attached to "
                f"Chat component with id='{self._parent_model.id}'. "
                f"These must match. Fix: use parent_id='{self._parent_model.id}'"
            )

        self._setup_chat_callbacks()
        self._setup_loading_indicator()
        self._setup_file_upload_callbacks()

    def _setup_streaming_callbacks(self):
        """SSE streaming decoding and accumulation."""
        clientside_callback(
            """
            function(animatedText, existingChildren, storeData) {
                const CHUNK_DELIMITER = '|END|';
                const STREAM_DONE_SIGNAL = '[DONE]';

                // Helper: Decode base64 chunk to UTF-8 text
                function decodeChunk(chunk) {
                    try {
                        const binaryString = atob(chunk);
                        const bytes = new Uint8Array(binaryString.length);
                        for (let i = 0; i < binaryString.length; i++) {
                            bytes[i] = binaryString.charCodeAt(i);
                        }
                        return new TextDecoder('utf-8').decode(bytes);
                    }
                    catch (e) {
                        console.warn('Failed to decode chunk:', e);
                        return '';
                    }
                }

                // Helper: Get message content from simple structure [role, content]
                function getMessageContent(msg) {
                    if (msg?.props?.children && Array.isArray(msg.props.children) && msg.props.children.length >= 2) {
                        return msg.props.children[1]?.props?.children || '';
                    }
                    return '';
                }

                // Helper: Set message content in simple structure [role, content]
                function setMessageContent(msg, content) {
                    if (msg?.props?.children && Array.isArray(msg.props.children) && msg.props.children.length >= 2) {
                        msg.props.children[1].props.children = content;
                    }
                }

                // Handle stream completion
                if (!animatedText || animatedText === STREAM_DONE_SIGNAL) {
                    window.lastProcessedChunkCount = 0;
                    return [existingChildren, window.dash_clientside.no_update];
                }

                const newChildren = [...(existingChildren || [])];
                const newData = [...(storeData || [])];
                const lastMsg = newChildren[newChildren.length - 1];
                const currentContent = getMessageContent(lastMsg);

                // Reset counter for new messages
                if (!window.lastProcessedChunkCount || currentContent === '') {
                    window.lastProcessedChunkCount = 0;
                }

                // Process new chunks only
                const chunks = animatedText.split(CHUNK_DELIMITER).slice(0, -1);
                const newText = chunks.slice(window.lastProcessedChunkCount)
                    .filter(Boolean)
                    .map(decodeChunk)
                    .join('');

                window.lastProcessedChunkCount = chunks.length;

                // Update message content if new text received
                if (newText) {
                    setMessageContent(lastMsg, currentContent + newText);

                    // Update store data for assistant messages
                    const lastStoreMsg = newData[newData.length - 1];
                    if (lastStoreMsg?.role === 'assistant') {
                        // During streaming, accumulate in content_json as serialized string
                        const existingContent = JSON.parse(lastStoreMsg.content_json || '""');
                        lastStoreMsg.content_json = JSON.stringify(existingContent + newText);
                    }
                }

                return [newChildren, newData];
            }
            """,
            [
                Output(f"{self.parent_id}-hidden-messages", "children", allow_duplicate=True),
                Output(f"{self.parent_id}-store", "data", allow_duplicate=True),
            ],
            Input(f"{self.parent_id}-sse", "animation"),
            [State(f"{self.parent_id}-hidden-messages", "children"), State(f"{self.parent_id}-store", "data")],
            prevent_initial_call=True,
        )

    def _setup_streaming_endpoint(self):
        """Set up streaming endpoint for SSE."""
        CHUNK_DELIMITER = "|END|"

        @dash.get_app().server.route(
            f"/streaming-{self.parent_id}", methods=["POST"], endpoint=f"streaming_chat_{self.parent_id}"
        )
        def streaming_chat():
            req = StreamingRequest(**request.get_json())

            def event_stream():
                for chunk in self.generate_response(req.messages):
                    # Encode chunk as base64 to handle any special characters
                    encoded_chunk = base64.b64encode(chunk.encode("utf-8")).decode("utf-8")
                    # Need a robust delimiter for clientside parsing
                    yield sse_message(encoded_chunk + CHUNK_DELIMITER)

                # Send SSE completion signal
                yield sse_message()

            return Response(event_stream(), mimetype="text/event-stream")

    def _setup_chat_callbacks(self):
        """Set up generic chat UI callbacks."""

        # Clientside callback to parse markdown and render code blocks with syntax highlighting
        clientside_callback(
            """
            function(children) {
                const CODE_BLOCK_REGEX = /```(\\w+)?\\n([\\s\\S]*?)```/g;

                // Style constants
                const BORDER_RADIUS = "0px";
                const FONT_FAMILY = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";
                const FONT_SIZE_EDITORIAL = "16px";
                const LINE_HEIGHT_EDITORIAL = "24px";
                const LETTER_SPACING_EDITORIAL = "-0.002em";
                const SPACING_MD = "12px";

                const MESSAGE_BUBBLE = {
                    maxWidth: "100%",
                    paddingTop: "10px",
                    paddingBottom: "10px",
                    marginBottom: SPACING_MD,
                    borderRadius: BORDER_RADIUS,
                    fontFamily: FONT_FAMILY,
                    lineHeight: LINE_HEIGHT_EDITORIAL,
                    letterSpacing: LETTER_SPACING_EDITORIAL,
                    whiteSpace: "pre-wrap",
                    wordBreak: "break-word",
                    display: "inline-block",
                    color: "var(--text-primary)"
                };

                const USER_MESSAGE_STYLE = {
                    ...MESSAGE_BUBBLE,
                    backgroundColor: "var(--surfaces-bg-card)",
                    marginLeft: "0",
                    marginRight: "auto",
                    paddingLeft: "15px",
                    paddingRight: "15px"
                };

                const ASSISTANT_MESSAGE_STYLE = {
                    ...MESSAGE_BUBBLE,
                    backgroundColor: "var(--bs-body-bg)",
                    marginLeft: "0",
                    marginRight: "auto"
                };

                // Component factory helpers
                const createComponent = (type, namespace, props) => ({
                    type, namespace, props
                });

                const createMarkdown = (text) => createComponent(
                    "Markdown",
                    "dash_core_components",
                    {
                        children: text,
                        dangerously_allow_html: false,
                        style: { color: "inherit", fontSize: FONT_SIZE_EDITORIAL },
                        className: "assistant-markdown"
                    }
                );

                const createCodeHighlight = (code, language) => createComponent(
                    "CodeHighlight",
                    "dash_mantine_components",
                    {
                        code: code.trim(),
                        language: language || 'text',
                        withLineNumbers: false
                    }
                );

                const createDiv = (children, style) => createComponent(
                    "Div",
                    "dash_html_components",
                    { children, style }
                );

                // Parse content into markdown and code blocks
                function parseContent(content) {
                    const parts = [];
                    let lastIndex = 0;
                    let match;

                    CODE_BLOCK_REGEX.lastIndex = 0; // Reset regex state

                    while ((match = CODE_BLOCK_REGEX.exec(content)) !== null) {
                        const [_, language, code] = match;

                        // Add preceding text as markdown
                        if (match.index > lastIndex) {
                            const text = content.slice(lastIndex, match.index).trim();
                            if (text) parts.push(createMarkdown(text));
                        }

                        // Add code block
                        parts.push(createCodeHighlight(code, language));
                        lastIndex = CODE_BLOCK_REGEX.lastIndex;
                    }

                    // Add trailing text
                    const trailing = content.slice(lastIndex).trim();
                    if (trailing) parts.push(createMarkdown(trailing));

                    return parts;
                }

                // Main processing
                if (!children?.length) return [];

                return children.map(msg => {
                    // Skip if no props
                    if (!msg?.props?.children) return msg;

                    // Handle simple structure: [role, content]
                    if (Array.isArray(msg.props.children) && msg.props.children.length >= 2) {
                        const [roleDiv, contentDiv] = msg.props.children;
                        const role = roleDiv?.props?.children;
                        const content = contentDiv?.props?.children;

                        // Only process string content
                        if (typeof content !== 'string') return msg;

                        // Apply styling based on role
                        if (role === 'user') {
                            // User message: simple styled div with text
                            return createDiv(
                                createDiv(
                                    createDiv(content, { fontSize: FONT_SIZE_EDITORIAL }),
                                    USER_MESSAGE_STYLE
                                ),
                                { display: "flex", justifyContent: "flex-start", width: "100%" }
                            );
                        } else {
                            // Assistant message: parse for code blocks
                            if (/```/g.test(content)) {
                                // Has code blocks - parse and use CodeHighlight
                                const parts = parseContent(content);
                                if (parts.length > 0) {
                                    return createDiv(
                                        createDiv(
                                            createDiv(parts),
                                            ASSISTANT_MESSAGE_STYLE
                                        ),
                                        { display: "flex", justifyContent: "flex-start", width: "100%" }
                                    );
                                }
                            }
                            // No code blocks - use regular Markdown
                            return createDiv(
                                createDiv(
                                    createMarkdown(content),
                                    ASSISTANT_MESSAGE_STYLE
                                ),
                                { display: "flex", justifyContent: "flex-start", width: "100%" }
                            );
                        }
                    }

                    // Return unchanged if structure doesn't match
                    return msg;
                });
            }
            """,
            Output(f"{self.parent_id}-rendered-messages", "children"),
            Input(f"{self.parent_id}-hidden-messages", "children"),
            prevent_initial_call=True,
        )

        # Handle Enter key for submission (but allow Shift+Enter for new lines)
        clientside_callback(
            f"""
            function(value) {{
                // Add event listener for the chat input if not already added
                setTimeout(() => {{
                    const chatInput = document.getElementById('{self.parent_id}-chat-input');
                    if (chatInput && !chatInput.dataset.listenerAdded) {{
                        chatInput.dataset.listenerAdded = 'true';
                        chatInput.addEventListener('keydown', function(e) {{
                            if (e.key === 'Enter' && !e.shiftKey) {{
                                e.preventDefault();
                                const sendButton = document.getElementById('{self.parent_id}-send-button');
                                if (sendButton && chatInput.value.trim()) {{
                                    sendButton.click();
                                }}
                            }}
                        }});
                    }}
                }}, 100);

                return window.dash_clientside.no_update;
            }}
            """,
            Output(f"{self.parent_id}-chat-input", "id", allow_duplicate=True),  # Dummy output
            Input(f"{self.parent_id}-chat-input", "value"),
            prevent_initial_call=True,
        )

        # Horrible hack to restore chat history when you change page and return.
        page = model_manager._get_model_page(self)

        @callback(
            [
                Output(f"{self.parent_id}-hidden-messages", "children", allow_duplicate=True),
                Output(
                    "vizro_version", "children", allow_duplicate=True
                ),  # Extremely horrible hack we should change, just done here to make
                # sure callback triggers (must have prevent_initial_call=True).
                Output(f"{self.parent_id}-data-info", "children", allow_duplicate=True),
            ],
            Input(*page._action_triggers["__default__"].split(".")),
            [
                State(f"{self.parent_id}-store", "data"),
                State(f"{self.parent_id}-file-store", "data"),
            ],
            prevent_initial_call=True,
        )
        def on_page_load(_, store, files):
            html_messages = [self.message_to_html(message) for message in store]
            filenames = [f["filename"] for f in files] if files else []
            file_preview = self._create_file_preview(filenames) if filenames else ""
            return html_messages, dash.no_update, file_preview

    def _setup_file_upload_callbacks(self):
        @callback(
            Output(f"{self.parent_id}-file-store", "data"),
            Output(f"{self.parent_id}-data-info", "children"),
            Input(f"{self.parent_id}-upload", "contents"),
            State(f"{self.parent_id}-upload", "filename"),
            State(f"{self.parent_id}-file-store", "data"),
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

            return all_files, self._create_file_preview([f["filename"] for f in all_files])

        @callback(
            Output(f"{self.parent_id}-file-store", "data", allow_duplicate=True),
            Output(f"{self.parent_id}-data-info", "children", allow_duplicate=True),
            Input({"type": f"{self.parent_id}-remove-file", "index": dash.ALL}, "n_clicks"),
            State(f"{self.parent_id}-file-store", "data"),
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
                return files, self._create_file_preview([f["filename"] for f in files])

            return no_update, no_update

    def generate_response(self, messages):
        """Override to implement response generation.

        Args:
            messages: List of message dicts with 'role' and 'content_json' keys
                     (content is serialized JSON)

        Returns:
            dict: Always returns {"content_json": "..."} with serialized content
                  for consistent handling and persistence
        """
        raise NotImplementedError("Subclasses must implement generate_response()")

    def _create_file_preview(self, filenames: list[str]):
        """Create file preview UI component for multiple files.

        Args:
            filenames: List of filenames to display, or a single filename string for backwards compatibility.
        """
        file_items = []
        for i, filename in enumerate(filenames):
            file_items.append(
                dmc.Paper(
                    [
                        dmc.Group(
                            [
                                dmc.Text(
                                    filename,
                                    size="sm",
                                    fw=500,
                                    style={"maxWidth": "150px", "overflow": "hidden", "textOverflow": "ellipsis"},
                                ),
                                dmc.ActionIcon(
                                    DashIconify(icon="material-symbols:close", width=16),
                                    size="xs",
                                    variant="subtle",
                                    id={"type": f"{self.parent_id}-remove-file", "index": i},
                                    n_clicks=0,
                                ),
                            ],
                            justify="space-between",
                            style={"width": "100%"},
                        )
                    ],
                    p="xs",
                    radius="sm",
                    withBorder=True,
                    style={"backgroundColor": "var(--surfaces-bg-card)"},
                )
            )

        return html.Div(
            file_items,
            style={
                "display": "flex",
                "flexDirection": "row",
                "flexWrap": "nowrap",
                "gap": "8px",
                "maxWidth": "100%",
                "overflowX": "auto",
            },
        )

    def message_to_html(self, message):
        """Convert a message dict to HTML structure.

        Override this method for custom rendering logic.

        Args:
            message: Dict with 'role' and 'content_json' keys

        Returns:
            Dash HTML component
        """
        role = message["role"]
        content = json.loads(message["content_json"])

        if role == "user":
            return html.Div(
                html.Div(
                    html.Div(str(content) if content else "", style={"fontSize": FONT_SIZE_EDITORIAL}),
                    style=USER_MESSAGE_STYLE,
                ),
                style={"display": "flex", "justifyContent": "flex-start", "width": "100%"},
            )
        else:
            # Assistant message
            if isinstance(content, str):
                # Text: use structure for clientside markdown/code processing
                return html.Div(
                    [
                        html.Div("assistant", style={"display": "none"}),  # Hidden role marker
                        html.Div(content),  # Plain text for clientside to process
                    ]
                )
            else:
                # Component: render directly with styling
                return html.Div(
                    html.Div(content, style=ASSISTANT_MESSAGE_STYLE),
                    style={"display": "flex", "justifyContent": "flex-start", "width": "100%"},
                )

    def _setup_loading_indicator(self):
        """Set up loading indicator using a serverside callback.

        This callback triggers immediately on button click and:
        1. Adds user message and loading placeholder to hidden-messages (UI only)
        2. Clears the input

        Note: This doesn't update the store - that's handled by function().
        The loading placeholder gets replaced when the main action callback returns.
        """

        @callback(
            Output(f"{self.parent_id}-hidden-messages", "children", allow_duplicate=True),
            Output(f"{self.parent_id}-chat-input", "value", allow_duplicate=True),
            Input(f"{self.parent_id}-send-button", "n_clicks"),
            State(f"{self.parent_id}-chat-input", "value"),
            prevent_initial_call=True,
        )
        def update_with_user_input(_, prompt):
            """Handle immediate UI update when user sends a message."""
            if not prompt or not prompt.strip():
                raise PreventUpdate

            html_messages = Patch()

            # Add user message to display
            latest_input = {"role": "user", "content_json": json.dumps(prompt)}
            html_messages.append(self.message_to_html(latest_input))

            # Add a loading indicator as a temporary assistant message
            loading_msg = html.Div(
                html.Div(
                    dmc.Loader(size="sm", type="dots"),
                    style={
                        **ASSISTANT_MESSAGE_STYLE,
                        "display": "flex",
                        "alignItems": "center",
                        "padding": "16px",
                        "minHeight": "48px",
                    },
                ),
                style={"display": "flex", "justifyContent": "flex-start", "width": "100%"},
            )
            html_messages.append(loading_msg)

            # Clear input
            return html_messages, ""

class ChatAction(_BaseChatAction):
    """Non-streaming chat action. Subclasses must implement generate_response()."""

    type: Literal["chat_action"] = "chat_action"

    def function(self, prompt, messages):
        if not prompt or not prompt.strip():
            return [no_update] * len(self.outputs)

        latest_input = {"role": "user", "content_json": json.dumps(prompt)}
        messages.append(latest_input)

        store = Patch()
        store.append(latest_input)

        result = self.generate_response(messages)
        latest_output = {"role": "assistant", **result}
        store.append(latest_output)

        html_messages = [self.message_to_html(msg) for msg in messages]
        html_messages.append(self.message_to_html(latest_output))

        return [store, html_messages, no_update]

    @property
    def outputs(self):
        return [
            f"{self.parent_id}-store.data",
            f"{self.parent_id}-hidden-messages.children",
            f"{self.parent_id}-chat-input.value",
        ]


class StreamingChatAction(_BaseChatAction):
    """Streaming chat action. Subclasses must implement generate_stream()."""

    type: Literal["streaming_chat_action"] = "streaming_chat_action"

    @_log_call
    def pre_build(self):
        super().pre_build()
        self._setup_streaming_callbacks()
        self._setup_streaming_endpoint()

    def generate_response(self, messages):
        """Override to implement streaming response.

        Args:
            messages: List of message dicts with 'role' and 'content_json' keys
                     (content is serialized JSON)

        Yields:
            str: Text chunks to stream
        """
        raise NotImplementedError("Subclasses must implement generate_response()")

    def function(self, prompt, messages):
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

        return [
            store,
            html_messages,
            no_update,
            f"/streaming-{self.parent_id}",
            sse_options(StreamingRequest(prompt=prompt, messages=messages)),
        ]

    @property
    def outputs(self):
        return [
            f"{self.parent_id}-store.data",
            f"{self.parent_id}-hidden-messages.children",
            f"{self.parent_id}-chat-input.value",
            f"{self.parent_id}-sse.url",
            f"{self.parent_id}-sse.options",
        ]


# -------------------- Example Chat Actions --------------------

# HOW TO CREATE A CHAT ACTION:
#
# Both ChatAction and StreamingChatAction use the same method name: generate_response()
# The difference is in what the method returns/yields.
#
# For non-streaming: inherit from ChatAction and implement generate_response()
#   - Returns {"content_json": json.dumps(...)} with text or Dash components
#   - Examples: simple_echo, mixed_content, openai_chat
#
# For streaming: inherit from StreamingChatAction and implement generate_response()
#   - Yields text chunks (generator/iterator)
#   - Examples: openai_streaming_chat, anthropic_chat


class openai_chat(ChatAction):
    """OpenAI non-streaming chat implementation."""

    type: Literal["openai_chat"] = "openai_chat"
    model: str = "gpt-4.1-nano"

    @property
    def client(self):
        return OpenAI()

    def generate_response(self, messages):
        """Handle non-streaming response from OpenAI."""
        api_messages = [{"role": msg["role"], "content": json.loads(msg["content_json"])} for msg in messages]
        response = self.client.responses.create(
            model=self.model,
            input=api_messages,
            instructions="Be polite and creative.",
            store=False,
        )
        return {"content_json": json.dumps(response.output_text)}


class openai_streaming_chat(StreamingChatAction):
    """OpenAI streaming chat implementation."""

    type: Literal["openai_streaming_chat"] = "openai_streaming_chat"
    model: str = "gpt-4.1-nano"

    @property
    def client(self):
        return OpenAI()

    def generate_response(self, messages):
        """Handle streaming response from OpenAI."""
        api_messages = [{"role": msg["role"], "content": json.loads(msg["content_json"])} for msg in messages]
        response = self.client.responses.create(
            model=self.model,
            input=api_messages,
            instructions="Be polite and creative.",
            store=False,
            stream=True,
        )

        for event in response:
            if event.type == "response.output_text.delta":
                yield event.delta


# Initialize Anthropic client once at module level
# Uses ANTHROPIC_API_KEY environment variable
anthropic_client = anthropic.Anthropic()


class anthropic_chat(StreamingChatAction):
    """Streaming implementation for Anthropic Claude chat."""

    type: Literal["anthropic_chat"] = "anthropic_chat"
    model: str = "claude-haiku-4-5-20251001"

    def generate_response(self, messages):
        """Generate streaming response from Anthropic Claude.

        Args:
            messages: List of message dicts with 'role' and 'content_json' keys

        Yields:
            str: Text chunks from Claude's response
        """
        api_messages = [{"role": msg["role"], "content": json.loads(msg["content_json"])} for msg in messages]
        with anthropic_client.messages.stream(
            model=self.model,
            max_tokens=1024,
            messages=api_messages,
        ) as stream:
            for text in stream.text_stream:
                yield text


class simple_echo(ChatAction):
    """Simple echo chat."""

    type: Literal["simple_echo"] = "simple_echo"

    def generate_response(self, messages):
        last_message = json.loads(messages[-1]["content_json"]) if messages else ""
        content = f"You said: {last_message}"
        return {"content_json": json.dumps(content)}


class mixed_content(ChatAction):
    """Simple example showing different content types: text, chart, and image."""

    type: Literal["mixed_content"] = "mixed_content"

    def generate_response(self, messages):
        """Returns serialized component structure as JSON."""
        prompt = json.loads(messages[-1]["content_json"]) if messages else ""

        fig = px.scatter(
            px.data.iris(),
            x="sepal_width",
            y="sepal_length",
            color="species",
            title="Iris Dataset",
            height=400,
        )

        content = html.Div(
            [
                dcc.Markdown(f"""
**You said:** "{prompt}"

This example demonstrates rendering different content types:
            """),
                dmc.Image(
                    radius="md",
                    h=200,
                    w="auto",
                    fit="contain",
                    src="https://raw.githubusercontent.com/mantinedev/mantine/master/.demo/images/bg-9.png",
                    style={"marginTop": "20px"},
                ),
                dcc.Graph(figure=fig, style={"marginTop": "20px"}),
            ]
        )

        return {"content_json": json.dumps(content, cls=plotly.utils.PlotlyJSONEncoder)}


# Example of using VizroAI to generate plots from natural language
class vizro_ai_chat(ChatAction):
    """Generate data visualizations using natural language with VizroAI."""

    type: Literal["vizro_ai_chat"] = "vizro_ai_chat"
    uploaded_files: str = Field(default_factory=lambda data: f"{data['parent_id']}-file-store.data")

    def function(self, prompt, messages, uploaded_files=None):
        """Override function to handle uploaded data parameter."""
        if not prompt or not prompt.strip():
            return [no_update] * len(self.outputs)

        latest_input = {"role": "user", "content_json": json.dumps(prompt)}
        messages.append(latest_input)

        store = Patch()
        store.append(latest_input)

        result = self.generate_response(messages, uploaded_files)
        latest_output = {"role": "assistant", **result}
        store.append(latest_output)

        html_messages = [self.message_to_html(msg) for msg in messages]
        html_messages.append(self.message_to_html(latest_output))

        return [store, html_messages, no_update]

    def generate_response(self, messages, uploaded_files=None):
        """Generate data visualization using VizroAI.

        Returns dict with serialized content for persistence.
        """
        from vizro_ai import VizroAI
        from langchain_openai import ChatOpenAI
        import io

        prompt = json.loads(messages[-1]["content_json"]) if messages else ""

        if not uploaded_files:
            content = html.P("Please upload a data file first!", style={"color": "#1890ff"})
            return {"content_json": json.dumps(content, cls=plotly.utils.PlotlyJSONEncoder)}

        # Get the first uploaded file
        uploaded_data = uploaded_files[0]["content"]
        uploaded_filename = uploaded_files[0]["filename"]

        # Parse the raw file contents (base64 encoded from dcc.Upload)
        try:
            content_type, content_string = uploaded_data.split(",")
            decoded = base64.b64decode(content_string)

            if uploaded_filename and uploaded_filename.endswith(".csv"):
                df = pd.read_csv(io.BytesIO(decoded))
            elif uploaded_filename and uploaded_filename.endswith((".xls", ".xlsx")):
                df = pd.read_excel(io.BytesIO(decoded))
            else:
                content = html.P(
                    f"Unsupported file type: {uploaded_filename}. Please upload CSV or Excel files.",
                    style={"color": "red"},
                )
                return {"content_json": json.dumps(content, cls=plotly.utils.PlotlyJSONEncoder)}
        except Exception as e:
            content = html.P(f"Error parsing file: {str(e)}", style={"color": "red"})
            return {"content_json": json.dumps(content, cls=plotly.utils.PlotlyJSONEncoder)}

        # Generate plot with VizroAI
        try:
            llm = ChatOpenAI(model_name="gpt-4o-mini")
            vizro_ai = VizroAI(model=llm)
            ai_outputs = vizro_ai.plot(df, prompt, return_elements=True)
            figure = ai_outputs.get_fig_object(data_frame=df, vizro=False)

            content = html.Div(
                [
                    dcc.Graph(figure=figure, style={"height": PLOT_HEIGHT, "width": PLOT_WIDTH}),
                    html.Details(
                        [
                            html.Summary(
                                "View generated code", style={"cursor": "pointer", "color": COLOR_TEXT_SECONDARY}
                            ),
                            dmc.CodeHighlight(
                                code=ai_outputs.code,
                                language="python",
                                withCopyButton=True,
                            ),
                        ],
                        style={"marginTop": "10px", "width": PLOT_WIDTH},
                    ),
                ],
                style={"width": PLOT_WIDTH},
            )

            return {"content_json": json.dumps(content, cls=plotly.utils.PlotlyJSONEncoder)}

        except Exception as e:
            error_msg = f"Error generating visualization: {str(e)}"
            content = html.P(error_msg, style={"color": "red"})
            return {"content_json": json.dumps(content, cls=plotly.utils.PlotlyJSONEncoder)}


class openai_vision_chat(ChatAction):
    """OpenAI Vision chat for analyzing images with text prompts.

    Uses the OpenAI responses API with input_image content type for vision capabilities.
    Supports multiple image uploads with a text prompt.
    """

    type: Literal["openai_vision_chat"] = "openai_vision_chat"
    model: str = "gpt-4.1-nano"
    uploaded_files: str = Field(default_factory=lambda data: f"{data['parent_id']}-file-store.data")

    @property
    def client(self):
        return OpenAI()

    def function(self, prompt, messages, uploaded_files=None):
        """Override function to handle uploaded images."""
        if not prompt or not prompt.strip():
            return [no_update] * len(self.outputs)

        latest_input = {"role": "user", "content_json": json.dumps(prompt)}
        messages.append(latest_input)

        store = Patch()
        store.append(latest_input)

        result = self.generate_response(messages, uploaded_files)
        latest_output = {"role": "assistant", **result}
        store.append(latest_output)

        html_messages = [self.message_to_html(msg) for msg in messages]
        html_messages.append(self.message_to_html(latest_output))

        return [store, html_messages, no_update]

    def generate_response(self, messages, uploaded_files=None):
        """Generate response using OpenAI Vision API with images.

        Builds content array with input_text and input_image types for OpenAI responses API.
        """
        prompt = json.loads(messages[-1]["content_json"]) if messages else ""

        content = [{"type": "input_text", "text": prompt}]

        if uploaded_files:
            for file_info in uploaded_files:
                data = file_info["content"]
                filename = file_info["filename"]

                is_image = any(filename.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif", ".webp"])

                if is_image:
                    # data is already base64 encoded from dcc.Upload (format: "data:image/png;base64,...")
                    content.append(
                        {
                            "type": "input_image",
                            "image_url": data,  # Pass the full data URL
                        }
                    )

        # Build API messages
        api_messages = []
        for msg in messages[:-1]:  # Exclude the last message since we'll add it with images
            api_messages.append({"role": msg["role"], "content": json.loads(msg["content_json"])})

        # Add the current message with images
        api_messages.append({"role": "user", "content": content})

        try:
            response = self.client.responses.create(
                model=self.model,
                input=api_messages,
                instructions="You are a helpful assistant that can analyze images and answer questions about them.",
                store=False,
            )

            response_text = response.output_text
            return {"content_json": json.dumps(response_text)}

        except Exception as e:
            error_msg = f"Error calling OpenAI Vision API: {str(e)}"
            content = html.P(error_msg, style={"color": "red"})
            return {"content_json": json.dumps(content, cls=plotly.utils.PlotlyJSONEncoder)}


# -------------------- Chat Component --------------------


class Chat(VizroBaseModel):
    type: Literal["chat"] = "chat"
    actions: list[ActionType] = []
    placeholder: str = "How can I help you?"
    file_upload: bool = False

    # This is how you make a new component a trigger of an action in the new system.
    _make_actions_chain = model_validator(mode="after")(make_actions_chain)

    @property
    def _action_triggers(self):
        return {"__default__": f"{self.id}-send-button.n_clicks"}

    def _build_upload_stores(self):
        """Build stores for file upload (always rendered for consistent callbacks)."""
        return [dcc.Store(id=f"{self.id}-file-store", storage_type="session")]

    def _build_input_area(self):
        """Build the input area with optional file upload button."""
        left_button = dcc.Upload(
            id=f"{self.id}-upload",
            children=dmc.ActionIcon(
                DashIconify(icon="material-symbols-light:attach-file-add", width=28, height=28),
                variant="subtle",
                color="grey",
                radius=BORDER_RADIUS,
                style={"width": "42px", "height": "42px"},
            ),
            style={"width": "fit-content", "display": "block" if self.file_upload else "none"},
            multiple=True,
        )

        # Build children list explicitly
        inner_children = []

        inner_children.append(html.Div(id=f"{self.id}-data-info", style={"marginBottom": "8px", "minHeight": "0px"}))

        # Textarea
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
                        "fontSize": FONT_SIZE_EDITORIAL,
                        "lineHeight": LINE_HEIGHT_EDITORIAL,
                        "color": COLOR_TEXT_PRIMARY,
                    }
                },
                style={"width": "100%"},
                value="",
            )
        )

        # Button row
        inner_children.append(
            html.Div(
                [
                    left_button,
                    dmc.ActionIcon(
                        DashIconify(icon="material-symbols-light:send-outline", width=38, height=38),
                        id=f"{self.id}-send-button",
                        variant="subtle",
                        color="grey",
                        n_clicks=0,
                        radius=BORDER_RADIUS,
                        style={"width": "42px", "height": "42px"},
                    ),
                ],
                style={"display": "flex", "justifyContent": "space-between", "width": "100%"},
            )
        )

        return html.Div(
            [
                html.Div(
                    inner_children,
                    style={"width": "100%", "maxWidth": MAX_CHAT_WIDTH},
                )
            ],
            style=INPUT_SECTION,
        )

    def build(self):
        return html.Div(
            [
                *self._build_upload_stores(),
                # Messages container
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(id=f"{self.id}-hidden-messages", children=[], style={"display": "none"}),
                                html.Div(id=f"{self.id}-rendered-messages", style=HISTORY_CONTAINER),
                            ],
                            id=f"{self.id}-chat-messages-container",
                        )
                    ],
                    style=HISTORY_SECTION,
                ),
                # Input area
                self._build_input_area(),
                # Store for conversation history
                dcc.Store(id=f"{self.id}-store", data=[], storage_type="session"),
                # Server-Sent Events for streaming support
                SSE(id=f"{self.id}-sse", concat=True, animate_chunk=10, animate_delay=5),
            ],
            style={"height": "100%", "width": "100%", "display": "flex", "flexDirection": "column"},
        )


vm.Page.add_type("components", Chat)
Chat.add_type("actions", Annotated[simple_echo, Tag("simple_echo")])
Chat.add_type("actions", Annotated[openai_chat, Tag("openai_chat")])
Chat.add_type("actions", Annotated[openai_streaming_chat, Tag("openai_streaming_chat")])
Chat.add_type("actions", Annotated[anthropic_chat, Tag("anthropic_chat")])
Chat.add_type("actions", Annotated[mixed_content, Tag("mixed_content")])
Chat.add_type("actions", Annotated[vizro_ai_chat, Tag("vizro_ai_chat")])
Chat.add_type("actions", Annotated[openai_vision_chat, Tag("openai_vision_chat")])


page = vm.Page(
    title="OpenAI Chat (Streaming)",
    components=[
        Chat(
            id="chat",
            actions=[openai_streaming_chat(parent_id="chat")],
        ),
    ],
)

page_nostream = vm.Page(
    title="OpenAI Chat (Non-Streaming)",
    components=[
        Chat(
            id="chat_nostream",
            actions=[openai_chat(parent_id="chat_nostream")],
        ),
    ],
)

page_echo = vm.Page(
    title="Simple Echo (No API Key)",
    components=[
        Chat(
            id="echo_chat",
            actions=[simple_echo(parent_id="echo_chat")],
        ),
    ],
)

page_2 = vm.Page(
    title="Mixed Content Chat",
    layout=vm.Grid(grid=[[0, 1, 1]]),
    components=[
        vm.Card(
            text="""
## Mixed Content Chat Demo

This example demonstrates that a chat response can include multiple content types:
- Markdown text with formatting
- Plotly charts
- Images

Type anything to see all content types rendered together!
"""
        ),
        Chat(id="mixed_chat", actions=[mixed_content(parent_id="mixed_chat")]),
    ],
)


page_anthropic = vm.Page(
    title="Claude Chat (Streaming)",
    layout=vm.Grid(grid=[[0], [1], [1], [1], [1]]),
    components=[
        vm.Card(
            text="""
## Anthropic Claude Chat - Streaming Example

**Note:** Set your `ANTHROPIC_API_KEY` environment variable to use this chat.
"""
        ),
        Chat(
            id="claude_chat",
            actions=[anthropic_chat(parent_id="claude_chat")],
        ),
    ],
)

page_vizro_ai = vm.Page(
    title="VizroAI Natural Language Charts",
    components=[
        Chat(
            id="vizro_ai_chat",
            file_upload=True,
            placeholder="Ask about your data...",
            actions=[vizro_ai_chat(parent_id="vizro_ai_chat")],
        ),
    ],
)

page_vision = vm.Page(
    title="OpenAI Vision Chat",
    layout=vm.Grid(grid=[[0], [1], [1], [1], [1]]),
    components=[
        vm.Card(
            text="""
## OpenAI Vision Chat - Image Analysis

Upload images and ask questions about them using OpenAI's vision capabilities.

**How to use:**
1. Click the attachment icon to upload one or more images
2. Type your question about the image(s)
3. Press send to get AI analysis

**Supported formats:** PNG, JPG, JPEG

**Model:** gpt-4.1-nano
"""
        ),
        Chat(
            id="vision_chat",
            file_upload=True,
            placeholder="Upload images and ask questions about them...",
            actions=[openai_vision_chat(parent_id="vision_chat", model="gpt-4.1-nano")],
        ),
    ],
)

dashboard = vm.Dashboard(
    pages=[page_echo, page, page_nostream, page_anthropic, page_2, page_vizro_ai, page_vision],
    theme="vizro_light",
    title="Vizro",
)

"""
Notes:
* How to handle different types? See options below.
* How can user easily write in chat function that plugs in?
* What stuff belongs in chat model vs. action function?

If get message history from server then need to hook into OPL for it. Could be whole separate action from OPL since
it doesn't involve Figures. Could do this with OpenAI but looks like it's potentially several requests due to
pagination.
If get message history from local then still need to populate somehow but not in OPL - could all be clientside and
outside actions. Probably easier overall.
Use previous_response_id stored locally so there's possibility in future of moving message population to serverside.

Can't use previous_response_id internally:
Previous response cannot be used for this organization due to Zero Data Retention.

Options for handling messages/prompt:
- messages as input property to do Dash component. Then don't need JSON duplication of it in store. Handle different
return types in Dash component rather than purely returning Dash components as here. Effectively this is done by
store_to_html callback in this example. Still easier to do this way than Dash component, regardless of whether it's
SS or CS callback. Could maybe have user write function that plugs in to do render of message? Conclusion: do the
Dash stuff SS by hand for response updating message output. Remember SS callbacks will have no problems at all for local use so not such a big compromise.
But need to work with streaming too so can't be done in callback - must be returned at same time as store,
so option 3 only realistic possibility.
- JSON store version that produces HTML version with SSCB. Ways to update this:
  - Option 1: prompt trigger updates store and triggers OpenAI callback at same time.
  - Option 2: prompt trigger updates store which then is trigger for OpenAI callback
  - Option 3: update HTML at same time as store. Then have duplicated data which is inelegant but not a big problem.
  Also makes on_page_load serverside - also not big problem. This is done here.

Things to improve in nearish future:
- need to specify chat_id manually
- way to plug into OPL if want to retrieve messages from server. Not urgent if do it all clientside. But now that
translation of store messages to html is SS, need to be able to do this. Options:
   - plug into OPL properly somehow
   - write another callback here that is triggered by {ON_PAGE_LOAD_ACTION_PREFIX}_{page.id}. Done here in hacky way
"""

if __name__ == "__main__":
    app = Vizro()
    app.build(dashboard).run(debug=False)
