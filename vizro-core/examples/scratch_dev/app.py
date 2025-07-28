# # Vizro is an open-source toolkit for creating modular data visualization applications.
# # check out https://github.com/mckinsey/vizro for more info about Vizro
# # and checkout https://vizro.readthedocs.io/en/stable/ for documentation.

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_ag_grid, dash_data_table
from vizro.actions import filter_interaction, export_data
from vizro.models.types import capture
from time import sleep
from vizro.managers import data_manager

df_gapminder = px.data.gapminder().query("year == 2007")


def load_dynamic_gapminder_data(continent: str = "Europe"):
    return df_gapminder[df_gapminder["continent"] == continent]


data_manager["dynamic_df_gapminder_arg"] = load_dynamic_gapminder_data
data_manager["dynamic_df_gapminder"] = lambda: df_gapminder


@capture("action")
def my_custom_action(t: int):
    """Custom action."""
    sleep(t)


#
#
# page_1 = vm.Page(
#     title="My first dashboard",
#     components=[
#         vm.Graph(figure=px.scatter("dynamic_df_gapminder", x="gdpPercap", y="lifeExp", size="pop", color="continent")),
#         # vm.Graph(figure=px.histogram(df_gapminder, x="lifeExp", color="continent", barmode="group")),
#     ],
#     controls=[
#         vm.Filter(column="continent", selector=vm.RadioItems()),
#     ],
# )

# TEST NEW ACTIONS SYNTAX
# page_2 = vm.Page(
#     title="Simple custom action",
#     components=[
#         vm.Graph(figure=px.scatter(df_gapminder, x="gdpPercap", y="lifeExp", size="pop", color="continent")),
#         vm.Button(
#             text="Export data",
#             actions=[
#                 export_data(id="a1"),
#                 vm.Action(id="a2", function=my_custom_action(t=2)),
#                 export_data(file_format="xlsx", id="a3"),
#             ],
#         ),
#     ],
#     controls=[
#         vm.Filter(column="continent", selector=vm.RadioItems()),
#     ],
# )
#
# page_3 = vm.Page(
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
#             actions=[filter_interaction(targets=["scatter_relation_2007"])],
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
#     controls=[
#         vm.Filter(column="continent"),
#     ],
# )
#
# page_4 = vm.Page(
#     title="Filter interaction grid",
#     components=[
#         vm.AgGrid(
#             id="grid",
#             figure=dash_ag_grid(data_frame=df_gapminder),
#             actions=[vm.Action(function=filter_interaction(targets=["scatter_relation_2007b"]))],
#         ),
#         vm.Graph(
#             id="scatter_relation_2007b",
#             figure=px.scatter(
#                 df_gapminder,
#                 x="gdpPercap",
#                 y="lifeExp",
#                 size="pop",
#                 color="continent",
#             ),
#         ),
#     ],
#     controls=[
#         vm.Filter(column="continent"),
#     ],
# )
#
# page_5 = vm.Page(
#     title="Dynamic filter",
#     components=[
#         vm.Graph(
#             figure=px.scatter("dynamic_df_gapminder", x="gdpPercap", y="lifeExp", size="pop", color="continent"),
#         ),
#     ],
#     controls=[
#         vm.Filter(id="filter", column="continent", selector=vm.RadioItems(id="selector")),
#     ],
# )
#
# # TODO NOW: think about whether in future this case should be dealt with as a single serverside callback that updates
# # filter and relevant graphs on page (as now) or instead more like an interact with two chained callbacks
page_6 = vm.Page(
    title="DataFrame Parameter",
    components=[
        vm.Graph(
            id="page_6_graph", figure=px.box("dynamic_df_gapminder_arg", x="continent", y="lifeExp", color="continent")
        ),
    ],
    controls=[
        vm.Filter(id="filter", column="continent", selector=vm.Dropdown(id="filter_selector")),
        vm.Parameter(
            targets=["page_6_graph.data_frame.continent"],
            selector=vm.RadioItems(options=list(set(df_gapminder["continent"])), value="Europe", id="parameter"),
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page_6])

# TODO NOW: check dropdown, checklist
# TODO NOW: roll out to all other dynamic components
# TODO NOW: check url params
# TODO NOW: check vizro_download, vizro_url

if __name__ == "__main__":
    Vizro().build(dashboard).run(
        debug=True,
        use_reloader=False,
    )
