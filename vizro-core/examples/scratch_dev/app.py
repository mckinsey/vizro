from dotenv import load_dotenv


from pydantic import Tag, Field
from typing import Annotated, Optional

from dash import html, dcc
from typing import Literal
from openai import OpenAI
from pydantic import model_validator

import vizro.models as vm

import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions._abstract_action import _AbstractAction
from vizro.models import VizroBaseModel
from vizro.models._models_utils import make_actions_chain

from vizro.models.types import capture, ActionType

import dash_bootstrap_components as dbc

load_dotenv()


# User can write a chat response function just like it's an action i.e. just with a single function.
@capture("action")
def echo_function(prompt):
    return f"You said {prompt}"


# Or they can write it using a class, just like with an action.
class echo(_AbstractAction):
    type: Literal["echo"] = "echo"
    chat_id: str
    prompt: str = Field(default_factory=lambda data: f"{data["chat_id"]}-input.value")
    # Or maybe input to match client.responses.create? Note input there can also
    # be whole history and not just latest although previous_response_id now easier way to do it.
    # Could pass all messages or just previous_response_id.

    # TBD whether we need messages
    # messages: str

    def function(self, prompt):
        return f"You said {prompt}"

    @property
    def outputs(self):
        return [f"{self.chat_id}-output.children"]


# Subclass echo just because I'm lazy, but actually maybe we should actually have some common built-in chat class that
# gets subclassed.
class openai_pirate(echo):
    # With the class-based definition there's room for static parameters like model and api_key which isn't possible
    # if you just write a function.
    model: str = "gpt-4.1-nano"
    api_key: Optional[str] = None  # takes from os.environ.get("OPENAI_API_KEY") by default so maybe even omit this
    # and just make people set it through env variable
    api_base: Optional[str] = None  # similarly with os.environ.get("OPENAI_BASE_URL")
    _client: OpenAI
    # expose instructions and other stuff as fields.
    # But ultimately users will want to customise a lot of things like tools etc. so should be able to easily write
    # their own.
    # Could pass through arbitrary kwargs to create function? Should always be configurable via JSON.
    # https://platform.openai.com/docs/api-reference/responses
    # Good idea to make this specific to OpenAI responses API and have specific arguments we've picked out for OpenAI
    # class, create and how to handle response.

    def pre_build(self):
        self._client = OpenAI(api_key=self.api_key, base_url=self.api_base)

    def function(self, prompt):
        response = self._client.responses.create(model=self.model, instructions="Talk like a pirate.", input=prompt)

        return response.output_text


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
                html.Div(id=f"{self.id}-output"),
                # html.H1("Store"),
                # html.Pre(id=f"{self.id}-store"),
            ]
        )


vm.Page.add_type("components", Chat)
# Would just be Chat.add_type("actions", echo) in future but that still seems gross. Maybe need some way to avoid
# doing this. Could have base class for ChatAction that people subclass - sounds like good idea.
Chat.add_type("actions", Annotated[echo, Tag("echo")])

page = vm.Page(
    title="Chat",
    components=[
        Chat(
            id="chat",
            # actions=[
            #     echo(chat_id="chat"),
            # ],
            actions=[vm.Action(function=echo_function(prompt="chat-input.value"), outputs=["chat-output.children"])],
            # actions=[graph(chat_id="chat")],
            # actions=[
            #     vm.Action(function=openai_pirate_function(prompt="chat-input.value"), outputs=["chat-output.children"])
            # ],
            # actions=[
            #     openai_pirate(
            #         # model=..., optional
            #         chat_id="chat",
            #     ),
            # ],
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

dashboard = vm.Dashboard(pages=[page])

"""
Notes:
* still need to work out whether to use message history or previous_response_id. How to restore chat when go back to
page? Remember Patch.
* Streaming is not easy... Let's forget about it for now as a built-in feature, save it for fancy demos and then come
back to trying to build it in.

If get message history from server then need to hook into OPL for it. Could be whole separate action from OPL since 
it doesn't involve Figures. Could do this with OpenAI but looks like it's potentially several requests due to 
pagination.
If get message history from local then still need to populate somehow but not in OPL - could all be clientside and 
outside actions. Probably easier overall.
Use previous_response_id stored locally so there's possibility in future of moving message population to serverside.
"""

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
