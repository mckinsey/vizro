"""Rough example used by developers."""

from typing import Any, Dict, List, Optional

import vizro.models as vm
import vizro.plotly.express as px
from dash import Output, State
from vizro import Vizro
from vizro.actions import export_data, filter_interaction
from vizro.managers._model_manager import ModelID
from vizro.models.types import capture
from vizro.tables import dash_ag_grid

df_gapminder = px.data.gapminder().query("year == 2007")
default_card_text = "Click on a cell in the table to filter the scatter plot."


# Just a util function
def _build_card_text_message(grid_cell_clicked: Optional[Dict] = None):
    if grid_cell_clicked:
        return f"""
            "Scatter" plot filtered by:

            column: **{grid_cell_clicked.get('colId')}**

            value: "**{grid_cell_clicked.get('value')}**"
         """
    return default_card_text


# Pure custom action to update card text with grid clicked data.
@capture("action")
def update_card_with_grid_clicked_data(grid_cell_clicked: Optional[Dict] = None):
    return _build_card_text_message(grid_cell_clicked=grid_cell_clicked)


# 1. Overwriting the filter_interaction action by overwriting only the pure_function
# TODO-AV2-OQ: It doesn't seem possible to achieve this, since _action._get_callback_mapping can't reconcile
#  self.inputs (List[States]) and self.function.inputs (Dict[str, List[State]]) at the same time. There is many ways
#  to solve this, but it's not clear which one is the best.
@capture("action")
def overwritten_filter_interactions_1(
    targets: Optional[List[ModelID]] = None, card_cellClicked: Optional[Dict] = None, **inputs: Dict[str, Any]
):
    return {
        "card_children": _build_card_text_message(grid_cell_clicked=grid_cell_clicked),
        **filter_interaction.pure_function(targets=targets, **inputs),
    }


# 2. Overwriting the filter_interaction action by inheriting FilterInteractionAction


# This also works:
# from vizro.actions.filter_interaction_action import FilterInteractionAction
# class OverwrittenFilterInteractions2(FilterInteractionAction):
class OverwrittenFilterInteractions2(filter_interaction):
    @staticmethod
    def pure_function(targets: list = None, grid_cell_clicked: dict = None, **kwargs):
        return {
            "card_children": _build_card_text_message(grid_cell_clicked=grid_cell_clicked),
            # TODO-AV2-OQ: Is it possible to get rid of 'targets=targets' (and potentially **kwargs) since targets
            #  should already be attached (added as partial arguments) within
            #  super()._post_init (self._arguments["targets"] = targets)?
            **filter_interaction.pure_function(targets=targets, **kwargs),
        }

    @property
    def inputs(self):
        return {
            "grid_cell_clicked": State("underlying_ag_grid", "cellClicked"),
            **super().inputs,
        }

    @property
    def outputs(self):
        return {
            "card_children": Output("card", "children"),
            **super().outputs,
        }


dashboard = vm.Dashboard(
    pages=[
        vm.Page(
            title="Ag Grid - Filter interaction",
            layout=vm.Layout(grid=[[0], [1], [1], [1], [2], [2], [2], [3]]),
            components=[
                vm.Card(
                    id="card",
                    text=default_card_text,
                ),
                vm.AgGrid(
                    id="ag_grid",
                    figure=dash_ag_grid(id="underlying_ag_grid", data_frame=df_gapminder),
                    actions=[
                        # vm.Action(
                        #     id="filter_interaction_action",
                        #     function=filter_interaction(
                        #         targets=[
                        #             "scatter",
                        #             "scatter_from_page_2",
                        # ]
                        # )
                        # ),
                        # Implementing updating card with grid clicked data as the independent action.
                        # vm.Action(
                        #     function=update_card_with_grid_clicked_data(),
                        #     inputs=["underlying_ag_grid.cellClicked"],
                        #     outputs=["card.children"],
                        # ),
                        # Now, let's try to implement updating card text by overwriting the filter_interaction action
                        # 1. Overwriting the filter_interaction action by overwriting only the pure_function
                        # vm.Action(
                        #     function=overwritten_filter_interactions_1(targets=["scatter"]),
                        #     inputs=["underlying_ag_grid.cellClicked"],
                        #     outputs=["card.children"],
                        # ),
                        # 2. Overwriting the filter_interaction action by inheritance.
                        vm.Action(
                            function=OverwrittenFilterInteractions2(targets=["scatter"]),
                        ),
                    ],
                ),
                vm.Graph(
                    id="scatter",
                    figure=px.scatter(
                        df_gapminder,
                        x="gdpPercap",
                        y="lifeExp",
                        size="pop",
                        color="continent",
                    ),
                ),
                vm.Button(
                    text="Export data",
                    actions=[
                        vm.Action(
                            function=export_data(
                                targets=[
                                    "scatter",
                                    # "scatter_from_page_2",
                                ]
                            )
                        ),
                    ],
                ),
            ],
            controls=[
                # TODO-AV2-TICKET-NEW: Overwrite filter function so it cancels the card.children changes too.
                # TODO-AV2-TICKET-CREATED: Attach the 'update_card_with_grid_clicked_data' action after
                #  the default filter action.
                vm.Filter(targets=["scatter"], column="continent"),
                vm.Parameter(targets=["scatter.x"], selector=vm.RadioItems(options=["gdpPercap", "lifeExp"])),
            ],
            # TODO-AV2-TICKET-CREATED: Try to attach the custom action that clicks data after the update_figures action.
        ),
        vm.Page(
            title="Page 2",
            components=[
                vm.Graph(
                    id="scatter_from_page_2",
                    figure=px.scatter(df_gapminder, x="gdpPercap", y="lifeExp", color="continent"),
                ),
            ],
            controls=[vm.Filter(column="continent")],
        ),
    ]
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
