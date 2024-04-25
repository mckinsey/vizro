"""Custom filter function example.
    Example below shows a try of how to implement a custom filter action that should be taken into account while
    performing other predefined actions. Custom filter action should perform filtering but always to include "Europe".
    1. Example over CustomFilterAction.
        This example tries to achieve the requirement by utilising "customising predefined actions" feature. It appends
        "Europe" to the input value and then calls the predefined filter_action function. The problem with this approach
        is that the custom action works, but only until some other predefined action (e.g. parameter action) is called.
        The problem is that the other predefined actions are not aware of the custom implementation of this filter
        action. As a result, this custom action is considered as a standard filter action (without a custom behaviour).
    2. Example over custom_filter_function_isin (run it by uncommenting the code section in vm.Filter.actions and
        commenting out the configuration related to CustomFilterAction. Select a continent in RadioItem in the app).
        This example works but... it's not the best example of the "taking the custom action into account while
        performing other predefined actions". The only reason why it works is that because the "filtering process" is
        exposed to the user. The user can define the "filter_function" that is used in the filter_action. Not all
        actions have "core function" exposed to the user. "filter_function" is something similar to what the
        "actions_info" should be.
"""
import pandas as pd
from typing import Optional, Dict, List, Any

import dash_ag_grid as dag
import vizro.models as vm
import vizro.plotly.express as px
from dash import ctx, dcc, Output, State
from vizro import Vizro
from vizro.actions import export_data, filter_interaction, update_figures, filter_action
from vizro.managers._model_manager import ModelID
from vizro.tables import dash_ag_grid
from vizro.models.types import capture

df = px.data.gapminder().query("year == 2007")
default_card_text = "Click on a cell in the table to filter the scatter plot."


class CustomDashboard(vm.Dashboard):
    """Custom Dashboard model which keeps ag_grid clicked data."""

    def build(self):
        dashboard_build_obj = super().build()
        dashboard_build_obj.children.append(dcc.Store(id="global_data_store"))
        return dashboard_build_obj


# -----> Example 1: 'CustomFilterAction' <-----
class CustomFilterAction(filter_action):
    """Action that filters the data based on the selected value, but always includes "Europe" in the filter."""

    @staticmethod
    def pure_function(
        targets: Optional[List[ModelID]] = None,
        **inputs: Dict[str, Any],
    ) -> Dict[str, Any]:
        # Similar like it's used in the "03_01_customising_predefined_action_with_inheriting.py" CustomUpdateFigures.
        ctx.args_grouping['external']['filters'][0]['value'] = [
            ctx.args_grouping['external']['filters'][0]['value'],
            "Europe"
        ]
        return {
            **filter_action.pure_function(targets=targets, **inputs),
        }


def _standard_vizro_filter_isin(series: pd.Series, value) -> pd.Series:
    return series.isin(value)


# -----> Example 2: 'custom_filter_function_isin' <-----
# Solution that works but is not the best example of the "taking the custom action into account while performing other"
def custom_filter_function_isin(series: pd.Series, value) -> pd.Series:
    value = value + ["Europe"]
    return series.isin(value)


dashboard = CustomDashboard(
    pages=[
        vm.Page(
            title="Page_1",
            layout=vm.Layout(grid=[[0], [1], [1], [1], [2], [2], [2], [3]]),
            components=[
                vm.Card(id="card", text=default_card_text),
                vm.AgGrid(
                    id="ag_grid",
                    figure=dash_ag_grid(id="underlying_ag_grid", data_frame=df),
                    actions=[vm.Action(function=filter_interaction(targets=["scatter"]))]
                ),
                vm.Graph(id="scatter", figure=px.scatter(df, x="gdpPercap", y="lifeExp", size="pop", color="continent")),
                vm.Button(text="Export data", actions=[vm.Action(function=export_data(targets=["scatter"]))])
            ],
            controls=[
                vm.Filter(
                    column="continent",
                    targets=["scatter"],
                    selector=vm.RadioItems(
                        title="Filter by continent: (Europe is included)",
                        options=sorted(list(set(df["continent"].unique().tolist()) - {"Europe"})),
                        actions=[
                            # -----> Example 1: 'CustomFilterAction' <-----
                            # Solution that doesn't work because custom behavior isn't seen by other predefined actions.
                            vm.Action(
                                function=CustomFilterAction(
                                    targets=["scatter"],
                                    filter_column="continent",
                                    filter_function=_standard_vizro_filter_isin
                                )
                            ),

                            # # -----> Example 2: 'custom_filter_function_isin' <-----
                            # # Solution that works but is not the best example as explained in the docstring.
                            # vm.Action(
                            #     function=filter_action(
                            #         targets=["scatter"],
                            #         filter_column="continent",
                            #         filter_function=custom_filter_function_isin
                            #     ),
                            # ),
                        ]
                    )
                ),
                vm.Parameter(selector=vm.RadioItems(options=["gdpPercap", "lifeExp"]), targets=["scatter.x"]),
            ],
        ),
        vm.Page(
            title="Page 2",
            components=[vm.Graph(figure=px.scatter(df, x="gdpPercap", y="lifeExp", color="continent"))],
            controls=[vm.Filter(column="continent")]
        ),
    ]
)
if __name__ == "__main__":
    Vizro().build(dashboard).run()
