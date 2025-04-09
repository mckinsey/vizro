import datetime
import time

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import export_data, filter_interaction
from vizro.managers import data_manager
from vizro.models.types import capture
from vizro.tables import dash_ag_grid

df_gapminder = px.data.gapminder().query("year == 2007")

page_1 = vm.Page(
    title="Built in actions",
    layout=dict(grid=[[0, 1], [2, 3]]),
    components=[
        # vm.Button(
        #     text="asdf",
        #     actions=[filter_interaction(targets=["scatter_relation_2007"])],
        #     # actions=[vm.Action(function=filter_interaction(targets=["scatter_relation_2007"]))],  # TODO NOW CHECK
        # ),
        vm.Graph(
            figure=px.box(
                df_gapminder,
                x="continent",
                y="lifeExp",
                color="continent",
                custom_data=["continent"],
            ),
            actions=[filter_interaction(targets=["scatter_relation_2007"])],
            # actions=[vm.Action(function=filter_interaction(targets=["scatter_relation_2007"]))],  # TODO NOW CHECK
        ),
        vm.Graph(
            id="scatter_relation_2007",
            figure=px.scatter(
                df_gapminder,
                x="gdpPercap",
                y="lifeExp",
                size="pop",
                color="continent",
            ),
        ),
        vm.Button(
            id="button",
            text="Export data to CSV",
            # actions=[export_data(targets=["scatter_relation_2007"], runtime_arg="button.n_clicks")],
            actions=[vm.Action(function=export_data(targets=["scatter_relation_2007"]))],
            # TODO NOW CHECK
        ),
        vm.Button(
            id="button2",
            text="Export data to Excel",
            actions=[export_data(targets=["scatter_relation_2007"], file_format="xlsx")],
            # actions=[
            #     vm.Action(
            #         function=export_data(
            #             targets=["scatter_relation_2007"],
            #             runtime_arg="button2.n_clicks",
            #             file_format="xlsx"
            #         )
            #     )
            # ],
            # TODO NOW CHECK
        ),
    ],
    controls=[
        vm.Filter(column="continent"),
        vm.Parameter(
            targets=["scatter_relation_2007.color"],
            selector=vm.RadioItems(options=["continent", "pop"]),
        ),
    ],
)


@capture("action")
# To test legacy=True
# def my_custom_action(points_data, _controls=None):
def my_custom_action(points_data, _controls):
    """Custom action."""
    clicked_point = points_data["points"][0]
    x, y = clicked_point["x"], clicked_point["y"]
    card_1_text = f"Clicked point has sepal length {x}, petal width {y}."
    card_2_text = f"Controls are `{_controls}`"
    return card_1_text, card_2_text


# from typing import Literal
# from vizro.actions import AbstractAction

# class f(AbstractAction):
#     type: Literal["f"] = "f"
#     points_data: str
#     swap: bool = False
#
#     def function(self, points_data, _controls):
#         """Custom action."""
#         clicked_point = points_data["points"][0]
#         x, y = clicked_point["x"], clicked_point["y"]
#         card_1_text = f"Clicked point has sepal length {x}, petal width {y}."
#         card_2_text = f"_Controls are `{_controls}`"
#         return card_1_text, card_2_text
#
#     @property
#     def outputs(self):
#         return (
#             ["my_card_2.children", "my_card_1.children"] if self.swap else ["my_card_1.children", "my_card_2.children"]
#         )
#
#
# from vizro.models._action._actions_chain import ActionsChain
#
# vm.Graph.add_type("actions", f)
# ActionsChain.add_type("actions", f)

# @capture("action")
# def my_custom_action():
#     """Custom action."""
#     card_1_text = card_2_text = str(datetime.datetime.now().time())
#     return card_1_text, card_2_text

# TODO NOW CHECK: current docs examples
df = px.data.iris()

page_2 = vm.Page(
    title="Example of a custom action with UI inputs and outputs",
    layout=vm.Layout(
        grid=[
            [0, 0],
            [0, 0],
            [0, 0],
            [1, 2],
        ],
        row_gap="25px",
    ),
    components=[
        vm.Graph(
            id="scatter_chart",
            figure=px.scatter(df, x="sepal_length", y="petal_width", color="species", custom_data=["species"]),
            actions=[
                vm.Action(
                    function=my_custom_action("scatter_chart.clickData"),
                    # TODO NOW CHECK: make sure user-specified argument continues to take precedence
                    #     # function=my_custom_action("scatter_chart.clickData", controls="my_card_1.children"),
                    #     # TODO NOW CHECK: test to make sure this old way continues to work
                    #     # function=my_custom_action(),
                    #     # function=my_custom_action(t=4),
                    #     # inputs=["scatter_chart.clickData"],
                    outputs=["my_card_1.children", "my_card_2.children"],
                ),
                # f(swap=True, points_data="scatter_chart.clickData")
            ],
        ),
        vm.Card(id="my_card_1", text="Click on a point on the above graph."),
        vm.Card(id="my_card_2", text="Click on a point on the above graph."),
    ],
    controls=[vm.Filter(column="species", selector=vm.Dropdown(title="Species"))],
)


########### MS EXAMPLE ###########
@capture("action")
def click_counts_heatmap(cell_data: dict):
    print(cell_data)
    return f"cell_data: {cell_data}"


def load_gapminder(continent: str):
    df = px.data.gapminder()
    time.sleep(2)
    return df[df["continent"] == continent]


df_gapminder = px.data.gapminder()

data_manager["gapminder"] = load_gapminder

page_3 = vm.Page(
    title="Experiment with data loading",
    components=[
        vm.AgGrid(
            id="grid",
            figure=dash_ag_grid(data_frame=df_gapminder),
            actions=[
                vm.Action(function=click_counts_heatmap("grid.cellClicked"), outputs=["card_cross_filter.children"])
            ],
        ),
        vm.Graph(
            id="slow_load_chart",
            figure=px.scatter("gapminder", x="gdpPercap", y="lifeExp", color="continent"),
        ),
        vm.Card(id="card_cross_filter", text="Click on a point on the above table."),
    ],
    controls=[
        vm.Parameter(
            targets=["slow_load_chart.data_frame.continent"],
            selector=vm.RadioItems(options=["Africa", "Americas", "Asia", "Europe", "Oceania"]),
        )
    ],
    layout=vm.Layout(
        grid=[[0, 1], [0, 1], [2, 2]],
    ),
)
########### MS EXAMPLE ###########

dashboard = vm.Dashboard(pages=[page_1, page_2, page_3])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
