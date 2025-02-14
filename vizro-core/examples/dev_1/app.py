"""Example of a chat assistant using VizroChatComponent."""

import os

import vizro.models as vm
from vizro import Vizro
from vizro_chat import EchoProcessor, VizroChatComponent

# from vizro_chat import OpenAIProcessor

# Initialize Vizro
vizro_app = Vizro()

# Initialize Vizro with assets folder
assets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
vizro_app = Vizro(assets_folder=assets_path)

# Register the chat component
vm.Page.add_type("components", VizroChatComponent)

# Create chat component with OpenAI processor
chat_component = VizroChatComponent(
    id="chat",
    input_placeholder="Ask anything...",
    button_text="Send",
    vizro_app=vizro_app,
    # processor=OpenAIProcessor(model="gpt-4o-mini", temperature=0.7)  # Or use EchoProcessor() for testing
    processor=EchoProcessor(),
)

# Create a chat page
chat_page = vm.Page(
    title="Chat Assistant",
    components=[chat_component],
)

# Build and run
dashboard = vm.Dashboard(pages=[chat_page])
vizro_app.build(dashboard)
vizro_app.run()
