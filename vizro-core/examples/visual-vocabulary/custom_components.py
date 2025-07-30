"""Contains custom components used inside the dashboard."""

from typing import Literal
from urllib.parse import quote

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import vizro.models as vm
from dash import html


class CodeClipboard(vm.VizroBaseModel):
    """Code clipboard based on `dmc.CodeHighlight` with optional PyCafe link."""

    type: Literal["code_clipboard"] = "code_clipboard"
    code: str
    mode: Literal["vizro", "plotly"]
    language: str = "python"

    def build(self):
        """Build and return the complete code clipboard component."""
        pycafe_link = dbc.Button(
            [
                "Edit code live on PyCafe",
                html.Span("open_in_new", className="material-symbols-outlined open-in-new"),
            ],
            href=f"https://py.cafe/snippet/vizro/v1#code={quote(self.code)}",
            target="_blank",
            class_name="pycafe-link",
        )

        return html.Div(
            [
                pycafe_link if self.mode == "vizro" else None,
                dmc.CodeHighlight(
                    code=self.code,
                    language=self.language,
                ),
            ],
            className="code-clipboard-container",
        )


vm.Container.add_type("components", CodeClipboard)
