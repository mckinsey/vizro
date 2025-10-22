import warnings
from typing import Annotated, Any, Literal, Optional

import dash_bootstrap_components as dbc
from dash import dcc, get_relative_path, html
from pydantic import AfterValidator, BeforeValidator, Field, ValidationInfo, model_validator
from pydantic.json_schema import JsonValue, SkipJsonSchema

from vizro.models import Tooltip, VizroBaseModel
from vizro.models._models_utils import _log_call, make_actions_chain
from vizro.models._tooltip import coerce_str_to_tooltip
from vizro.models.types import ActionsType, _IdProperty


def warn_description_without_header(description, info: ValidationInfo):
    header = info.data.get("header")

    if description and not header:
        warnings.warn(
            """
            The `description` field is set, but `header` is missing or empty.
            The tooltip will not appear unless a `header` is provided.
            """,
            UserWarning,
        )
    return description


class Card(VizroBaseModel):
    """Creates a card based on Markdown syntax.

    Args:
        type (Literal["card"]): Defaults to `"card"`.
        text (str): Markdown string to create card title/text that should adhere to the CommonMark Spec.
        header (str): Markdown text positioned above the `Card.title`. Follows the CommonMark specification.
            Ideal for adding supplementary information. Defaults to `""`.
        footer (str): Markdown text positioned below the `Card`. Follows the CommonMark specification.
            Ideal for providing further details such as sources, disclaimers, or additional notes. Defaults to `""`.
        href (str): URL (relative or absolute) to navigate to. If not provided the Card serves as a text card
            only. Defaults to `""`.
        description (Optional[Tooltip]): Optional markdown string that adds an icon next to the card header.
            Hovering over the icon shows a tooltip with the provided description. Defaults to `None`.
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
        AfterValidator(warn_description_without_header),
        Field(
            default=None,
            description="""Optional markdown string that adds an icon next to the card header.
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
    def validate_href_and_actions(self):
        if self.href and self.actions:
            raise ValueError("Button cannot have both `href` and `actions` defined.")

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
            dbc.CardHeader(
                id=f"{self.id}_header",
                children=html.Div(
                    children=[dcc.Markdown(children=self.header, dangerously_allow_html=False), *description],
                    className="card-header-outer",
                ),
            )
            if self.header
            else None,
            dbc.CardBody(children=card_text),
            dbc.CardFooter(
                id=f"{self.id}_footer", children=dcc.Markdown(children=self.footer, dangerously_allow_html=False)
            )
            if self.footer
            else None,
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
