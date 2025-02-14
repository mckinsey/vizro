"""Custom chat component example."""

from typing import Literal

import dash_bootstrap_components as dbc
from vizro_chat import VizroChatComponent


class CustomChatComponent(VizroChatComponent):
    """A customized chat component."""

    type: Literal["custom_chat"] = "custom_chat"

    button_color: str = "info"

    def build(self):
        """Build the component."""
        component = super().build()

        input_group = component.children[1].children[1].children[0]
        for child in input_group.children:
            if isinstance(child, dbc.Button):
                child.color = self.button_color

        return component
