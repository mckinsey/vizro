# flake8: noqa
"""Example where filter on another page is set to the value of the filter on the first page.
    Implementation is solved utilising the "overwriting default actions" feature.
"""

from typing import Any, Dict, List, Optional

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from dash import Output, dcc
from vizro import Vizro
from vizro.actions import filter_action, filter_interaction, update_figures
from vizro.managers._model_manager import ModelID
from vizro.models.types import capture

df = px.data.gapminder().query("year == 2007")
default_card_text = "Click on a cell in the table to filter the scatter plot."
default_dropdown_value = ["Asia"]


class CustomDashboard(vm.Dashboard):
    """Custom Dashboard model which keeps ag_grid clicked data."""

    def build(self):
        dashboard_build_obj = super().build()
        dashboard_build_obj.children.append(dcc.Store(id="global_data_store", data=default_dropdown_value))
        return dashboard_build_obj


class CustomFilterAction(filter_action):
    """Action which stores the filter from data into the global store."""

    @staticmethod
    def pure_function(
        targets: Optional[List[ModelID]] = None,
        **inputs: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            # filter value could also be fetched from the ctx.args_grouping.
            "global_data_store": inputs["filters"][0],
            **filter_interaction.pure_function(targets=targets, **inputs),
        }

    @property
    def outputs(self):
        return {
            "global_data_store": Output("global_data_store", "data"),
            **super().outputs,
        }


def _filter_isin(series: pd.Series, value) -> pd.Series:
    return series.isin(value)


dashboard = CustomDashboard(
    pages=[
        vm.Page(
            title="Page_1",
            components=[
                vm.Graph(id="fig_1", figure=px.scatter(df, x="gdpPercap", y="lifeExp", size="pop", color="continent")),
            ],
            controls=[
                vm.Filter(
                    column="continent",
                    selector=vm.Dropdown(
                        options=df["continent"].unique().tolist(),
                        value=default_dropdown_value,
                        actions=[
                            vm.Action(
                                function=CustomFilterAction(
                                    targets=["fig_1"],
                                    filter_column="continent",
                                    filter_function=_filter_isin,
                                ),
                            )
                        ],
                    ),
                ),
            ],
        ),
        vm.Page(
            title="Page 2",
            components=[
                vm.Graph(id="fig_2", figure=px.scatter(df, x="gdpPercap", y="lifeExp", size="pop", color="continent"))
            ],
            controls=[
                vm.Filter(column="continent", selector=vm.Dropdown(id="target_filter_selector")),
            ],
            actions=[
                # 1. It would be nice if we already had client side actions for this.
                # 2. Probably that would be a good idea to implement this using customising UpdateFigure action.
                #   where additional input would be the 'global_data_store' and additional output would be the 'filter'.
                #   The down-side of this approach is that the filter value would only become visible when the action
                #   is finished.
                vm.Action(
                    function=capture("action")(lambda x: x)(),
                    inputs=["global_data_store.data"],
                    outputs=["target_filter_selector.value"],
                ),
                vm.Action(function=update_figures()),
            ],
        ),
    ]
)


if __name__ == "__main__":
    Vizro().build(dashboard).run()
