from __future__ import annotations

from vizro._constants import ON_PAGE_LOAD_ACTION_PREFIX
from vizro.actions import _on_page_load

from vizro.models import Action
from vizro.models._action._actions_chain import ActionsChain, Trigger
from typing import List, Optional, TYPE_CHECKING

import dash_bootstrap_components as dbc
from dash import html, dcc
from pydantic import Field, validator

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models.types import TabComponentType


class Tab(VizroBaseModel):
    components: List[TabComponentType]
    label: str = Field(..., description="Tab Lable to be displayed.")
    title: Optional[str]  # do we need this one?
    # layout: Optional[Layout]
    # controls: List[ControlType] = []  -> should be done implicitly without configuring? -> tendency to remove it
    actions: List[ActionsChain] = []

    @validator("actions", always=True)
    def validate_tab_actions(cls, actions, values):
        from vizro.models import Graph
        # TODO: Remove default on page load action if possible
        if any(isinstance(component, Graph) for component in values["components"]):
            actions = [
                ActionsChain(
                    id=f"{ON_PAGE_LOAD_ACTION_PREFIX}_{values['id']}",
                    trigger=Trigger(
                        component_id=f"{ON_PAGE_LOAD_ACTION_PREFIX}_trigger_{values['id']}",
                        component_property="data",
                    ),
                    actions=[
                        Action(
                            id=f"{ON_PAGE_LOAD_ACTION_PREFIX}_action_{values['id']}", function=_on_page_load(page_id=values['id'])
                        )
                    ],
                )
            ]
        return actions

    @_log_call
    def pre_build(self):
        print(self.actions)
        return dbc.Tab(
            id=self.id,
            label=self.label,
            tab_id=self.id,
            tabClassName="custom-tab",
            labelClassName="custom-tab-label",
            activeTabClassName="custom-tab-active",
            activeLabelClassName="custom-tab-label-active",
        )

    @_log_call
    def build(self):
        components = [component.build() for component in self.components]
        return html.Div(children=[
            html.H3(self.title, className="tab-title"),
            # Component that triggers _on_page_load action which returns tab Graphs
            # Needs improvements: Probably we need to create new action called "_on_tab_load".
            dcc.Store(id=f"{ON_PAGE_LOAD_ACTION_PREFIX}_trigger_{self.id}"),
            *components
        ])
