# flake8: noqa
"""Customising (overwriting) predefined actions with inheriting.
    1. What's new?
        - It's possible to modify the predefined action behaviour. This could be used to:
            - Adjust predefined action's outputs returned value.
            - Add additional inputs into the action's function.
            - Add additional outputs which are returned from the action's function.
    2. Example below shows how not to lose the clicked data from ag_grid when the page is changed, but this time, using
        the power of customising predefined actions. Remember that every action is one http request to the server, so
        it's important to keep the number of actions as low as possible. In this example, we're replicating the example
        from the `02_overwriting_default_actions`, but using the customised actions to keep number of actions low.
        How it works:
        - Clicking an ag_grid cell:
            1. Applies filter interaction but also stores the clicked data into the global store and card component.
        - Navigating to the Page_1
            1. Takes the global store into account while applying update_figures action. It updates card component too.
"""

from typing import Any, Dict, List, Optional

import dash_ag_grid as dag
import vizro.models as vm
import vizro.plotly.express as px
from dash import Output, State, ctx, dcc
from vizro import Vizro
from vizro.actions import export_data, filter_interaction, update_figures
from vizro.managers._model_manager import ModelID
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


class CustomFilterInteraction(filter_interaction):
    """Action which stores the clicked data into the global store. It updates card component too."""

    @staticmethod
    def pure_function(
        targets: Optional[List[ModelID]] = None,
        grid_cell_clicked: Optional[Dict] = None,
        **inputs: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "card_children": _build_card_text_message(grid_cell_clicked=grid_cell_clicked),
            "global_data_store": grid_cell_clicked,
            # TODO-AV2-OQ: Is it possible to get rid of 'targets=targets' (and potentially **inputs) since targets
            #  should already be attached (added as partial arguments) within
            #  super()._post_init (self._arguments["targets"] = targets)?
            **filter_interaction.pure_function(targets=targets, **inputs),
        }

    @property
    def inputs(self):
        return {
            # Technically, we don't need to add 'underlying_ag_grid.cellClicked' here and we can fetch it directly from
            # **inputs: Dict[str, Any], but it's added for clarity.
            "grid_cell_clicked": State("underlying_ag_grid", "cellClicked"),
            **super().inputs,
        }

    @property
    def outputs(self):
        # Adjusting 'outputs' enables that everything regarding the standard filter interaction stay same, plus we're
        # adding 'global_data_store' and 'card_children' outputs.
        return {
            "card_children": Output("card", "children"),
            "global_data_store": Output("global_data_store", "data"),
            **super().outputs,
        }


class CustomUpdateFigures(update_figures):
    """Action which takes the global store into account while applying update_figures action. It updates card too."""

    @staticmethod
    def pure_function(
        targets: Optional[List[ModelID]] = None,
        global_data_store: Optional[Dict] = None,
        **inputs: Dict[str, Any],
    ) -> Dict[str, Any]:
        # This adjustment is not needed now, but it will probably be the way how to adjust inputs in the future.
        # inputs['filter_interaction'][0]['cellClicked'] = global_data_store

        # This adjustment potentially won't be necessary anymore once we solve the following to-do from
        # filter_action.py: "Consider the following inputs ctx form: ..."
        ctx.args_grouping["external"]["filter_interaction"][0]["cellClicked"]["value"] = global_data_store

        return_value = {
            "card_children": _build_card_text_message(grid_cell_clicked=global_data_store),
            **filter_interaction.pure_function(targets=targets, **inputs),
        }
        # Setting the cellClicked like this: `return_value["ag_grid"].cellClicked = global_data_store` doesn't work.
        # We need to set it like this:
        ag_grid_props = return_value["ag_grid"].to_plotly_json()["props"]
        ag_grid_props["cellClicked"] = global_data_store
        return_value["ag_grid"] = dag.AgGrid(**ag_grid_props)
        return return_value

    @property
    def inputs(self):
        return {
            "global_data_store": State("global_data_store", "data"),
            **super().inputs,
        }

    @property
    def outputs(self):
        return {
            "card_children": Output("card", "children", allow_duplicate=True),
            **super().outputs,
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
                        vm.Action(function=CustomFilterInteraction(targets=["scatter"])),
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
            actions=[vm.Action(function=CustomUpdateFigures())],
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
