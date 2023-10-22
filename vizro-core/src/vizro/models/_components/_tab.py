from __future__ import annotations

from typing import List, Optional

from dash import dcc, html
from pydantic import Field

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models.types import ComponentType


class Tab(VizroBaseModel):
    components: List[ComponentType]
    label: str = Field(..., description="Tab Lable to be displayed.")
    title: Optional[str]  # do we need this one?
    # layout: Optional[Layout]

    @_log_call
    def build(self):
        components = [component.build() for component in self.components]
        return dcc.Tab(
            html.Div(children=[html.H3(self.title, className="tab-title"), *components]),
            id=self.id,
            label=self.label,
        )
