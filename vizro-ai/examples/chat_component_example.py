"""Example of how to use the VizroChatComponent from vizro-ai."""

import os
import vizro.models as vm
from vizro import Vizro

import vizro_ai.components as vcc

from dotenv import load_dotenv
load_dotenv()

# Create the chat component using the refactored version
chat_component = vcc.VizroChatComponent(
    id="my_chat",
    input_placeholder="Ask me a question...",
    initial_message="Hello! I'm your AI assistant. How can I help you today?",
    # You can use either EchoProcessor or OpenAIProcessor
    # processor=vcc.EchoProcessor(),  # Default processor
    # For OpenAI, uncomment the following:
    processor=vcc.OpenAIProcessor(
        api_key=os.getenv("OPENAI_API_KEY"),
        api_base=os.getenv("OPENAI_BASE_URL"),
    ),
)

# Register the component type with Vizro
vm.Page.add_type("components", vcc.VizroChatComponent)

# Create a page with the chat component
page = vm.Page(
    title="Vizro-AI Chat Demo",
    components=[chat_component],
)

# Create and run the dashboard
dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run() 