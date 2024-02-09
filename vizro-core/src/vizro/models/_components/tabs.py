from __future__ import annotations

from typing import TYPE_CHECKING, List, Literal

import dash_mantine_components as dmc
from dash import html

try:
    from pydantic.v1 import validator
except ImportError:  # pragma: no cov
    from pydantic import validator

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call, _validate_min_length

if TYPE_CHECKING:
    from vizro.models._components import Container


class Tabs(VizroBaseModel):
    """Tabs to group together a set of containers on a page.

    Args:
        type (Literal["tabs"]): Defaults to `"tabs"`.
        tabs (List[Container]): See [`Container`][vizro.models.Container].

    """

    type: Literal["tabs"] = "tabs"
    tabs: List[Container]

    _validate_tabs = validator("tabs", allow_reuse=True, always=True)(_validate_min_length)

    @_log_call
    def build(self):
        tabs_list = dmc.TabsList(
            [dmc.Tab(tab.title, value=tab.id, className="tab__title") for tab in self.tabs],
            className="tabs__list",
        )

        tabs_panels = [
            dmc.TabsPanel(html.Div([tab.build()], className="tab__content"), value=tab.id, className="tabs__panel")
            for tab in self.tabs
        ]

        return dmc.Tabs(
            id=self.id,
            value=self.tabs[0].id,
            children=[tabs_list, *tabs_panels],
            persistence=True,
            persistence_type="session",
            className="tabs",
        )
