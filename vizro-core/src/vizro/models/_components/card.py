from typing import Annotated, Any, Literal, Optional

import dash_bootstrap_components as dbc
from dash import dcc, get_relative_path, html
from pydantic import BeforeValidator, Field, model_validator
from pydantic.json_schema import JsonValue, SkipJsonSchema

from vizro.models import Tooltip, VizroBaseModel
from vizro.models._models_utils import _log_call, make_actions_chain
from vizro.models._tooltip import coerce_str_to_tooltip
from vizro.models.types import ActionsType, _IdProperty


class Card(VizroBaseModel):
    """Creates a card based on Markdown syntax.

    Abstract: Usage documentation
        [How to use cards](../user-guides/card.md)

    Args:
        type (Literal["card"]): Defaults to `"card"`.
        text (str): Markdown string to create card title/text that should adhere to the CommonMark Spec.
        header (str): Markdown text positioned above the card text. Follows the CommonMark specification.
            Ideal for adding supplementary information. Defaults to `""`.
        footer (str): Markdown text positioned at the bottom of the `Card`. Follows the CommonMark specification.
            Ideal for providing further details such as sources, disclaimers, or additional notes. Defaults to `""`.
        href (str): URL (relative or absolute) to navigate to. If not provided the Card serves as a text card
            only. Defaults to `""`.
        description (Optional[Tooltip]): Optional markdown string that adds an icon in the top-right corner of the Card.
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
        description="""Markdown text positioned above the card text. Follows the CommonMark specification. Ideal for
        adding supplementary information.""",
    )
    footer: str = Field(
        default="",
        description="""Markdown text positioned at the bottom of the `Card`. Follows the CommonMark specification.
        Ideal for providing further details such as sources, disclaimers, or additional notes.""",
    )
    href: str = Field(
        "",
        description="URL (relative or absolute) to navigate to. If not provided the Card serves as a text card only.",
    )
    # TODO: ideally description would have json_schema_input_type=Union[str, Tooltip] attached to the BeforeValidator,
    #  but this requires pydantic >= 2.9.
    description: Annotated[
        Optional[Tooltip],
        BeforeValidator(coerce_str_to_tooltip),
        Field(
            default=None,
            description="""Optional markdown string that adds an icon in the top-right corner of the Card.
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
            raise ValueError("Card cannot have both `href` and `actions` defined.")

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
    def _get_value_from_trigger(value: JsonValue, trigger: int) -> JsonValue:
        """Return the given `value` without modification."""
        return value

    @_log_call
    def build(self):
        description = self.description.build().children if self.description else [None]

        card_text = self._build_card_text()
        card_content = [
            self._build_card_header(description),
            self._build_card_body(card_text, description),
            self._build_card_footer(),
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

    def _build_card_text(self):
        """Wrap text in NavLink if href is provided."""
        text = dcc.Markdown(
            id=f"{self.id}-text", children=self.text, dangerously_allow_html=False, className="card-text"
        )
        if not self.href:
            return text

        href = get_relative_path(self.href) if self.href.startswith("/") else self.href
        return dbc.NavLink(children=text, href=href, target="_top")

    def _build_card_header(self, description):
        """Build card header."""
        if not self.header:
            return None

        children = [dcc.Markdown(children=self.header, dangerously_allow_html=False)]

        # Add description to header if it exists
        if description is not None:
            children.extend(description)

        return dbc.CardHeader(
            id=f"{self.id}_header",
            children=html.Div(children=children, className="card-header-outer"),
        )

    def _build_card_body(self, card_text, description):
        """Build card body with description if no header exists."""
        children = [card_text]

        # Add description to body only if there's no header
        if not self.header and description is not None:
            children.extend(description if isinstance(description, list) else [description])

        return dbc.CardBody(children=children, className="card-body-outer")

    def _build_card_footer(self):
        """Build card footer if footer text exists."""
        if not self.footer:
            return None

        return dbc.CardFooter(
            id=f"{self.id}_footer", children=dcc.Markdown(children=self.footer, dangerously_allow_html=False)
        )
