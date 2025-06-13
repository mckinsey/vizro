"""Example of how to use the Chat component from vizro-ai with the plugin pattern."""

import os
import vizro.models as vm
from vizro import Vizro

import vizro_ai.models as vam

from dotenv import load_dotenv
load_dotenv()

# Create the chat component
chat_component = vam.Chat(
    id="my_chat",
    input_placeholder="Ask me a question...",
    initial_message="Hello! I'm your AI assistant. How can I help you today?",
    # You can use either EchoProcessor or OpenAIProcessor
    # processor=vam.EchoProcessor(),  # Default processor
    # For OpenAI, uncomment the following:
    processor=vam.OpenAIProcessor(
        api_key=os.getenv("OPENAI_API_KEY"),
        api_base=os.getenv("OPENAI_BASE_URL"),
    ),
)

# Register the component type with Vizro
vm.Page.add_type("components", vam.Chat)

# Create a page with the chat component
page = vm.Page(
    title="Vizro-AI Chat Demo",
    components=[chat_component],
)

# Create the dashboard
dashboard = vm.Dashboard(pages=[page])

# IMPORTANT: Pass the chat component as a plugin to Vizro
# This ensures the streaming routes are properly registered during app initialization
app = Vizro(plugins=[chat_component])
app.build(dashboard).run() 