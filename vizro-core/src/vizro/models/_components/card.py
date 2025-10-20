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
        title (str): Title of the `Card`. Defaults to `""`.
        header (str): Markdown text positioned above the `Card.title`. Follows the CommonMark specification.
            Ideal for adding supplementary information. Defaults to `""`.
        footer (str): Markdown text positioned below the `Card`. Follows the CommonMark specification.
            Ideal for providing further details such as sources, disclaimers, or additional notes. Defaults to `""`.
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
    text: str = Field(
        description="Markdown string to create card title/text that should adhere to the CommonMark Spec."
    )
    title: str = Field(default="", description="Title of the `Card`")
    header: str = Field(
        default="",
        description="Markdown text positioned above the `Card.title`. Follows the CommonMark specification. Ideal for "
        "adding supplementary information.",
    )
    footer: str = Field(
        default="",
        description="Markdown text positioned below the `Card`. Follows the CommonMark specification. Ideal for "
        "providing further details such as sources, disclaimers, or additional notes.",
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
    def _validate_href_if_actions_set(self):
        if self.href and self.actions:
            raise ValueError("You cannot define both `href` and `actions` in `Card` model.")
        return self

    @model_validator(mode="after")
    def _make_actions_chain(self):
        return make_actions_chain(self)

    @property
    def _action_triggers(self) -> dict[str, _IdProperty]:
        return {"__default__": f"{self.id}-outer.n_clicks"}

    @property
    def _action_outputs(self) -> dict[str, _IdProperty]:
        return {
            "__default__": f"{self.id}-text.children",
            "text": f"{self.id}-text.children",
            **({"title": f"{self.id}_title.children"} if self.title else {}),
            **({"header": f"{self.id}_header.children"} if self.header else {}),
            **({"footer": f"{self.id}_footer.children"} if self.footer else {}),
            **({"description": f"{self.description.id}-text.children"} if self.description else {}),
        }

    @staticmethod
    def _get_value_from_trigger(value: str, trigger: int) -> JsonValue:
        """Return the given `value` without modification."""
        return value

    @_log_call
    def build(self):
        text = dcc.Markdown(
            id=f"{self.id}-text", children=self.text, dangerously_allow_html=False, className="card-text"
        )

        description = self.description.build().children if self.description else [None]

        title = html.Div(
            children=[
                html.H4(id=f"{self.id}_title", children=self.title, className="card-title") if self.title else None,
                *description,
            ],
            className="card-title-outer",
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

        card_content = [
            dbc.CardHeader(id=f"{self.id}_header", children=self.header) if self.header else None,
            dbc.CardBody(children=[title, card_text]),
            dbc.CardFooter(id=f"{self.id}_footer", children=self.footer) if self.footer else None,
        ]

        defaults = {
            "id": self.id,
            "children": card_content,
            "class_name": "card-nav" if self.href else "",
        }

        return html.Div(
            id=f"{self.id}-outer",
            children=dbc.Card(**(defaults | self.extra)),
            className="card-wrapper-actions" if self.actions else "card-wrapper",
        )
