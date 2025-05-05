"""Example of how to use the VizroChatComponent."""
import os
from vizro_chat_component import EchoProcessor, VizroChatComponent, OpenAIProcessor

import vizro.models as vm
from vizro import Vizro

chat_component = VizroChatComponent(
    id="my_chat",
    input_placeholder="Ask me a question...",
    # processor=EchoProcessor(),
    processor=OpenAIProcessor(
        api_key=os.getenv("OPENAI_API_KEY"),
        api_base=os.getenv("OPENAI_BASE_URL"),
    ),
)

vm.Page.add_type("components", VizroChatComponent)

page = vm.Page(
    title="Chat Demo",
    components=[chat_component],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
