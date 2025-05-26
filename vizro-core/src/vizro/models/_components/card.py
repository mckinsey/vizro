from typing import Annotated, Any, Literal

import dash_bootstrap_components as dbc
from dash import dcc, get_relative_path
from pydantic import Field
from pydantic.json_schema import SkipJsonSchema

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models.types import _IdProperty


class Card(VizroBaseModel):
    """Creates a card based on Markdown syntax.

    Args:
        type (Literal["card"]): Defaults to `"card"`.
        text (str): Markdown string to create card title/text that should adhere to the CommonMark Spec.
        href (str): URL (relative or absolute) to navigate to. If not provided the Card serves as a text card
            only. Defaults to `""`.
        extra (Optional[dict[str, Any]]): Extra keyword arguments that are passed to `dbc.Card` and overwrite any
            defaults chosen by the Vizro team. This may have unexpected behavior.
            Visit the [dbc documentation](https://dash-bootstrap-components.opensource.faculty.ai/docs/components/card/)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
            underlying component may change in the future. Defaults to `{}`.

    """

    type: Literal["card"] = "card"
    text: str = Field(
        description="Markdown string to create card title/text that should adhere to the CommonMark Spec."
    )
    href: str = Field(
        "",
        description="URL (relative or absolute) to navigate to. If not provided the Card serves as a text card only.",
    )
    extra: SkipJsonSchema[
        Annotated[
            dict[str, Any],
            Field(
                default={},
                description="""Extra keyword arguments that are passed to `dbc.Card` and overwrite any
            defaults chosen by the Vizro team. This may have unexpected behavior.
            Visit the [dbc documentation](https://dash-bootstrap-components.opensource.faculty.ai/docs/components/card/)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
            underlying component may change in the future. Defaults to `{}`.""",
            ),
        ]
    ]

    @property
    def _action_outputs(self) -> dict[str, _IdProperty]:
        return {
            "__default__": f"{self.id}-text.children",
            "text": f"{self.id}-text.children",
        }

    @_log_call
    def build(self):
        text = dcc.Markdown(
            id=f"{self.id}-text", children=self.text, dangerously_allow_html=False, className="card-text"
        )

        card_content = (
            dbc.NavLink(
                children=text,
                href=get_relative_path(self.href) if self.href.startswith("/") else self.href,
                target="_top",
            )
            if self.href
            else text
        )

        defaults = {
            "id": self.id,
            "children": card_content,
            "class_name": "card-nav" if self.href else "",
        }

        return dbc.Card(**(defaults | self.extra))
