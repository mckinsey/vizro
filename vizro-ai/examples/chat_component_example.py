"""Example of how to use the Chat component from vizro-ai with the plugin pattern."""

import os

import vizro.models as vm
import vizro_ai.models as vam
from dotenv import load_dotenv
from vizro import Vizro

load_dotenv()

demo_text = """
Vizro is an open-source Python-based toolkit.

Use it to build beautiful and powerful data visualization apps quickly and easily,
without needing advanced engineering or visual design expertise.

Then customize and deploy your app to production at scale.

In just a few lines of simple low-code configuration, with in-built visual design
best practices, you can quickly assemble high-quality, multi-page prototypes,
that are production-ready.
"""

example_llm_processor = vam.OpenAIProcessor(
    api_key=os.getenv("OPENAI_API_KEY"),
    api_base=os.getenv("OPENAI_BASE_URL"),
)

chat_component1 = vam.Chat(
    input_placeholder="Ask me a question...",
    processor=example_llm_processor,
)

chat_component2 = vam.Chat(
    processor=vam.EchoProcessor(),
    initial_message="I'm an echo processor",
)

chat_component3 = vam.Chat(
    processor=vam.EchoProcessor(),
    height="400px",
    storage_type="local",
)

chat_component4 = vam.Chat(
    input_placeholder="Ask me anything to see mixed content...",
    processor=vam.GraphProcessor(),
    initial_message="Hello! I can show you text, code, and interactive charts. Try asking me anything!",
)

vm.Page.add_type("components", vam.Chat)

page1 = vm.Page(
    title="Vizro Chat Demo",
    components=[chat_component1],
)

page2 = vm.Page(
    title="Vizro Chat with Grid Layout",
    components=[vm.Card(text=demo_text), chat_component2],
    layout=vm.Grid(grid=[[0, 1]]),
)

page3 = vm.Page(
    title="Vizro Chat with Flex Layout",
    components=[
        chat_component3,
        vm.Card(text=demo_text),
    ],
    layout=vm.Flex(direction="row"),
)

page4 = vm.Page(
    title="Chat with Graphs & Mixed Content",
    components=[chat_component4],
)

dashboard = vm.Dashboard(
    pages=[page1, page2, page3, page4],
    theme="vizro_light",
)

# IMPORTANT: Pass the chat component as a plugin to Vizro
# This ensures the streaming routes are properly registered during app initialization
app = Vizro(plugins=[chat_component1, chat_component2, chat_component3, chat_component4])
app.build(dashboard).run()
