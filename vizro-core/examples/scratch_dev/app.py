import base64
import json

import dash
from dotenv import load_dotenv


from pydantic import Tag, Field
from typing import Annotated, Optional, Any

from dash import html, dcc, callback, Output, Input, State, Patch, clientside_callback
from typing import Literal
from openai import OpenAI, BaseModel
from pydantic import model_validator

import vizro.models as vm

import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions._abstract_action import _AbstractAction
from vizro.managers import model_manager
from vizro.models import VizroBaseModel
from vizro.models._models_utils import make_actions_chain

from vizro.models.types import capture, ActionType

import dash_bootstrap_components as dbc

from dash_extensions import SSE
from dash_extensions.streaming import sse_message, sse_options
from flask import Response, request
from utils import yield_text_component

load_dotenv()


# User can write a chat response function just like it's an action i.e. just with a single function.
@capture("action")
def echo_function(prompt):
    return f"You said {prompt}"


# Class hierarchy for chat functionality:
# - echo: Basic chat functionality (no streaming)
# - ChatAction: Extends echo to add full chat functionality (streaming + non-streaming)
# - openai_pirate: Extends ChatAction to add OpenAI-specific API handling


# Or they can write it using a class, just like with an action.
class echo(_AbstractAction):
    type: Literal["echo"] = "echo"
    chat_id: str
    prompt: str = Field(default_factory=lambda data: f"{data['chat_id']}-input.value")
    # Or maybe input to match client.responses.create? Note input there can also
    # be whole history and not just latest although previous_response_id now easier way to do it.

    # TBD whether we need messages
    # messages: str

    def function(self, prompt):
        return f"You said {prompt}"

    @property
    def outputs(self):
        return [f"{self.chat_id}-output.children"]


# Pydantic model that will be dumped to json automatically by sse_options. Define this somewhere sensible.
class Stuff(BaseModel):
    prompt: str
    messages: Any  # I'm being lazy but maybe it doesn't matter


# Base class for chat functionality (streaming and non-streaming)
class ChatAction(echo):
    """Base class for chat functionality with streaming and non-streaming support."""
    stream: bool = True
    
    def pre_build(self):
        if self.stream:
            self._setup_streaming_callbacks()
            self._setup_streaming_endpoint()
        
        self._setup_chat_callbacks()

    
    def _setup_streaming_callbacks(self):
        """Set up clientside callback for streaming updates."""
        clientside_callback(
            """
            function(animatedText, existingChildren, storeData) {
                if (!animatedText || animatedText === '[DONE]') {
                    return [existingChildren, window.dash_clientside.no_update];
                }

                let component = null;
                let content = '';

                const decodedData = atob(animatedText);
                component = JSON.parse(decodedData);
                if (component.props && component.props.children) {
                    content = component.props.children;
                }

                const newChildren = [...(existingChildren || [])];
                const newData = [...(storeData || [])];

                if (newChildren.length > 0 && component) {
                    const last = newChildren[newChildren.length - 1];
                    if (last.props?.children?.[0]?.props?.children === "assistant") {
                        last.props.children[1] = component;
                    }
                }

                if (newData.length > 0 && newData[newData.length - 1].role === 'assistant') {
                    newData[newData.length - 1].content = content;
                }

                return [newChildren, newData];
            }
            """,
            [
                Output(f"{self.chat_id}-output", "children", allow_duplicate=True),
                Output(f"{self.chat_id}-store", "data", allow_duplicate=True),
            ],
            Input(f"{self.chat_id}-sse", "animation"),
            [State(f"{self.chat_id}-output", "children"), State(f"{self.chat_id}-store", "data")],
            prevent_initial_call=True,
        )

    def _setup_streaming_endpoint(self):
        """Set up streaming endpoint for SSE."""
        @dash.get_app().server.route(f"/streaming-{self.chat_id}", methods=["POST"], endpoint=f"streaming_chat_{self.chat_id}")
        def streaming_chat():
            stuff = Stuff(**request.get_json())

            def event_stream():
                for event in self.core_function(**stuff.model_dump()):
                    if event['type'] == 'text_chunk':
                        yield from yield_text_component(self.create_component, event['full_text'])

                # Send standard SSE completion signal
                yield sse_message()

            return Response(event_stream(), mimetype="text/event-stream")
    
    def _setup_chat_callbacks(self):
        """Set up generic chat UI callbacks."""
        # Callback for user input
        @callback(
            Output(f"{self.chat_id}-store", "data", allow_duplicate=True),
            Output(f"{self.chat_id}-output", "children", allow_duplicate=True),
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

        # Callback to restore chat history on page load
        page = model_manager._get_model_page(self)
        @callback(
            Output(f"{self.chat_id}-output", "children", allow_duplicate=True),
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

    
    def function(self, prompt, messages):
        """Generic function method for handling chat interactions."""
        # Need to repeat append here since this runs at same time as store update.
        latest_input = {"role": "user", "content": prompt}
        messages.append(latest_input)

        if self.stream:
            store, html_messages = Patch(), Patch()

            # Add generic placeholder for streaming response
            placeholder_msg = {"role": "assistant", "content": ""}
            store.append(placeholder_msg)
            html_messages.append(self.message_to_html(placeholder_msg))

            return [
                store,
                html_messages,
                f"/streaming-{self.chat_id}",
                sse_options(Stuff(prompt=prompt, messages=messages)),
            ]
        else:
            response = self.core_function(prompt, messages)
            latest_output = {"role": "assistant", "content": response.output_text}

            # Could do this without Patch and it would also work fine, but that would send more data across network than
            # is really necessary. Latest input has already been appended to both of these in update_with_user_input.
            store, html_messages = Patch(), Patch()
            store.append(latest_output)
            html_messages.append(self.message_to_html(latest_output))
            return store, html_messages
    
    def create_component(self, content_type, content):
        """Create the appropriate component based on content type.
        
        Args:
            content_type: Type of content ('text' or other)
            content: The actual content (text string)
        
        Returns:
            Dash component suitable for the content type
        """
        if content_type == "text":
            return dcc.Markdown(content, dangerously_allow_html=False)
        else:
            return html.Div(content)

    # User writes this function. Does it belong here or in Chat?
    def message_to_html(self, message):
        return html.Div([html.B(message["role"]), self.create_component("text", message["content"])])

    @property
    def outputs(self):
        """Define outputs for the chat component."""
        if self.stream:
            return [
                f"{self.chat_id}-store.data",
                f"{self.chat_id}-output.children",
                f"{self.chat_id}-sse.url",
                f"{self.chat_id}-sse.options",
            ]
        else:
            return [f"{self.chat_id}-store.data", f"{self.chat_id}-output.children"]


# Subclass ChatAction for OpenAI-specific functionality
# This class now uses a generic event-based approach where:
# - core_function handles provider-specific API calls and event processing
# - _process_streaming_response abstracts away provider-specific event types
# - _process_buffer_for_line_breaks handles text chunking strategy
# - The streaming endpoint only needs to handle generic 'text_chunk' events
class openai_pirate(ChatAction):
    # With the class-based definition there's room for static parameters like model and api_key which isn't possible
    # if you just write a function.
    type: Literal["openai_pirate"] = "openai_pirate"
    model: str = "gpt-4.1-nano"
    api_key: Optional[str] = None  # takes from os.environ.get("OPENAI_API_KEY") by default so maybe even omit this
    # and just make people set it through env variable
    api_base: Optional[str] = None  # similarly with os.environ.get("OPENAI_BASE_URL")
    stream: bool = True
    _client: OpenAI
    messages: str = Field(default_factory=lambda data: f"{data['chat_id']}-store.data")
    # expose instructions and other stuff as fields.
    # But ultimately users will want to customise a lot of things like tools etc. so should be able to easily write
    # their own.
    # Could pass through arbitrary kwargs to create function? Should always be configurable via JSON.
    # https://platform.openai.com/docs/api-reference/responses
    # Good idea to make this specific to OpenAI responses API and have specific arguments we've picked out for OpenAI
    # class, create and how to handle response.

    def pre_build(self):
        # Call parent pre_build to set up streaming callbacks and chat UI
        super().pre_build()
        
        # Initialize OpenAI client
        self._client = OpenAI(api_key=self.api_key, base_url=self.api_base)

    # User writes this function. Can it be the same function for streaming and non streaming and still work? I think
    # yes. It might still be worth having two separate functions though, not sure.
    # Note responses.create has different return types in these cases.
    def core_function(self, prompt, messages):
        """Core function that handles both streaming and non-streaming responses."""
        response = self._client.responses.create(
            model=self.model, 
            input=messages, 
            instructions="Be polite and creative.", 
            store=False, 
            stream=self.stream,
        )
        
        if self.stream:
            return self._process_streaming_response(response)
        else:
            return response
    
    def _process_streaming_response(self, response_stream):
        """Process streaming response.
        
        This method contains vendor-specific response handling.

        Args:
            response_stream: The raw streaming response from the LLM provider
            
        Yields:
            dict: Generic event objects with 'type' and 'content' keys
        """
        buffer = ""  # Buffer to accumulate text until we hit line breaks
        full_text = ""  # Accumulate all text received so far
        
        for event in response_stream:
            # Handle OpenAI-specific event types
            if event.type == "response.output_text.delta":
                buffer += event.delta
                processed_chunks = self._process_buffer_for_line_breaks(buffer)
                buffer = processed_chunks['remaining_buffer']
                
                for chunk in processed_chunks['complete_chunks']:
                    full_text += chunk
                    yield {
                        'type': 'text_chunk',
                        'content': chunk,
                        'full_text': full_text
                    }
        
        # Send any remaining text in buffer when stream ends
        if buffer:
            full_text += buffer
            yield {
                'type': 'text_chunk',
                'content': buffer,
                'full_text': full_text
            }
    
    # currently use the "\n\n" as buffer split, not sure if this is the best way to do it.
    def _process_buffer_for_line_breaks(self, buffer, line_break="\n\n"):
        complete_chunks = []
        remaining_buffer = buffer
        
        while line_break in remaining_buffer:
            split_pos = remaining_buffer.find(line_break)
            chunk = remaining_buffer[:split_pos] + line_break
            remaining_buffer = remaining_buffer[split_pos + len(line_break):]
            
            if chunk:
                complete_chunks.append(chunk)
        
        return {
            'complete_chunks': complete_chunks,
            'remaining_buffer': remaining_buffer
        }


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
# @capture("action")
# def openai_pirate_function(prompt):
#     client = OpenAI()
#     return client.responses.create(model="gpt-4.1-nano", instructions="Talk like a pirate.", input=prompt).output_text


# Note different return type objects work immediately - no need for different modes. You can return any Dash
# components you want.
class graph(echo):
    def function(self, prompt):
        return dcc.Graph(figure=px.scatter(px.data.iris(), x="sepal_width", y="sepal_length", title=prompt))


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
                # Note the SSE example uses
                # dcc.Markdown(id="response", dangerously_allow_html=True, dedent=False),
                # Question for Lingyi: Should we do the same? Will it mean that we can stream mixed content messages
                # directly? Do models actually return HTML?
                html.Div(id=f"{self.id}-output", children=[]),
                dcc.Store(id=f"{self.id}-store", data=[], storage_type="session"),  # TBD storage_type
                # animate_chunk was set to 20, causing truncation of base64-encoded JSON messages
                # Setting to a much larger value to accommodate full JSON component messages
                SSE(id=f"{self.id}-sse", concat=False, animate_chunk=10000, animate_delay=5),
                html.Div(id=f"{self.id}-streaming-output", style={"display": "none"}),
            ]
        )


vm.Page.add_type("components", Chat)
# Would just be Chat.add_type("actions", echo) in future but that still seems gross. Maybe need some way to avoid
# doing this. Could have base class for ChatAction that people subclass - sounds like good idea.
Chat.add_type("actions", Annotated[echo, Tag("echo")])
Chat.add_type("actions", Annotated[openai_pirate, Tag("openai_pirate")])

pirate_stream_action = openai_pirate(chat_id="chat")

page = vm.Page(
    title="Chat",
    components=[
        Chat(
            id="chat",
            # actions=[
            #     echo(chat_id="chat"),
            # ],
            # actions=[vm.Action(function=echo_function(prompt="chat-input.value"), outputs=["chat-output.children"])],
            # actions=[graph(chat_id="chat")],
            # actions=[
            #     vm.Action(function=openai_pirate_function(prompt="chat-input.value"), outputs=["chat-output.children"])
            # ],
            actions=[pirate_stream_action],
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

page_2 = vm.Page(title="Dummy", components=[vm.Card(text="dummy")])

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
