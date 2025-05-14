# # Vizro is an open-source toolkit for creating modular data visualization applications.
# # check out https://github.com/mckinsey/vizro for more info about Vizro
# # and checkout https://vizro.readthedocs.io/en/stable/ for documentation.

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_ag_grid, dash_data_table

tips = px.data.tips()

page1 = vm.Page(
    title="LAYOUT_FLEX_WRAP_ANimport vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import export_data
from vizro.models.types import capture
from time import sleep

from vizro.tables import dash_ag_grid

#
# @capture("action")
# def my_custom_action(t: int):
#     """Custom action."""
#     sleep(t)
#
#
# df = px.data.iris()
#
# page = vm.Page(
#     title="Simple custom action",
#     components=[
#         vm.Graph(figure=px.scatter(df, x="sepal_length", y="petal_width", color="species")),
#         vm.Button(
#             text="Export data",
#             actions=[
#                 vm.Action(function=export_data()),
#                 vm.Action(function=my_custom_action(t=2)),
#                 vm.Action(function=export_data(file_format="xlsx")),
#             ],
#         ),
#     ],
# )
#
# # dashboard = vm.Dashboard(pages=[page])
#
# import vizro.plotly.express as px
# from vizro import Vizro
# import vizro.models as vm
#
# df = px.data.iris()
#
# page2 = vm.Page(
#     title="My first dashboard",
#     components=[
#         vm.Graph(figure=px.scatter(df, x="sepal_length", y="petal_width", color="species")),
#         vm.Graph(figure=px.histogram(df, x="sepal_width", color="species")),
#     ],
#     controls=[
#         vm.Filter(column="species"),
#     ],
# )
# import vizro.models as vm
# import vizro.plotly.express as px
# from vizro import Vizro
# from vizro.actions import filter_interaction
#
# df_gapminder = px.data.gapminder().query("year == 2007")
# page3 = vm.Page(
#     title="Filter interaction graph",
#     components=[
#         vm.Graph(
#             figure=px.box(
#                 df_gapminder,
#                 x="continent",
#                 y="lifeExp",
#                 color="continent",
#                 custom_data=["continent"],
#             ),
#             actions=[vm.Action(function=filter_interaction(targets=["scatter_relation_2007"]))],
#         ),
#         vm.Graph(
#             id="scatter_relation_2007",
#             figure=px.scatter(
#                 df_gapminder,
#                 x="gdpPercap",
#                 y="lifeExp",
#                 size="pop",
#                 color="continent",
#             ),
#         ),
#     ],
# )
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import filter_interaction

df_gapminder = px.data.gapminder().query("year == 2007")
page4 = vm.Page(
    title="Filter interaction grid",
    components=[
        vm.AgGrid(
            id="grid",
            figure=dash_ag_grid(data_frame=df_gapminder),
            actions=[vm.Action(function=filter_interaction(targets=["scatter_relation_2007b"]))],
        ),
        vm.Graph(
            id="scatter_relation_2007b",
            figure=px.scatter(
                df_gapminder,
                x="gdpPercap",
                y="lifeExp",
                size="pop",
                color="continent",
            ),
        ),
    ],
)


dashboard = vm.Dashboard(pages=[page4])

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
D_AG_GRID",
    layout=vm.Flex(wrap=True),
    components=[
        vm.AgGrid(id=f"outer_id_{i}", figure=dash_ag_grid(tips, id=f"inner_id_{i}", style={"width": 1000}))
        # vm.AgGrid(id=f"outer_id_{i}", figure=dash_ag_grid(tips, id=f"qwer", style={"width": 1000}))
        for i in range(3)
    ],
)

page2 = vm.Page(
    title="LAYOUT_FLEX_GAP_AND_TABLE",
    layout=vm.Flex(gap="40px"),
    # components=[vm.Table(figure=dash_data_table(tips, style_table={"width": "1000px"})) for i in range(3)],
    components=[
        vm.Table(figure=dash_data_table(tips, id=f"qwert_{i}", style_table={"width": "1000px"})) for i in range(3)
    ],
)

page3 = vm.Page(
    title="cross_id",
    layout=vm.Flex(gap="40px"),
    components=[
        vm.Table(figure=dash_data_table(tips, id="qwert", style_table={"width": "1000px"})),
        vm.AgGrid(figure=dash_ag_grid(tips, id="qwert", style={"width": 1000})),
    ],
)

dashboard = vm.Dashboard(pages=[page1, page2, page3])


if __name__ == "__main__":
    Vizro().build(dashboard).run()

## TO CHECK: also for figure and/or Graph?
