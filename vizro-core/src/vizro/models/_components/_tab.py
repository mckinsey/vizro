from __future__ import annotations

from typing import List, Optional

from dash import dcc, html
from pydantic import Field

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models.types import TabComponentType


class Tab(VizroBaseModel):
    components: List[TabComponentType]
    label: str = Field(..., description="Tab Lable to be displayed.")
    title: Optional[str]  # do we need this one?
    # layout: Optional[Layout]
    # controls: List[ControlType] = []  -> should be done implicitly without configuring? -> tendency to remove it
    # actions: List[ActionsChain] = []  -> do we even need to make this configurable? -> tendency to remove it

    @_log_call
    def build(self):
        components = [component.build() for component in self.components]
        return dcc.Tab(
            id=self.id,
            label=self.label,
            children=html.Div(
                children=[html.H4(self.title), *components],
                id=f"{self.id}_outer",
            ),
        )
