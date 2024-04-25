"""Trigger update_figures on button click.

1. Why it doesn't work?
2. How can we hack it?
    2.1 We can apply custom_filter_action on button.actions which preventUpdate. (This is done in the example below)
    2.2 We can make custom_parameter_action, custom_update_figures and custom_export_data, but it is exhausting process.
    2.3 Enable pure filter_actions to be defined for controls. Then, in between the vm.Dashboard.build and the server.run
        maybe it's possible to adjust action loop engine, so it prevents update (or doesn't call at all) filter actions.
3. How can we support this to work natively?
    3.1. Implementation of new actions architecture:
        - Enable that customised predefined actions are taken into account properly while triggering other
            predefined actions. It means that every action is triggered on its own which means that 'pure_function' of
            the filter_action only filters data for targeted charts. Or even to introduce a new CapturedActionCallable
            method called 'core_function' which does that. It would change the way how actions are applied in the
            _actions_utils.py. Each action that is taken into account would be triggered separately (its core_function).
        - That way, we can define custom_filter_action on button.actions which would apply filtering on two targets.

"""
import pandas as pd
from typing import Optional, Dict, List, Any

import dash_ag_grid as dag
import vizro.models as vm
import vizro.plotly.express as px
from dash import ctx, dcc, Output, State, exceptions
from vizro import Vizro
from vizro.actions import export_data, filter_interaction, update_figures, filter_action
from vizro.managers._model_manager import ModelID
from vizro.tables import dash_ag_grid
from vizro.models.types import capture


df = px.data.gapminder()


class CustomFilterAction(filter_action):
    """Custom filter action which prevents update."""
    @staticmethod
    def pure_function(**kwargs):
        raise exceptions.PreventUpdate


def _filter_isin(series: pd.Series, value) -> pd.Series:
    return series.isin(value)


vm.Page.add_type("controls", vm.Button)

dashboard = vm.Dashboard(
    pages=[
        vm.Page(
            title="Page_1",
            components=[
                vm.AgGrid(
                    id="ag_grid",
                    figure=dash_ag_grid(id="underlying_ag_grid", data_frame=df),
                ),
                vm.Graph(id="scatter", figure=px.scatter(df, x="gdpPercap", y="lifeExp", size="pop", color="continent")),
                vm.Button(text="Export data", actions=[vm.Action(function=export_data(targets=["scatter"]))])
            ],
            controls=[
                vm.Filter(
                    column="year",
                    selector=vm.Slider(
                        title="Filter by year:",
                        min=1952,
                        max=2007,
                        step=5,
                        actions=[
                            vm.Action(
                                function=CustomFilterAction(
                                    filter_column="year",
                                    targets=["ag_grid", "scatter"],
                                    filter_function=_filter_isin
                                )
                            )
                        ],
                    )
                ),
                vm.Filter(
                    column="continent",
                    selector=vm.RadioItems(
                        title="Filter by continent:",
                        actions=[
                            vm.Action(
                                function=CustomFilterAction(
                                    filter_column="continent",
                                    targets=["ag_grid", "scatter"],
                                    filter_function=_filter_isin
                                )
                            )
                        ],
                    )
                ),
                vm.Button(
                    text="Apply filters on click",
                    actions=[
                        vm.Action(function=update_figures())
                    ]
                ),
                vm.Parameter(
                    targets=["scatter.x"],
                    selector=vm.RadioItems(options=["gdpPercap", "lifeExp"]),
                ),
            ],
            actions=[]
        ),
    ]
)
if __name__ == "__main__":
    Vizro().build(dashboard).run()
