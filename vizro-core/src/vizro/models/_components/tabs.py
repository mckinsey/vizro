from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Literal, Optional

import dash_bootstrap_components as dbc
from dash import html
from pydantic import AfterValidator, BeforeValidator, Field, conlist

from vizro.models import Tooltip, VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models._tooltip import coerce_str_to_tooltip
from vizro.models.types import _IdProperty

if TYPE_CHECKING:
    from vizro.models._components import Container


def validate_tab_has_title(tab: Container) -> Container:
    if not tab.title:
        raise ValueError("`Container` must have a `title` explicitly set when used inside `Tabs`.")
    return tab


class Tabs(VizroBaseModel):
    """Tabs to group together a set of containers on a page.

    Args:
        type (Literal["tabs"]): Defaults to `"tabs"`.
        tabs (list[Container]): See [`Container`][vizro.models.Container].
        title (str): Title displayed above Tabs. Defaults to `""`.
        description (Optional[Tooltip]): Optional markdown string that adds an icon next to the title.
            Hovering over the icon shows a tooltip with the provided description. Defaults to `None`.

    """

    type: Literal["tabs"] = "tabs"
    # TODO[mypy], see: https://github.com/pydantic/pydantic/issues/156 for tabs field
    tabs: conlist(Annotated[Container, AfterValidator(validate_tab_has_title)], min_length=1)  # type: ignore[valid-type]
    title: str = Field(default="", description="Title displayed above Tabs.")
    description: Annotated[
        Optional[Tooltip],
        BeforeValidator(coerce_str_to_tooltip),
        Field(
            default=None,
            description="""Optional markdown string that adds an icon next to the title.
            Hovering over the icon shows a tooltip with the provided description. Defaults to `None`.""",
        ),
    ]

    @property
    def _action_outputs(self) -> dict[str, _IdProperty]:
        return {
            **({"title": f"{self.id}_title.children"} if self.title else {}),
            **({"description": f"{self.description.id}-text.children"} if self.description else {}),
        }

    @_log_call
    def build(self):
        description = self.description.build().children if self.description else [None]

        title_content = (
            html.H3([html.Span(self.title, id=f"{self.id}_title"), *description], className="inner-tabs-title")
            if self.title
            else None
        )

        tabs = dbc.Tabs(
            id=self.id,
            children=[dbc.Tab(tab.build(), label=tab.title) for tab in self.tabs],
            persistence=True,
            persistence_type="session",
        )

        return html.Div(children=[title_content, tabs], className="tabs-container")
