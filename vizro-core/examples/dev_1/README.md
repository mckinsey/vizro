# Chat Component Example

This example demonstrates how to use and customize the Vizro Chat Component.

## Installation

Before running the example, install the required packages:

```bash
pip install -r requirements.txt
```

## Basic Usage

The basic example shows how to add a chat component to your Vizro dashboard:

```python
from vizro import Vizro
import vizro.models as vm
from vizro_chat import VizroChatComponent

# Register and use the component
vm.Page.add_type("components", VizroChatComponent)

chat_page = vm.Page(
    title="Chat Assistant",
    components=[
        VizroChatComponent(
            id="chat",
            input_placeholder="Ask anything...",
            button_text="Ask",
        )
    ],
)
```

## Custom Chat Component

The custom example shows how to extend the base chat component with additional features:

```python
from vizro_chat import VizroChatComponent
from typing import Literal

class CustomChatComponent(VizroChatComponent):
    type: Literal["custom_chat"] = "custom_chat"
    button_color: str = "primary"
    
    def build(self):
        base_component = super().build()
        button = base_component.find_component(f"{self.id}-submit")
        button.color = self.button_color
        return base_component
```

## Running the Examples

1. Install the vizro-chat package:
```bash
pip install vizro-chat
```

2. Run the basic example:
```bash
python app.py
```

3. To use the custom component, modify app.py to use CustomChatComponent instead of VizroChatComponent. 