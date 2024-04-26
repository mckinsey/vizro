# flake8: noqa
"""Customising (overwriting) predefined actions with @capture.
    This example shows some limitations of the current vm.Action inputs/outputs building mechanism. The general idea is
        to enable users to overwrite predefined action only by using the @capture decorator. It doesn't seem possible to
        achieve this, since _action._get_callback_mapping can't reconcile self.inputs (List[States]) and
        self.function.inputs (Dict[str, List[State]]) at the same time.

    Example below shows an attempt to customise the predefined filter_interaction action. The idea is to save the
        clicked data from the ag_grid into the global store and card component.
"""

from typing import Any, Dict, List, Optional

import vizro.models as vm
import vizro.plotly.express as px
from dash import dcc
from vizro import Vizro
from vizro.actions import export_data, filter_interaction
from vizro.managers._model_manager import ModelID
from vizro.models.types import capture
from vizro.tables import dash_ag_grid

df = px.data.gapminder().query("year == 2007")
default_card_text = "Click on a cell in the table to filter the scatter plot."


class CustomDashboard(vm.Dashboard):
    """Custom Dashboard model which keeps ag_grid clicked data."""

    def build(self):
        dashboard_build_obj = super().build()
        dashboard_build_obj.children.append(dcc.Store(id="global_data_store"))
        return dashboard_build_obj


# Just a util function
def _build_card_text_message(grid_cell_clicked: Optional[Dict] = None):
    if grid_cell_clicked:
        return f"""
            "Scatter" plot filtered by:

            (column -> value):

            "**{grid_cell_clicked.get('colId')}**" -> "**{grid_cell_clicked.get('value')}**"
         """
    return default_card_text


# TODO-AV2-OQ: It doesn't seem possible to achieve this, since _action._get_callback_mapping can't reconcile
#  self.inputs (List[States]) and self.function.inputs (Dict[str, List[State]]) at the same time. There are many ways
#  to solve this, but it's not clear which one is the best.

# TODO-AV-OQ: It seems like the only way to achieve a proper overwrite of the predefined action is to really inherit it
#  from the base predefined action. In that case, it will be taken into account while applying other predefined actions.
#  Should we introduce something like @capture("filter_interaction") then?
#  See `04_taking_custom_filter_into_account.py` for more.
@capture("action")
def custom_filter_interaction(
    targets: Optional[List[ModelID]] = None, grid_cell_clicked: Optional[Dict] = None, **inputs: Dict[str, Any]
):
    return {
        "card_children": _build_card_text_message(grid_cell_clicked=grid_cell_clicked),
        "global_data_store_data": grid_cell_clicked,
        **filter_interaction.pure_function(targets=targets, **inputs),
    }


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
                    actions=[
                        vm.Action(
                            function=custom_filter_interaction(targets=["scatter"]),
                            inputs=["underlying_ag_grid.cellClicked"],
                            outputs=["card.children", "global_data_store.data"],
                        ),
                    ],
                ),
                vm.Graph(
                    id="scatter", figure=px.scatter(df, x="gdpPercap", y="lifeExp", size="pop", color="continent")
                ),
                vm.Button(text="Export data", actions=[vm.Action(function=export_data(targets=["scatter"]))]),
            ],
            controls=[
                vm.Filter(column="continent", targets=["scatter"]),
                vm.Parameter(selector=vm.RadioItems(options=["gdpPercap", "lifeExp"]), targets=["scatter.x"]),
            ],
        ),
        vm.Page(
            title="Page 2",
            components=[vm.Graph(figure=px.scatter(df, x="gdpPercap", y="lifeExp", color="continent"))],
            controls=[vm.Filter(column="continent")],
        ),
    ]
)


if __name__ == "__main__":
    Vizro().build(dashboard).run()
