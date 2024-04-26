# flake8: noqa
"""Overwriting default actions examples.
    1. What's new?
        - Overwriting default filter/parameter actions have always been possible, but with the new
            actions implementation, overwriting of "on page load mechanism" is also possible.
        - By making `filter_action`, `parameter_action` and `update_figures` actions public,
            we achieve the new level of flexibility. This enables users to add some "pre-actions" before or
            "post-actions" after the filter action is triggered (sounds like "cascading filters"?).
            It's also possible to apply global stored controls values before the `update_figures` is triggered
            (sounds like "Enable shared filter values" and "Drill-through"?).
        - Complete overwriting of the default actions instead of appending configured actions to the actions chain seems
            as a better approach. One more reason for that could be that because sometimes we don’t want any action to
            be trigger (setting `actions=[]') from the Filter.selector or vm.Page (default is update_figures).
            See example: '05_01_adv_example_trigger_filtering_on_button_click.py'
    2. Example below shows how not to lose the clicked data from ag_grid when the page is changed.
        How it works:
        - Clicking an ag_grid cell app:
            1. Applies a standard filter interaction
            2. Stores the clicked data into the global store and updates the card component with the clicked data.
        - Navigating to the Page_1 app:
            1. Applies global store data to ag_grid cellClicked property and updates the card component
            2. Applies a standard "update_figures" action
            3. Applies global store data to ag_grid cellClicked property and updates the card component again.

"""

from typing import Dict, Optional

import vizro.models as vm
import vizro.plotly.express as px
from dash import dcc
from vizro import Vizro
from vizro.actions import export_data, filter_interaction, update_figures
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


@capture("action")
def apply_cell_clicked_data(grid_cell_clicked: Optional[Dict] = None):
    return grid_cell_clicked, _build_card_text_message(grid_cell_clicked=grid_cell_clicked)


dashboard = CustomDashboard(
    pages=[
        vm.Page(
            title="Page_1",
            layout=vm.Layout(grid=[[0], [1], [1], [1], [2], [2], [2], [3]]),
            components=[
                vm.Card(
                    id="card",
                    text=default_card_text,
                ),
                vm.AgGrid(
                    id="ag_grid",
                    figure=dash_ag_grid(id="underlying_ag_grid", data_frame=df),
                    actions=[
                        vm.Action(function=filter_interaction(targets=["scatter"])),
                        vm.Action(
                            function=apply_cell_clicked_data(),
                            inputs=["underlying_ag_grid.cellClicked"],
                            outputs=["global_data_store.data", "card.children"],
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
            actions=[
                # Example of overwriting the default `update_figures` action, where some custom behaviour is set
                # before and after the default `update_figures` action. This is the best example that shows why do we
                # need to expose all default actions as public.
                # Preparing the 'underlying_ag_grid.cellClicked' data before running the `update_figures` action is
                # important, so it takes the 'underlying_ag_grid.cellClicked' filter_interaction value into account.
                vm.Action(
                    # Small digression: Notice how Vizro custom actions are reusable. The same action's function
                    # ("apply_cell_clicked_data") is used inside the ag_grid.actions, but with different inputs/outputs.
                    function=apply_cell_clicked_data(),
                    inputs=["global_data_store.data"],
                    outputs=["underlying_ag_grid.cellClicked", "card.children"],
                ),
                # Apply filter/parameter/filter_interaction to all figures in the page.
                vm.Action(function=update_figures()),
                # Since update_figures doesn't preserve clicked data value, we need to apply it again.
                vm.Action(
                    function=apply_cell_clicked_data(),
                    inputs=["global_data_store.data"],
                    outputs=["underlying_ag_grid.cellClicked", "card.children"],
                ),
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
