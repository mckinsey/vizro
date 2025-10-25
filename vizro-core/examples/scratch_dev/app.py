import base64
from typing import Annotated, Optional, Any, Literal, Union

import dash
from dash import html, dcc, callback, Output, Input, State, Patch, clientside_callback
from dash.development.base_component import Component
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_extensions import SSE
from dash_extensions.streaming import sse_message, sse_options
from dotenv import load_dotenv
from flask import Response, request
from openai import OpenAI, BaseModel
from pydantic import Tag, Field, model_validator

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions._abstract_action import _AbstractAction
from vizro.managers import model_manager
from vizro.models import VizroBaseModel
from vizro.models._models_utils import make_actions_chain
from vizro.models.types import capture, ActionType


load_dotenv()


# -------------------- Base Classes --------------------


class StreamingRequest(BaseModel):
    """Request payload for streaming chat endpoint."""

    prompt: str
    messages: Any  # List of message dicts with 'role' and 'content' keys


class ChatResponse(BaseModel):
    """Standard response format for chat actions."""
    model_config = {"arbitrary_types_allowed": True}

    content: Union[str, Component]  # String or any Dash component instance


class ChatAction(_AbstractAction):
    """Base class for chat functionality with streaming and non-streaming support."""

    type: Literal["chat_action"] = "chat_action"
    chat_id: str
    prompt: str = Field(default_factory=lambda data: f"{data['chat_id']}-input.value")
    messages: str = Field(default_factory=lambda data: f"{data['chat_id']}-store.data")
    stream: bool = True

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

                // Helper: Get message content from structure
                function getMessageContent(msg) {
                    return msg?.props?.children?.[1]?.props?.children || '';
                }

                // Helper: Set message content in structure
                function setMessageContent(msg, content) {
                    if (msg?.props?.children?.[1]?.props) {
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
                        lastStoreMsg.content += newText;
                    }
                }

                return [newChildren, newData];
            }
            """,
            [
                Output(f"{self.chat_id}-hidden-messages", "children", allow_duplicate=True),
                Output(f"{self.chat_id}-store", "data", allow_duplicate=True),
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
                for chunk in self.core_function(**req.model_dump()):
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

                // Component factory helpers
                const createComponent = (type, namespace, props) => ({
                    type, namespace, props
                });

                const createMarkdown = (text) => createComponent(
                    "Markdown",
                    "dash_core_components",
                    { children: text, dangerously_allow_html: false }
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

                const createDiv = (children) => createComponent(
                    "Div",
                    "dash_html_components",
                    { children }
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
                    // Validate message structure
                    if (!msg?.props?.children || msg.props.children.length < 2) {
                        return msg;
                    }

                    const [role, contentWrapper] = msg.props.children;
                    const content = contentWrapper?.props?.children;

                    // Only process string content
                    if (typeof content !== 'string') return msg;

                    const parts = parseContent(content);

                    // Return original if no code blocks found
                    if (parts.length === 0) return msg;

                    // Reconstruct message with parsed content
                    return createDiv([role, createDiv(parts)]);
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
            # input(*self._action_triggers["__default__"].split(".")), # Need to look up parent action triggers and
            # make sure it.
            Input(f"{self.chat_id}-submit", "n_clicks"),
            State(*self.prompt.split(".")),
            prevent_initial_call=True,
        )
        def update_with_user_input(_, prompt):
            store, html_messages = Patch(), Patch()
            latest_input = {"role": "user", "content": prompt}
            store.append(latest_input)
            html_messages.append(self.message_to_html(latest_input))
            return store, html_messages

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

    def core_function(self):
        raise NotImplementedError("Subclasses must implement core_function")

    def function(self, prompt, messages):
        # Need to repeat append here since this runs at same time as store update.
        # To be decided exactly what gets passed and how (prompt, latest_input, messages, etc.)
        latest_input = {"role": "user", "content": prompt}
        messages.append(latest_input)

        if self.stream:
            store, html_messages = Patch(), Patch()

            placeholder_msg = {"role": "assistant", "content": ""}
            store.append(placeholder_msg)
            html_messages.append(self.message_to_html(placeholder_msg))

            return [
                store,
                html_messages,
                f"/streaming-{self.chat_id}",
                sse_options(StreamingRequest(prompt=prompt, messages=messages)),
            ]
        else:
            response = self.core_function(prompt, messages)
            latest_output = {"role": "assistant", "content": response.content}

            # Could do this without Patch and it would also work fine, but that would send more data across network than
            # is really necessary. Latest input has already been appended to both of these in update_with_user_input.
            store, html_messages = Patch(), Patch()
            store.append(latest_output)
            html_messages.append(self.message_to_html(latest_output))
            return store, html_messages

    def message_to_html(self, message):
        content = message["content"]
        role_label = html.B(message["role"])

        if isinstance(content, Component):
            return html.Div([role_label, content])
        else:
            return html.Div([role_label, html.Div(content)])

    @property
    def outputs(self):
        if self.stream:
            return [
                f"{self.chat_id}-store.data",
                f"{self.chat_id}-hidden-messages.children",
                f"{self.chat_id}-sse.url",
                f"{self.chat_id}-sse.options",
            ]
        else:
            return [f"{self.chat_id}-store.data", f"{self.chat_id}-hidden-messages.children"]


class openai_pirate(ChatAction):
    # With the class-based definition there's room for static parameters like model and api_key which isn't possible
    # if you just write a function.
    type: Literal["openai_pirate"] = "openai_pirate"
    model: str = "gpt-4.1-nano"
    api_key: Optional[str] = None  # Uses OPENAI_API_KEY env variable if not provided
    api_base: Optional[str] = None  # Uses OPENAI_BASE_URL env variable if not provided
    stream: bool = True
    _client: OpenAI
    messages: str = Field(default_factory=lambda data: f"{data['chat_id']}-store.data")
    # expose instructions and other stuff as fields.
    # But ultimately users will want to customize a lot of things like tools etc. so should be able to easily write
    # their own.
    # Could pass through arbitrary kwargs to create function? Should always be configurable via JSON.
    # https://platform.openai.com/docs/api-reference/responses
    # Good idea to make this specific to OpenAI responses API and have specific arguments we've picked out for OpenAI
    # class, create and how to handle response.

    def pre_build(self):
        super().pre_build()

        self._client = OpenAI(api_key=self.api_key, base_url=self.api_base)

    def _stream_response(self, messages):
        """Handle streaming response from OpenAI."""
        response = self._client.responses.create(
            model=self.model,
            input=messages,
            instructions="Be polite and creative.",
            store=False,
            stream=True,
        )

        for event in response:
            # Handle OpenAI-specific event types
            if event.type == "response.output_text.delta":
                yield event.delta

    def _non_stream_response(self, messages):
        """Handle non-streaming response from OpenAI."""
        response = self._client.responses.create(
            model=self.model,
            input=messages,
            instructions="Be polite and creative.",
            store=False,
            stream=False,
        )
        return ChatResponse(content=response.output_text)

    # User writes this function. Can it be the same function for streaming and non streaming and still work? I think
    # yes. It might still be worth having two separate functions though, not sure.
    # Note responses.create has different return types in these cases.
    def core_function(self, prompt, messages):
        """Core function that handles both streaming and non-streaming responses."""
        if self.stream:
            return self._stream_response(messages)
        else:
            return self._non_stream_response(messages)


# -------------------- Example Chat Actions --------------------
# This could also be done as a function and it works fine. client could be defined inside function or outside. There's
# no big cost recreating it every time.
# Note the function versions still need you to specify prompt since can't use chat_id as a static argument.
# This will get impractical once there's also message history and previous response id etc. So for user to write
# their own easily they really need to be able to plug in just a function e.g. def chat_function in openai class that
# gets called from inside function.
# Could have some @capture("action", template=...) that makes the class for them so they can still do without
# subclassing?
# Overall this seems fine - you can manually write function or use various built in things to make it easier. Have
# full flexibility but not too hard to write.


@capture("action")
def openai_pirate_function(prompt):
    client = OpenAI()
    return client.responses.create(model="gpt-4.1-nano", instructions="Talk like a pirate.", input=prompt).output_text


class SimpleEchoChat(ChatAction):
    """Simple echo chat."""

    type: Literal["simple_echo"] = "simple_echo"
    stream: bool = False

    def core_function(self, prompt, messages):
        return ChatResponse(content=f"You said: {prompt}")


class mixed_content(ChatAction):
    """Chat action that returns different content types based on keywords."""

    type: Literal["mixed_content"] = "mixed_content"
    stream: bool = False  # Components can't be streamed
    messages: str = Field(default_factory=lambda data: f"{data['chat_id']}-store.data")

    def core_function(self, prompt, messages):
        prompt_lower = prompt.lower()

        if "chart" in prompt_lower or "graph" in prompt_lower or "plot" in prompt_lower:
            # Return a Plotly chart
            fig = px.scatter(
                px.data.iris(),
                x="sepal_width",
                y="sepal_length",
                color="species",
                title=f"Iris Dataset - Response to: {prompt}",
                height=400,
            )
            return ChatResponse(content=dcc.Graph(figure=fig))

        elif "image" in prompt_lower or "picture" in prompt_lower or "photo" in prompt_lower:
            # Return an image using dmc.Image
            image = dmc.Image(
                radius="md",
                h=300,
                w="auto",
                fit="contain",
                src="https://raw.githubusercontent.com/mantinedev/mantine/master/.demo/images/bg-9.png",
            )
            return ChatResponse(content=image)

        else:
            # Return regular text with markdown and code
            response = f"""
I understand you said: "{prompt}"

I can show you different types of content:
- Use keywords like **chart**, **graph**, or **plot** to see a scatter plot
- Use **image**, **picture**, or **photo** to see an image
- Or just chat normally for text responses

Here's an example of code rendering:
```python
# Sample Python code
import plotly.express as px

# Create a visualization
fig = px.scatter(data, x="x_col", y="y_col")
fig.show()
```

This demonstrates that markdown formatting and code highlighting still work perfectly!
"""
            return ChatResponse(content=response.strip())

    @property
    def outputs(self):
        return [
            f"{self.chat_id}-store.data",
            f"{self.chat_id}-hidden-messages.children",
        ]


# -------------------- Chat Component --------------------


class Chat(VizroBaseModel):
    type: Literal["chat"] = "chat"
    actions: list[ActionType] = []

    # This is how you make a new component a trigger of an action in the new system.
    _make_actions_chain = model_validator(mode="after")(make_actions_chain)

    @property
    def _action_triggers(self):
        # Or {"__default__": f"{self.id}-input.value"} or both somehow (clientside callback?)
        return {"__default__": f"{self.id}-submit.n_clicks"}

    def build(self):
        return html.Div(
            [
                dbc.Input(id=f"{self.id}-input", placeholder="Type something...", type="text", debounce=True),
                dbc.Button(id=f"{self.id}-submit", children="Submit"),
                # Hidden div to store raw messages
                html.Div(id=f"{self.id}-hidden-messages", children=[], style={"display": "none"}),
                # Visible div to display parsed messages with code highlighting
                html.Div(id=f"{self.id}-rendered-messages", children=[]),
                dcc.Store(id=f"{self.id}-store", data=[], storage_type="session"),
                SSE(id=f"{self.id}-sse", concat=True, animate_chunk=10, animate_delay=5),
            ]
        )


vm.Page.add_type("components", Chat)
Chat.add_type("actions", Annotated[SimpleEchoChat, Tag("simple_echo")])
Chat.add_type("actions", Annotated[openai_pirate, Tag("openai_pirate")])
Chat.add_type("actions", Annotated[mixed_content, Tag("mixed_content")])


page = vm.Page(
    title="Chat",
    components=[
        Chat(
            id="chat",
            actions=[openai_pirate(chat_id="chat", stream=True)],
            # actions=[openai_pirate_function(prompt="chat-input.value")],
        ),
        # Soon you wouldn't have to label with id like this. It would be done by looking up in the model
        # manager. So it would just like this and no need to specify id="chat" which looks silly right now.
        # Chat(actions=[echo()])
        # prompt and output are optional and would have default value defined in pre_build of class that looks at
        # self._tree. Or better maybe there's some special syntax for "<parent>.value" that could be used for
        # inputs/outputs. We could have a sort of lookup dictionary like in AIO components. Then it works as above but
        # just need to have automatic way of specify chat_id.
        # prompt: str = "<something_special>.input"
        # Where <something_special> translates to the correct ID somehow - will need to figure out how given that
        # it's not the direct parent.
        # Would be able to use same syntax for outputs property.
    ],
)

page_2 = vm.Page(
    title="Mixed Content Chat",
    layout=vm.Flex(direction="column"),
    components=[
        vm.Card(
            text="""
## Mixed Content Chat Demo

This chat can display different types of content:
- **Text**: Just type normally for markdown-formatted responses with code highlighting
- **Charts**: Use words like 'chart', 'graph', or 'plot' to see a scatter plot
- **Images**: Use 'image', 'picture', or 'photo' to display an image

Try typing: "Show me a chart" or "Display an image" or just chat normally!
"""
        ),
        Chat(id="mixed_chat", actions=[mixed_content(chat_id="mixed_chat")]),
    ],
)

page_nostream = vm.Page(
    title="Chat (non-stream)",
    components=[
        Chat(
            id="chat_nostream",
            actions=[
                openai_pirate(
                    chat_id="chat_nostream",
                    stream=False,
                ),
            ],
        ),
    ],
)


dashboard = vm.Dashboard(
    pages=[page, page_nostream, page_2],
    theme="vizro_light",
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
