"""Contains custom components and charts used inside the dashboard."""

from typing import Literal

import dash_bootstrap_components as dbc
import vizro.models as vm
from dash import dcc, html


# CUSTOM COMPONENTS -------------------------------------------------------------
class CodeClipboard(vm.VizroBaseModel):
    type: Literal["code_clipboard"] = "code_clipboard"
    title: str = "Code"
    text: str

    def build(self):
        return dbc.Accordion(
            [
                dbc.AccordionItem(
                    dbc.Card(
                        [
                            html.H3(self.title),
                            dcc.Markdown(self.text, id=self.id, className="code-block"),
                            dcc.Clipboard(target_id=self.id, className="code-clipboard"),
                        ]
                    ),
                    title="SHOW CODE",
                )
            ],
            start_collapsed=True,
        )


class CustomTextCard(vm.Card):
    type: Literal["custom_text_card"] = "custom_text_card"

    def build(self):
        text_card = super().build()
        text_card[self.id].className = "custom-text-card"
        return text_card


class FlexContainer(vm.Container):
    """Custom flex `Container`."""

    type: Literal["flex_container"] = "flex_container"

    def build(self):
        return html.Div(
            id=self.id, children=[component.build() for component in self.components], className="flex-container"
        )
