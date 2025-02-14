import os
from vizro import Vizro
import vizro.models as vm
from vizro_chat import VizroChatComponent

# Initialize Vizro
vizro_app = Vizro()

# Initialize Vizro with assets folder
assets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
vizro_app = Vizro(assets_folder=assets_path)

# Register the chat component
vm.Page.add_type("components", VizroChatComponent)

# Create chat component
chat_component = VizroChatComponent(
    id="chat",
    input_placeholder="Ask anything...",
    button_text="Ask",
    vizro_app=vizro_app
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