from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import dash_bootstrap_components as dbc

try:
    from pydantic.v1 import validator
except ImportError:  # pragma: no cov
    from pydantic import validator

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call, validate_min_length

if TYPE_CHECKING:
    from vizro.models._components import Container


class Tabs(VizroBaseModel):
    """Tabs to group together a set of containers on a page.

    Args:
        type (Literal["tabs"]): Defaults to `"tabs"`.
        tabs (list[Container]): See [`Container`][vizro.models.Container].

    """

    type: Literal["tabs"] = "tabs"
    tabs: list[Container]

    _validate_tabs = validator("tabs", allow_reuse=True, always=True)(validate_min_length)

    @_log_call
    def build(self):
        return dbc.Tabs(
            id=self.id,
            children=[dbc.Tab(tab.build(), label=tab.title) for tab in self.tabs],
            persistence=True,
            persistence_type="session",
        )
