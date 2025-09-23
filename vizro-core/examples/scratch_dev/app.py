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

load_dotenv()


# User can write a chat response function just like it's an action i.e. just with a single function.
@capture("action")
def echo_function(prompt):
    return f"You said {prompt}"


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


# Subclass echo just because I'm lazy, but actually maybe we should actually have some common built-in chat class that
# gets subclassed.
class openai_pirate(echo):
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
        self._client = OpenAI(api_key=self.api_key, base_url=self.api_base)

        # Should we define these callbacks in pre_build or in _define_callback with call to super()? Not sure yet.
        # Should we use vizro_store? Only if needed for correct functioning on change page. Otherwise best to build
        # in store here.
        # Must be serverside to use self.message_to_html.
        # Should be triggered in exact same way as main callback and at same time, but we assume it finishes before
        # other one because it's faster. Could this cause difficulties? Definitely requires multithreaded server at
        # least but that's ok. Would they ever not finish in right order? Not sure.
        # This callback populates chat messages with latest input straight away rather than waiting to receive response.
        # This makes it feel more responsive.
        @callback(
            # outputs are self.outputs
            Output(f"{self.chat_id}-store", "data", allow_duplicate=True),
            Output(f"{self.chat_id}-output", "children", allow_duplicate=True),
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

        if self.stream:
            # Question for Lingyi: what is happening here?! WHy is it so complicated and why do we have two
            # clientside callbacks?
            clientside_callback(
                """
                function(animatedText, existingChildren) {
                    if (!animatedText) return existingChildren;

                    // Check if this is the [DONE] completion signal - if so, ignore it
                    if (animatedText === '[DONE]') {
                        return existingChildren;
                    }

                    // Clone existing children
                    const newChildren = [...(existingChildren || [])];

                    // Find the last message and update it if it's from assistant
                    if (newChildren.length > 0) {
                        const lastIdx = newChildren.length - 1;
                        const lastMsg = newChildren[lastIdx];

                        // Check if this is an assistant message being streamed
                        if (lastMsg && lastMsg.props && lastMsg.props.children &&
                            lastMsg.props.children[0] && lastMsg.props.children[0].props &&
                            lastMsg.props.children[0].props.children === "assistant") {
                            // Update the content of the assistant message
                            lastMsg.props.children[1].props.children = animatedText;
                        }
                    }

                    return newChildren;
                }
                """,
                Output(f"{self.chat_id}-output", "children", allow_duplicate=True),
                Input(f"{self.chat_id}-sse", "animation"),
                State(f"{self.chat_id}-output", "children"),
                prevent_initial_call=True,
            )

            # Persist assistant message progressively on each non-empty animated chunk
            clientside_callback(
                """
                function(animatedText, sseData, storeData) {
                    if (!animatedText || animatedText === '[DONE]') {
                        return window.dash_clientside.no_update;
                    }

                    const newData = [...(storeData || [])];
                    const last = newData.length > 0 ? newData[newData.length - 1] : null;
                    if (last && last.role === 'assistant') {
                        newData[newData.length - 1] = {role: 'assistant', content: animatedText};
                    } else {
                        newData.push({role: 'assistant', content: animatedText});
                    }
                    return newData;
                }
                """,
                Output(f"{self.chat_id}-store", "data", allow_duplicate=True),
                Input(f"{self.chat_id}-sse", "animation"),
                State(f"{self.chat_id}-sse", "data"),
                State(f"{self.chat_id}-store", "data"),
                prevent_initial_call=True,
            )

    def plug(self, app):
        """Register streaming routes with the Dash app.

        Args:
            app: The Dash application instance.
        """
        if not self.stream:
            return

        # Now I'm wondering whether we actually want to do this with plug(). I think it's the "right" thing to do but
        # it is extra effort for the user and I think that for most setups it will probably work like you had it before.
        # I'd suggest we actually go back to using @dash.get_app().server.route() like you did before in pre_build.
        # That way someone can do app = Vizro() without needing to specify plugins.
        # Then we wait until someone finds a setup that doesn't work, complains, and we enable it with plugins as
        # well so that those people can have it work properly.
        # Question for Lingyi: if we do it the "wrong" way with @dash.get_app().server.route() in pre_build,
        # can you easily find any setups where it doesn't work? e.g. Maybe with gunicorn it doesn't?
        # Question: why do we set endpoint here?
        @app.server.post(f"/streaming-{self.chat_id}", endpoint=f"streaming_chat_{self.chat_id}")
        def streaming_chat():
            try:
                stuff = Stuff(**request.get_json())

                def event_stream():
                    response_stream = self.core_function(**stuff.model_dump())

                    for event in response_stream:
                        if event.type == "response.output_text.delta":
                            # Question for Lingyi: is it possible to somehow use self.message_to_html here?
                            # The data gets sent over SSE so won't come out correctly. But is there any way to break
                            # the message into chunks to e.g. separate off code snippets to use dmc.CodeHighlight?
                            # e.g. maybe dmc.CodeHighlight(event.delta).to_plotly_json() would translate it to json
                            # and then maybe somehow it could be rendered correctly.
                            # Experiment to see if each event comes out as a new html.P:
                            # It doesn't work but I feel like something like this might be possible?
                            # yield sse_message(html.P(event.delta))
                            # yield sse_message(html.P(event.delta).to_plotly_json())
                            yield sse_message(event.delta)

                    # Send standard SSE completion signal
                    # https://github.com/emilhe/dash-extensions/blob/78d1de50d32f888e5f287cfedfa536fe314ab0b4/dash_extensions/streaming.py#L6
                    yield sse_message()

                return Response(event_stream(), mimetype="text/event-stream")
            except Exception:
                # Let's check if we need this error catching.
                return Response("An internal error has occurred.", status=500)

    def function(self, prompt, messages):
        # Need to repeat append here since this runs at same time as store update.
        # To be decided exactly what gets passed and how (prompt, latest_input, messages, etc.)
        latest_input = {"role": "user", "content": prompt}
        messages.append(latest_input)

        if self.stream:
            # For streaming:
            # 1. Add an empty assistant message as placeholder
            # 2. Return SSE URL and options
            # TODO: 3. Add a callback to update store when streaming is complete

            store, html_messages = Patch(), Patch()

            placeholder_msg = {"role": "assistant", "content": ""}
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

    # User writes this function. Can it be the same function for streaming and non streaming and still work? I think
    # yes. It might still be worth having two separate functions though, not sure.
    # Note responses.create has different return types in these cases.
    def core_function(self, prompt, messages):
        return self._client.responses.create(
            model=self.model, input=messages, instructions="Talk like a pirate.", store=False, stream=self.stream
        )

    # User writes this function. Does it belong here or in Chat?
    def message_to_html(self, message):
        return html.Div([html.B(message["role"]), html.P(message["content"])])

    @property
    def outputs(self):
        if self.stream:
            return [
                f"{self.chat_id}-store.data",
                f"{self.chat_id}-output.children",
                f"{self.chat_id}-sse.url",
                f"{self.chat_id}-sse.options",
            ]
        else:
            return [f"{self.chat_id}-store.data", f"{self.chat_id}-output.children"]


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
                SSE(id=f"{self.id}-sse", concat=True, animate_chunk=5, animate_delay=10),
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

dashboard = vm.Dashboard(pages=[page, page_nostream, page_2])

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
    app = Vizro(plugins=[pirate_stream_action])
    app.build(dashboard).run(debug=False)
