"""Contains custom components used inside the dashboard."""

from typing import Literal

import dash_bootstrap_components as dbc
import vizro.models as vm
from dash import dcc, html

try:
    from pydantic.v1 import Field
except ImportError:  # pragma: no cov
    from pydantic import Field

from urllib.parse import quote


class CodeClipboard(vm.VizroBaseModel):
    """Code snippet with a copy to clipboard button."""

    type: Literal["code_clipboard"] = "code_clipboard"
    code: str
    mode: Literal["vizro", "plotly"]
    language: str = ""

    def build(self):
        """Returns the code clipboard component inside an accordion."""
        markdown_code = "\n".join([f"```{self.language}", self.code, "```"])

        pycafe_link = dbc.Button(
            [
                "Edit code live on PyCafe",
                html.Span("open_in_new", className="material-symbols-outlined open-in-new"),
            ],
            href=f"https://py.cafe/snippet/vizro/v1#code={quote(self.code)}",
            target="_blank",
            className="pycafe-link",
        )

        return html.Div(
            [
                pycafe_link if self.mode == "vizro" else None,
                dcc.Clipboard(target_id=self.id, className="code-clipboard"),
                dcc.Markdown(markdown_code, id=self.id),
            ],
            className="code-clipboard-container",
        )


class Markdown(vm.VizroBaseModel):
    """Markdown component."""

    type: Literal["markdown"] = "markdown"
    text: str = Field(
        ..., description="Markdown string to create card title/text that should adhere to the CommonMark Spec."
    )
    classname: str = ""

    def build(self):
        """Returns a markdown component with an optional classname."""
        return dcc.Markdown(
            id=self.id, children=self.text, dangerously_allow_html=False, className=self.classname, link_target="_blank"
        )


class FlexContainer(vm.Container):
    """Custom flex `Container`."""

    type: Literal["flex_container"] = "flex_container"
    title: str = None  # Title exists in vm.Container but we don't want to use it here.

    def build(self):
        """Returns a flex container."""
        return html.Div(
            id=self.id, children=[component.build() for component in self.components], className="flex-container"
        )


vm.Container.add_type("components", FlexContainer)
vm.Container.add_type("components", Markdown)
vm.Container.add_type("components", CodeClipboard)
