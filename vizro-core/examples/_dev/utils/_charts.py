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


class HtmlIntro(vm.VizroBaseModel):
    type: Literal["html_intro"] = "html_intro"
    text: str

    def build(self):
        return html.H4(self.text, className="html-intro")
