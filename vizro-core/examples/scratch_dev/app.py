import base64
from typing import Annotated, Optional, Any, Literal
import json

import dash
import plotly
from dash import html, dcc, callback, Output, Input, State, Patch, clientside_callback, no_update
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc
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
from vizro.models.types import capture, ActionType


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


class ChatAction(_AbstractAction):
    """Base class for chat functionality with streaming and non-streaming support."""

    type: Literal["chat_action"] = "chat_action"
    chat_id: str
    prompt: str = Field(default_factory=lambda data: f"{data['chat_id']}-chat-input.value")
    messages: str = Field(default_factory=lambda data: f"{data['chat_id']}-store.data")
    stream: bool = True

    @model_validator(mode="after")
    def validate_required_methods(self):
        """Validate that subclasses implement the required generation methods.

        This enforces the contract:
        - If stream=True, generate_stream() must be implemented
        - If stream=False, generate_response() must be implemented

        Methods are considered "implemented" if they're defined in the subclass
        (not just inherited from ChatAction base class).
        """
        cls = self.__class__

        # Check if a method is actually implemented in the subclass (not just inherited from base)
        def is_implemented_in_subclass(method_name):
            # Get the method from the instance's class
            method = getattr(cls, method_name, None)
            if method is None:
                return False

            # Check if it's defined in ChatAction base class
            base_method = getattr(ChatAction, method_name, None)

            # If the method is the same object as the base class method, it's not overridden
            return method is not base_method

        if self.stream:
            if not is_implemented_in_subclass("generate_stream"):
                raise NotImplementedError(
                    f"{cls.__name__} has stream=True but does not implement generate_stream(). "
                    f"You must override generate_stream() to yield text chunks, even if you "
                    f"override function() for custom behavior."
                )
        else:
            if not is_implemented_in_subclass("generate_response"):
                raise NotImplementedError(
                    f"{cls.__name__} has stream=False but does not implement generate_response(). "
                    f"You must override generate_response() to return content (string or Dash component), or a tuple of (content, metadata), even if you "
                    f"override function() for custom behavior."
                )

        return self

    def pre_build(self):
        if self.stream:
            self._setup_streaming_callbacks()
            self._setup_streaming_endpoint()

        self._setup_chat_callbacks()

    # Now there are two data flows:
    #     1. SSE chunks → decoded and accumulated in hidden-messages div
    #     2. hidden-messages → parsed for markdown/code blocks → rendered-messages div

    # This separation allows the markdown parser to work nicely for:
    #     - Streaming messages (accumulated chunk by chunk)
    #     - Non-streaming messages (complete response)
    #     - Restored messages from history (on page load)
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
                    return [existingChildren, window.dash_clientside.no_update, ""];  // Clear loading
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

                return [newChildren, newData, window.dash_clientside.no_update];
            }
            """,
            [
                Output(f"{self.chat_id}-hidden-messages", "children", allow_duplicate=True),
                Output(f"{self.chat_id}-store", "data", allow_duplicate=True),
                Output(f"{self.chat_id}-loading-output", "children", allow_duplicate=True),
            ],
            Input(f"{self.chat_id}-sse", "animation"),
            [State(f"{self.chat_id}-hidden-messages", "children"), State(f"{self.chat_id}-store", "data")],
            prevent_initial_call=True,
        )

    def _setup_streaming_endpoint(self):
        """Set up streaming endpoint for SSE."""
        CHUNK_DELIMITER = "|END|"

        @dash.get_app().server.route(
            f"/streaming-{self.chat_id}", methods=["POST"], endpoint=f"streaming_chat_{self.chat_id}"
        )
        def streaming_chat():
            req = StreamingRequest(**request.get_json())

            def event_stream():
                for chunk in self.generate_stream(req.messages):
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
            Output(f"{self.chat_id}-rendered-messages", "children"),
            Input(f"{self.chat_id}-hidden-messages", "children"),
            prevent_initial_call=True,
        )

        @callback(
            Output(f"{self.chat_id}-store", "data", allow_duplicate=True),
            Output(f"{self.chat_id}-hidden-messages", "children", allow_duplicate=True),
            Output(f"{self.chat_id}-chat-input", "value"),  # Clear input after sending
            Output(f"{self.chat_id}-loading-output", "children"),  # Show loading indicator
            # input(*self._action_triggers["__default__"].split(".")), # Need to look up parent action triggers and
            # make sure it.
            Input(f"{self.chat_id}-send-button", "n_clicks"),
            State(*self.prompt.split(".")),
            prevent_initial_call=True,
        )
        def update_with_user_input(_, prompt):
            if not prompt:
                raise PreventUpdate

            store, html_messages = Patch(), Patch()
            latest_input = {"role": "user", "content_json": json.dumps(prompt)}
            store.append(latest_input)
            html_messages.append(self.message_to_html(latest_input))

            # Clear input and show loading
            # Add a loading indicator as a temporary assistant message
            loading_msg = html.Div(
                [
                    dmc.Paper(
                        [
                            dmc.Group(
                                [
                                    dmc.Loader(size="md", type="dots"),
                                ]
                            )
                        ],
                        p="md",
                        style={"backgroundColor": "var(--left-side-bg)"},
                    )
                ],
                style=ASSISTANT_MESSAGE_STYLE,
            )
            html_messages.append(loading_msg)

            return store, html_messages, "", ""

        # Handle Enter key for submission (but allow Shift+Enter for new lines)
        clientside_callback(
            f"""
            function(value) {{
                // Add event listener for the chat input if not already added
                setTimeout(() => {{
                    const chatInput = document.getElementById('{self.chat_id}-chat-input');
                    if (chatInput && !chatInput.dataset.listenerAdded) {{
                        chatInput.dataset.listenerAdded = 'true';
                        chatInput.addEventListener('keydown', function(e) {{
                            if (e.key === 'Enter' && !e.shiftKey) {{
                                e.preventDefault();
                                const sendButton = document.getElementById('{self.chat_id}-send-button');
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
            Output(f"{self.chat_id}-chat-input", "id", allow_duplicate=True),  # Dummy output
            Input(f"{self.chat_id}-chat-input", "value"),
            prevent_initial_call=True,
        )

        # Horrible hack to restore chat history when you change page and return.
        page = model_manager._get_model_page(self)

        @callback(
            Output(f"{self.chat_id}-hidden-messages", "children", allow_duplicate=True),
            Output(
                "vizro_version", "children", allow_duplicate=True
            ),  # Extremely horrible hack we should change, just done here to make
            # sure callback triggers (must have prevent_initial_call=True).
            Input(*page._action_triggers["__default__"].split(".")),
            State(f"{self.chat_id}-store", "data"),
            prevent_initial_call=True,
        )
        def on_page_load(_, store):
            return [self.message_to_html(message) for message in store], dash.no_update

    def generate_stream(self, messages):
        """Override to implement streaming response.

        Args:
            messages: List of message dicts with 'role' and 'content_json' keys
                     (content is serialized JSON)

        Yields:
            str: Text chunks to stream

        Note:
            This method MUST be implemented if stream=True, enforced by
            validate_required_methods(). Even if you override function() entirely,
            implement this method to satisfy the contract.
        """
        pass

    def generate_response(self, messages):
        """Override to implement non-streaming response.

        Args:
            messages: List of message dicts with 'role' and 'content_json' keys
                     (content is serialized JSON)

        Returns:
            dict: Always returns {"content_json": "..."} with serialized content
                  for consistent handling and persistence

        Note:
            This method MUST be implemented if stream=False, enforced by
            validate_required_methods(). Even if you override function() entirely
            (e.g., to handle extra parameters like uploaded_data), implement this
            method to satisfy the contract.
        """
        pass

    def function(self, prompt, messages):
        """Main action function called by Dash callback.

        This method can be overridden for special cases (e.g., to handle metadata,
        extra parameters like uploaded_data, or custom response processing).

        However, even when overriding this method, subclasses MUST still implement
        generate_stream() or generate_response() to satisfy the class contract.

        Args:
            prompt: User's input text
            messages: List of previous messages in conversation
        """
        # Need to repeat append here since this runs at same time as store update.
        # To be decided exactly what gets passed and how (prompt, latest_input, messages, etc.)
        latest_input = {"role": "user", "content_json": json.dumps(prompt)}
        messages.append(latest_input)

        if self.stream:
            store, html_messages = Patch(), Patch()

            # Remove the loading indicator and add placeholder for streaming
            html_messages[-1] = html.Div(style={"display": "none"})  # Hide loading

            placeholder_msg = {"role": "assistant", "content_json": json.dumps("")}
            store.append(placeholder_msg)
            html_messages.append(self.message_to_html(placeholder_msg))

            return [
                store,
                html_messages,
                f"/streaming-{self.chat_id}",
                sse_options(StreamingRequest(prompt=prompt, messages=messages)),
                "",  # Clear loading indicator
            ]
        else:
            result = self.generate_response(messages)
            latest_output = {"role": "assistant", **result}

            # Could do this without Patch and it would also work fine, but that would send more data across network than
            # is really necessary. Latest input has already been appended to both of these in update_with_user_input.
            store, html_messages = Patch(), Patch()

            # Remove the loading indicator and add actual response
            html_messages[-1] = html.Div(style={"display": "none"})  # Hide loading

            store.append(latest_output)
            html_messages.append(self.message_to_html(latest_output))
            return store, html_messages, ""  # Clear loading indicator

    def message_to_html(self, message):
        """Convert a message dict to HTML structure.

        All messages use serialized content_json format.
        """
        role = message["role"]
        content = json.loads(message["content_json"])

        # Return simple structure: role + content (let clientside callback handle styling)
        content_str = str(content) if content is not None else ""
        return html.Div(
            [
                html.Div(role, style={"display": "none"}),  # Hidden role marker
                html.Div(content_str),  # Plain text content
            ]
        )

    @property
    def outputs(self):
        if self.stream:
            return [
                f"{self.chat_id}-store.data",
                f"{self.chat_id}-hidden-messages.children",
                f"{self.chat_id}-sse.url",
                f"{self.chat_id}-sse.options",
                f"{self.chat_id}-loading-output.children",
            ]
        else:
            return [
                f"{self.chat_id}-store.data",
                f"{self.chat_id}-hidden-messages.children",
                f"{self.chat_id}-loading-output.children",
            ]


# -------------------- Example Chat Actions --------------------

# HOW TO CREATE A CHAT ACTION:
#
# All chat actions inherit from ChatAction and implement ONE or BOTH methods:
#
# 1. generate_stream(messages) - For streaming responses
#    - Yields text chunks
#    - Used when stream=True
#    - Example: anthropic_chat (streaming-only)
#
# 2. generate_response(messages) - For non-streaming responses
#    - Returns text (string) or Dash components (charts, images, etc.)
#    - Used when stream=False
#    - Examples: simple_echo, mixed_content
#
# 3. Both methods - For maximum flexibility
#    - Users can toggle stream=True/False
#    - Example: openai_chat


class openai_chat(ChatAction):
    """OpenAI chat implementation with both streaming and non-streaming support."""

    type: Literal["openai_chat"] = "openai_chat"
    model: str = "gpt-4.1-nano"
    api_key: Optional[str] = None  # Uses OPENAI_API_KEY env variable if not provided
    api_base: Optional[str] = None  # Uses OPENAI_BASE_URL env variable if not provided
    stream: bool = True
    messages: str = Field(default_factory=lambda data: f"{data['chat_id']}-store.data")

    # expose instructions and other stuff as fields.
    # But ultimately users will want to customize a lot of things like tools etc. so should be able to easily write
    # their own.
    # Could pass through arbitrary kwargs to create function? Should always be configurable via JSON.
    # https://platform.openai.com/docs/api-reference/responses
    # Good idea to make this specific to OpenAI responses API and have specific arguments we've picked out for OpenAI
    # class, create and how to handle response.
    @property
    def client(self):
        if not hasattr(self, "_client"):
            self._client = OpenAI(api_key=self.api_key, base_url=self.api_base)
        return self._client

    def generate_stream(self, messages):
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
            # Handle OpenAI-specific event types
            if event.type == "response.output_text.delta":
                yield event.delta

    def generate_response(self, messages):
        """Handle non-streaming response from OpenAI."""
        api_messages = [{"role": msg["role"], "content": json.loads(msg["content_json"])} for msg in messages]
        response = self.client.responses.create(
            model=self.model,
            input=api_messages,
            instructions="Be polite and creative.",
            store=False,
            stream=False,
        )
        return {"content_json": json.dumps(response.output_text)}


# Initialize Anthropic client once at module level
# Uses ANTHROPIC_API_KEY environment variable
anthropic_client = anthropic.Anthropic()


class anthropic_chat(ChatAction):
    """Streaming-only implementation for Anthropic Claude chat."""

    type: Literal["anthropic_chat"] = "anthropic_chat"
    model: str = "claude-haiku-4-5-20251001"
    stream: bool = True  # Streaming-only for this implementation
    messages: str = Field(default_factory=lambda data: f"{data['chat_id']}-store.data")

    def generate_stream(self, messages):
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
    stream: bool = False  # Non-streaming only

    def generate_response(self, messages):
        last_message = json.loads(messages[-1]["content_json"]) if messages else ""
        content = f"You said: {last_message}"
        return {"content_json": json.dumps(content)}


class mixed_content(ChatAction):
    """Simple example showing different content types: text, chart, and image."""

    type: Literal["mixed_content"] = "mixed_content"
    stream: bool = False  # Non-streaming only - components cannot be streamed
    messages: str = Field(default_factory=lambda data: f"{data['chat_id']}-store.data")

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

    def message_to_html(self, message):
        """Override to recreate components from serialized JSON."""
        content = json.loads(message["content_json"])

        return html.Div(
            html.Div(content, style=ASSISTANT_MESSAGE_STYLE),
            style={"display": "flex", "justifyContent": "flex-start", "width": "100%"},
        )


# Example of using VizroAI to generate plots from natural language
class vizro_ai_chat(ChatAction):
    """Generate data visualizations using natural language with VizroAI."""

    type: Literal["vizro_ai_chat"] = "vizro_ai_chat"
    stream: bool = False  # VizroAI returns complete plots, not streamable
    uploaded_data: str = Field(default_factory=lambda data: f"{data['chat_id']}-data-store.data")

    @property
    def inputs(self):
        """Define runtime inputs including uploaded data."""
        return [self.prompt, self.messages, self.uploaded_data]

    def function(self, prompt, messages, uploaded_data=None):
        """Override function to handle uploaded data parameter."""
        latest_input = {"role": "user", "content_json": json.dumps(prompt)}
        messages.append(latest_input)

        # Store uploaded_data temporarily so generate_response can access it
        self._uploaded_data = uploaded_data

        # Call generate_response directly (we know stream=False)
        result = self.generate_response(messages)
        latest_output = {"role": "assistant", **result}

        store, html_messages = Patch(), Patch()

        # Remove the loading indicator and add actual response
        html_messages[-1] = html.Div(style={"display": "none"})  # Hide loading

        store.append(latest_output)
        html_messages.append(self.message_to_html(latest_output))
        return store, html_messages, ""  # Clear loading indicator

    def generate_response(self, messages):
        """Required by ChatAction contract.

        Generates data visualization using VizroAI. Requires uploaded_data to be
        available (stored in self._uploaded_data by function()).
        Returns dict with serialized content for persistence.
        """
        from vizro_ai import VizroAI
        from langchain_openai import ChatOpenAI
        import io

        prompt = json.loads(messages[-1]["content_json"]) if messages else ""

        # Check if uploaded_data is available (set by function())
        uploaded_data = getattr(self, "_uploaded_data", None)
        if not uploaded_data:
            content = html.P("Please upload a CSV file first!", style={"color": "#1890ff"})
            return {"content_json": json.dumps(content, cls=plotly.utils.PlotlyJSONEncoder)}

        try:
            df = pd.read_json(io.StringIO(uploaded_data), orient="split")
        except Exception as e:
            content = html.P(f"Error loading data: {str(e)}", style={"color": "red"})
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

    def message_to_html(self, message):
        """Override to recreate components from serialized JSON."""
        content = json.loads(message["content_json"])

        return html.Div(
            html.Div(content, style=ASSISTANT_MESSAGE_STYLE),
            style={"display": "flex", "justifyContent": "flex-start", "width": "100%"},
        )


# -------------------- Chat Component --------------------


class Chat(VizroBaseModel):
    type: Literal["chat"] = "chat"
    actions: list[ActionType] = []

    # This is how you make a new component a trigger of an action in the new system.
    _make_actions_chain = model_validator(mode="after")(make_actions_chain)

    @property
    def _action_triggers(self):
        return {"__default__": f"{self.id}-send-button.n_clicks"}

    def build(self):
        return html.Div(
            [
                # Messages container
                html.Div(
                    [
                        html.Div(
                            [
                                # Hidden div to store raw messages
                                html.Div(id=f"{self.id}-hidden-messages", children=[], style={"display": "none"}),
                                # Visible div to display parsed messages with code highlighting
                                html.Div(id=f"{self.id}-rendered-messages", style=HISTORY_CONTAINER),
                            ],
                            id=f"{self.id}-chat-messages-container",
                        )
                    ],
                    style=HISTORY_SECTION,
                ),
                # Input area - reusable component without file upload
                build_input_area(chat_id=self.id, placeholder="How can I help you?", show_upload=False),
                # Loading indicator (hidden by default)
                html.Div(id=f"{self.id}-loading-output", style={"display": "none"}),
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
Chat.add_type("actions", Annotated[anthropic_chat, Tag("anthropic_chat")])
Chat.add_type("actions", Annotated[mixed_content, Tag("mixed_content")])
Chat.add_type("actions", Annotated[vizro_ai_chat, Tag("vizro_ai_chat")])


# -------------------- Helper Methods --------------------


def build_input_area(chat_id, placeholder="How can I help you?", show_upload=False, upload_id=None, file_info_id=None):
    """
    Build a reusable input area with optional file upload support.

    Args:
        chat_id: ID of the chat component
        placeholder: Placeholder text for the textarea
        show_upload: Whether to show the upload button
        upload_id: ID for the upload component (required if show_upload=True)
        file_info_id: ID for the file info display (required if show_upload=True)

    Returns:
        html.Div containing the input area with 3-row layout
    """
    rows = []

    # Row 1: File preview area (only if upload is enabled)
    if show_upload and file_info_id:
        rows.append(html.Div(id=file_info_id, style={"marginBottom": "8px", "minHeight": "0px"}))

    # Row 2: Textarea
    rows.append(
        dmc.Textarea(
            id=f"{chat_id}-chat-input",
            placeholder=placeholder,
            autosize=True,
            size="md",
            minRows=1,
            maxRows=6,
            radius=0,
            # styles: targets internal parts of the component (the actual textarea element)
            styles={
                "input": {
                    "borderLeft": "none",
                    "borderRight": "none",
                    "borderTop": "none",
                    "borderRadius": "0",
                    "resize": "none",
                    "backgroundColor": "var(--bs-body-bg)",  # from design system
                    "fontSize": FONT_SIZE_EDITORIAL,  # 16px for input text
                    "lineHeight": LINE_HEIGHT_EDITORIAL,  # 24px
                    "color": COLOR_TEXT_PRIMARY,  # Main text color
                }
            },
            # style: targets the outer wrapper div
            style={"width": "100%"},
            value="",
        )
    )

    # Row 3: Action buttons (upload and send)
    button_row = []

    if show_upload and upload_id:
        button_row.append(
            dcc.Upload(
                id=upload_id,
                children=dmc.ActionIcon(
                    DashIconify(
                        icon="material-symbols-light:attach-file-add", width=28, height=28
                    ),  # need to make this smaller so it looks aligned with the send button
                    variant="subtle",
                    color="grey",
                    radius=BORDER_RADIUS,
                    style={"width": "42px", "height": "42px"},
                ),
                style={"width": "fit-content"},
                multiple=False,
            )
        )
    else:
        # Invisible placeholder to maintain layout
        button_row.append(html.Div(style={"width": "42px", "height": "42px", "visibility": "hidden"}))

    button_row.append(
        dmc.ActionIcon(
            DashIconify(icon="material-symbols-light:send-outline", width=38, height=38),
            id=f"{chat_id}-send-button",
            variant="subtle",
            color="grey",
            n_clicks=0,
            radius=BORDER_RADIUS,
            style={"width": "42px", "height": "42px"},
        )
    )

    rows.append(
        html.Div(
            button_row,
            style={
                "display": "flex",
                "justifyContent": "space-between",
                "width": "100%",
            },
        )
    )

    return html.Div([html.Div(rows, style={"width": "100%", "maxWidth": MAX_CHAT_WIDTH})], style=INPUT_SECTION)


# -------------------- Chat with Upload Component --------------------


class ChatWithUpload(Chat):
    """Chat component with file upload capability for data analysis."""

    type: Literal["chat_with_upload"] = "chat_with_upload"

    def build(self):
        """Build the chat UI with file upload."""
        return html.Div(
            [
                # Data store
                dcc.Store(id=f"{self.id}-data-store"),
                # Messages container
                html.Div(
                    [
                        html.Div(
                            [
                                # Hidden div to store raw messages
                                html.Div(id=f"{self.id}-hidden-messages", children=[], style={"display": "none"}),
                                # Visible div to display parsed messages with code highlighting
                                html.Div(id=f"{self.id}-rendered-messages", style=HISTORY_CONTAINER),
                            ],
                            id=f"{self.id}-chat-messages-container",
                        )
                    ],
                    style=HISTORY_SECTION,
                ),
                # Input area - reusable component with file upload
                build_input_area(
                    chat_id=self.id,
                    placeholder="Ask about your data...",
                    show_upload=True,
                    upload_id=f"{self.id}-upload",
                    file_info_id=f"{self.id}-data-info",
                ),
                # Loading indicator (hidden by default)
                html.Div(id=f"{self.id}-loading-output", style={"display": "none"}),
                # Store for conversation history
                dcc.Store(id=f"{self.id}-store", data=[], storage_type="session"),
                # Server-Sent Events for streaming support
                SSE(id=f"{self.id}-sse", concat=True, animate_chunk=10, animate_delay=5),
            ],
            style={"height": "100%", "width": "100%", "display": "flex", "flexDirection": "column"},
        )

    def pre_build(self):
        """Set up file upload callback."""

        @callback(
            Output(f"{self.id}-data-store", "data"),
            Output(f"{self.id}-data-info", "children"),
            Input(f"{self.id}-upload", "contents"),
            State(f"{self.id}-upload", "filename"),
            prevent_initial_call=True,
        )
        def process_upload(contents, filename):
            """Process uploaded file and store data."""
            if contents is None:
                return None, ""

            try:
                import io

                # Parse the file
                content_type, content_string = contents.split(",")
                decoded = base64.b64decode(content_string)

                if filename.endswith(".csv"):
                    df = pd.read_csv(io.BytesIO(decoded))
                else:
                    return None, html.Div(
                        "Please upload a CSV file", style={"color": "red", "fontSize": FONT_SIZE_HELP}
                    )

                # Create a file preview with icon and filename
                info = html.Div(
                    [
                        dmc.Paper(
                            [
                                dmc.Group(
                                    [
                                        dmc.Text(filename, size="sm", fw=500),
                                        dmc.ActionIcon(
                                            DashIconify(icon="material-symbols:close", width=16),
                                            size="xs",
                                            variant="subtle",
                                            id=f"{self.id}-remove-file",
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
                    ],
                    style={"width": "200px"},
                )

                return df.to_json(orient="split"), info

            except Exception as e:
                return None, html.Div(
                    f"Error loading file: {str(e)}", style={"color": "red", "fontSize": FONT_SIZE_HELP}
                )

        @callback(
            Output(f"{self.id}-data-store", "data", allow_duplicate=True),
            Output(f"{self.id}-data-info", "children", allow_duplicate=True),
            Input(f"{self.id}-remove-file", "n_clicks"),
            prevent_initial_call=True,
        )
        def remove_file(n_clicks):
            """Remove the uploaded file."""
            if n_clicks:
                return None, ""
            return no_update, no_update


vm.Page.add_type("components", ChatWithUpload)
ChatWithUpload.add_type("actions", Annotated[vizro_ai_chat, Tag("vizro_ai_chat")])


page = vm.Page(
    title="OpenAI Chat (Streaming)",
    components=[
        Chat(
            id="chat",
            actions=[openai_chat(chat_id="chat", stream=True)],
        ),
    ],
)

page_nostream = vm.Page(
    title="OpenAI Chat (Non-Streaming)",
    components=[
        Chat(
            id="chat_nostream",
            actions=[openai_chat(chat_id="chat_nostream", stream=False)],
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
        Chat(id="mixed_chat", actions=[mixed_content(chat_id="mixed_chat")]),
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
            actions=[anthropic_chat(chat_id="claude_chat")],  # stream=True is set in the class
        ),
    ],
)

page_vizro_ai = vm.Page(
    title="VizroAI Natural Language Charts",
    components=[
        ChatWithUpload(
            id="vizro_ai_chat",
            actions=[vizro_ai_chat(chat_id="vizro_ai_chat")],
        ),
    ],
)

dashboard = vm.Dashboard(
    pages=[page, page_nostream, page_anthropic, page_2, page_vizro_ai],
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
