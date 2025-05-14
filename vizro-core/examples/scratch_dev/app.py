import vizro.models as vm
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
