from __future__ import annotations

from typing import Annotated, Any

import dash_bootstrap_components as dbc
from dash import dcc, html
from pydantic import (
    AfterValidator,
    Field,
)
from pydantic.json_schema import SkipJsonSchema

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call, validate_icon
from vizro.models.types import _IdProperty


def coerce_str_to_tooltip(text: Any) -> Any:
    if isinstance(text, str):
        return Tooltip(text=text, icon="Info")
    return text


class Tooltip(VizroBaseModel):
    """A tooltip that displays text when hovering over an icon.

    Args:
        text (str): Markdown string for text shown when hovering over the icon. Should adhere to the CommonMark Spec.
        icon (str): Icon name from [Google Material icons library](https://fonts.google.com/icons).
        extra (Optional[dict[str, Any]]): Extra keyword arguments that are passed to `dbc.Tooltip` and overwrite any
            chosen by the Vizro team. This may have unexpected behavior. Visit the
            [dbc documentation](https://dash-bootstrap-components.opensource.faculty.ai/docs/components/tooltip/)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
            underlying component may change in the future. Defaults to `{}`.

    """

    text: str = Field(
        description="Markdown string for text shown when hovering over the icon. Should adhere to the CommonMark Spec."
    )
    icon: Annotated[
        str,
        AfterValidator(validate_icon),
        Field(description="Icon name from Google Material icons library."),
    ]
    extra: SkipJsonSchema[
        Annotated[
            dict[str, Any],
            Field(
                default={},
                description="""Extra keyword arguments that are passed to `dbc.Tooltip` and overwrite any
                defaults chosen by the Vizro team. This may have unexpected behavior. Visit the
                [dbc documentation](https://dash-bootstrap-components.opensource.faculty.ai/docs/components/tooltip/)
                to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and
                the underlying component may change in the future. Defaults to `{}`.""",
            ),
        ]
    ]

    @property
    def _action_outputs(self) -> dict[str, _IdProperty]:
        return {
            "__default__": f"{self.id}-text.children",
            "text": f"{self.id}-text.children",
            "icon": f"{self.id}-icon.children",
        }

    @_log_call
    def build(self):
        defaults = {
            "id": self.id,
            "children": dcc.Markdown(id=f"{self.id}-text", children=self.text, className="card-text"),
            "target": f"{self.id}-icon",
            "autohide": False,
        }

        return html.Div(
            [
                html.Span(self.icon, id=f"{self.id}-icon", className="material-symbols-outlined tooltip-icon"),
                dbc.Tooltip(**(defaults | self.extra)),
            ]
        )
