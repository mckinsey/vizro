"""Rough example used by developers."""
from dash import Output

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import export_data, filter_interaction
from vizro.tables import dash_ag_grid
from vizro.models.types import capture
from vizro.managers._model_manager import ModelID
from typing import Any, Dict, List, Optional


df_gapminder = px.data.gapminder().query("year == 2007")
default_card_text = "Click on a cell in the table to filter the scatter plot."


# Just a util function
def _build_card_text_message(card_cellClicked: Optional[Dict] = None):
    if card_cellClicked:
        return f"""
            "Scatter" plot filtered by:

            column: **{card_cellClicked.get('colId')}**

            value: "**{card_cellClicked.get('value')}**"
         """
    return default_card_text


# Pure custom action to update card text with grid clicked data.
@capture("action")
def update_card_with_grid_clicked_data(card_cellClicked: Optional[Dict] = None):
    return _build_card_text_message(card_cellClicked=card_cellClicked)


# 1. Overwriting the filter_interaction action by overwriting only the pure_function
# TODO-AV2-OQ: It doesn't seem possible to achieve this, since _action._get_callback_mapping can't reconcile
#   self.inputs (List[States]) and self.function.inputs (Dict[str, List[State]]) at the same time.
@capture("action")
def overwritten_filter_interactions_1(
    targets: Optional[List[ModelID]] = None,
    card_cellClicked: Optional[Dict] = None,
    **inputs: Dict[str, Any]
):
    return {
        "card.children": _build_card_text_message(card_cellClicked=card_cellClicked),
        **filter_interaction.pure_function(targets=targets, **inputs),
    }

# 2. Overwriting the filter_interaction action by inheriting FilterInteractionAction
from vizro.actions.filter_interaction_action import FilterInteractionAction
from dash import Output, State


class OverwrittenFilterInteractions2(FilterInteractionAction):
    @staticmethod
    def pure_function(targets: list = None, card_cell_clicked: dict = None, **kwargs):
        return {
            "card_children": _build_card_text_message(card_cellClicked=card_cell_clicked),
            # TODO-AV2-OQ: Is it possible to get rid of 'targets=targets' (and potentially **kwargs) since targets
            #   should already be attached (added as partial arguments) within
            #   super()._post_init (self._arguments["targets"] = targets)?
            **FilterInteractionAction.pure_function(targets=targets, **kwargs),
        }

    @property
    def inputs(self):
        return {
            "card_cell_clicked": State("underlying_ag_grid", "cellClicked"),
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
                        #             # "scatter_from_page_2",
                        #         ]
                        #     )
                        # ),
                        # Implementing updating card with grid clicked data as the independent action.
                        vm.Action(
                            function=update_card_with_grid_clicked_data(),
                            inputs=["underlying_ag_grid.cellClicked"],
                            outputs=["card.children"],
                        ),
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
                # TODO-AV2-TICKET: 1. overwrite filter function so it cancels the card.children changes too.
                #   2. OR attach the 'update_card_with_grid_clicked_data' action after the default filter action.
                vm.Filter(targets=["scatter"], column="continent"),
                vm.Parameter(targets=["scatter.x"], selector=vm.RadioItems(options=["gdpPercap", "lifeExp"]))
            ],
            # TODO-AV2-TICKET: Try to attach the 'update_card_with_grid_clicked_data' action after update_figures action.
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
