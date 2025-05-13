from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Literal

import dash_bootstrap_components as dbc
from dash import html
from pydantic import AfterValidator, Field, conlist

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call

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

    """

    type: Literal["tabs"] = "tabs"
    # TODO[mypy], see: https://github.com/pydantic/pydantic/issues/156 for tabs field
    tabs: conlist(Annotated[Container, AfterValidator(validate_tab_has_title)], min_length=1)  # type: ignore[valid-type]
    title: str = Field(default="", description="Title displayed above Tabs.")

    @_log_call
    def build(self):
        title = html.H3(self.title, id=f"{self.id}_title") if self.title else None
        tabs = dbc.Tabs(
            id=self.id,
            children=[dbc.Tab(tab.build(), label=tab.title) for tab in self.tabs],
            persistence=True,
            persistence_type="session",
        )

        return html.Div(children=[title, tabs], className="tabs-container")
