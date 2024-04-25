"""Example where (invisible) filter on another page is set to the filter_interaction value from the Page_1.
    Once filter interaction from the Page_1 is triggered, user is redirected to the Page_2 where the filter is set to
    the chart clicked value.
    Implementation is solved utilising the "overwriting default actions" feature and by hiding the existing filter.
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

df = px.data.gapminder().query("year == 2007")
default_card_text = "Click on a cell in the table to filter the scatter plot."


class CustomDashboard(vm.Dashboard):
    """Custom Dashboard model which keeps ag_grid clicked data."""

    def build(self):
        dashboard_build_obj = super().build()
        dashboard_build_obj.children.extend([
            dcc.Location(id="url", refresh="callback-nav"),
            dcc.Store(id="global_data_store", data=[]),
        ])
        return dashboard_build_obj


@capture("action")
def save_clicked_data(grid_cell_clicked: Optional[Dict] = None):
    if grid_cell_clicked["colId"] != "continent":
        raise exceptions.PreventUpdate
    return [grid_cell_clicked['value']]


dashboard = CustomDashboard(
    pages=[
        vm.Page(
            title="Page_1",
            layout=vm.Layout(grid=[[0]] + [[1]]*5),
            components=[
                vm.Card(text="Click on a cell inside the 'continent' column to perform the Drill-through effect."),
                vm.AgGrid(
                    id="ag_grid",
                    figure=dash_ag_grid(id="underlying_ag_grid", data_frame=df),
                    actions=[
                        vm.Action(
                            function=save_clicked_data(),
                            inputs=["underlying_ag_grid.cellClicked"],
                            outputs=["global_data_store.data"],
                        ),
                        vm.Action(
                            function=capture("action")(lambda: "/page-2")(),
                            outputs=["url.href"],
                        )
                    ]
                ),
            ],
        ),
        vm.Page(
            title="Page 2",
            components=[
                vm.Graph(id="fig_2", figure=px.scatter(df, x="gdpPercap", y="lifeExp", size="pop", color="continent"))],
            controls=[
                # `display: none` is set to this filter, so it is not visible to the user.
                vm.Filter(
                    column="continent",
                    selector=vm.Dropdown(
                        id="drill_through_example_target_filter_selector"
                    )
                ),
                vm.Filter(column="gdpPercap"),
            ],
            actions=[
                # 1. It would be nice if we already had client side actions for this.
                vm.Action(
                    function=capture("action")(lambda x: x)(),
                    inputs=["global_data_store.data"],
                    outputs=["drill_through_example_target_filter_selector.value"],
                ),
                vm.Action(function=update_figures())
            ]
        ),
    ]
)


if __name__ == "__main__":
    Vizro().build(dashboard).run()
