"""Contains custom components and charts used inside the dashboard."""

from typing import Literal

import dash_bootstrap_components as dbc
import vizro.models as vm
from dash import dcc, html

try:
    from pydantic.v1 import Field
except ImportError:  # pragma: no cov
    from pydantic import Field


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


class Markdown(vm.VizroBaseModel):
    type: Literal["markdown"] = "markdown"
    text: str = Field(
        ..., description="Markdown string to create card title/text that should adhere to the CommonMark Spec."
    )
    classname: str = ""

    def build(self):
        return dcc.Markdown(id=self.id, children=self.text, dangerously_allow_html=False, className=self.classname)


class FlexContainer(vm.Container):
    """Custom flex `Container`."""

    type: Literal["flex_container"] = "flex_container"

    def build(self):
        return html.Div(
            id=self.id, children=[component.build() for component in self.components], className="flex-container"
        )
