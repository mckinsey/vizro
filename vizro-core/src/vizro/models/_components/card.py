from typing import Annotated, Any, Literal, Optional

import dash_bootstrap_components as dbc
from dash import dcc, get_relative_path, html
from pydantic import AfterValidator, BeforeValidator, Field, model_validator
from pydantic.json_schema import JsonValue, SkipJsonSchema

from vizro.models import Tooltip, VizroBaseModel
from vizro.models._models_utils import _log_call, make_actions_chain, warn_description_without_title
from vizro.models._tooltip import coerce_str_to_tooltip
from vizro.models.types import ActionsType, _IdProperty


class Card(VizroBaseModel):
    """Creates a card based on Markdown syntax.

    Args:
        type (Literal["card"]): Defaults to `"card"`.
        text (str): Markdown string to create card title/text that should adhere to the CommonMark Spec.
        href (str): URL (relative or absolute) to navigate to. If not provided the Card serves as a text card
            only. Defaults to `""`.
        extra (Optional[dict[str, Any]]): Extra keyword arguments that are passed to `dbc.Card` and overwrite any
            defaults chosen by the Vizro team. This may have unexpected behavior.
            Visit the [dbc documentation](https://www.dash-bootstrap-components.com/docs/components/card/)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
            underlying component may change in the future. Defaults to `{}`.
        actions (ActionsType): See [`ActionsType`][vizro.models.types.ActionsType].

    """

    type: Literal["card"] = "card"
    title: str = ""
    header: str = ""
    image: str = ""
    footer: str = ""
    text: str = Field(
        description="Markdown string to create card title/text that should adhere to the CommonMark Spec."
    )
    href: str = Field(
        "",
        description="URL (relative or absolute) to navigate to. If not provided the Card serves as a text card only.",
    )
    description: Annotated[
        Optional[Tooltip],
        BeforeValidator(coerce_str_to_tooltip),
        AfterValidator(warn_description_without_title),
        Field(
            default=None,
            description="""Optional markdown string that adds an icon next to the title.
            Hovering over the icon shows a tooltip with the provided description. Defaults to `None`.""",
        ),
    ]
    extra: SkipJsonSchema[
        Annotated[
            dict[str, Any],
            Field(
                default={},
                description="""Extra keyword arguments that are passed to `dbc.Card` and overwrite any
            defaults chosen by the Vizro team. This may have unexpected behavior.
            Visit the [dbc documentation](https://www.dash-bootstrap-components.com/docs/components/card/)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
            underlying component may change in the future. Defaults to `{}`.""",
            ),
        ]
    ]
    actions: ActionsType = []

    @model_validator(mode="after")
    def _make_actions_chain(self):
        return make_actions_chain(self)

    @property
    def _action_triggers(self) -> dict[str, _IdProperty]:
        return {"__default__": f"{self.id}.n_clicks"}

    @property
    def _action_outputs(self) -> dict[str, _IdProperty]:
        return {
            "__default__": f"{self.id}-text.children",
            "text": f"{self.id}-text.children",
        }

    @staticmethod
    def _get_value_from_trigger(value: str, trigger: int) -> JsonValue:
        """Return the given `value` without modification."""
        return value

    @_log_call
    def build(self):
        header = dbc.CardHeader(self.header) if self.header else None
        footer = dbc.CardFooter(self.footer) if self.footer else None
        text = dcc.Markdown(
            id=f"{self.id}-text", children=self.text, dangerously_allow_html=False, className="card-text"
        )

        description = self.description.build().children if self.description is not None else [None]

        title = html.Div(
            children=[html.H4(self.title, className="card-title") if self.title else None, *description],
            className="card-title-desc",
        )

        card_text = (
            dbc.NavLink(
                children=text,
                href=get_relative_path(self.href) if self.href.startswith("/") else self.href,
                target="_top",
            )
            if self.href
            else text
        )
        card_body = dbc.CardBody(children=[title, card_text])

        card_content = [header, card_body, footer]

        defaults = {
            "id": self.id,
            "children": card_content,
            "class_name": "card-nav" if self.href else "",
        }

        return html.Div(dbc.Card(**(defaults | self.extra)), className="card-wrapper")
