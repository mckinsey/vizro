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


page_1 = vm.Page(
    title="My first dashboard - [1 guard]",
    components=[
        vm.Graph(id="page_1_graph", figure=px.histogram(df_gapminder, x="lifeExp", color="continent", barmode="group")),
    ],
    controls=[
        vm.Filter(id="page_1_filter", column="continent"),
    ],
)

# TEST NEW ACTIONS SYNTAX
page_2 = vm.Page(
    title="Export data -> custom sleep action -> export data - [1 guard]",
    components=[
        vm.Graph(id="page_2_graph", figure=px.scatter(df_gapminder, x="gdpPercap", y="lifeExp", size="pop", color="continent")),
        vm.Button(
            id="page_2_button",
            text="Export data",
            actions=[
                export_data(id="a1"),
                vm.Action(id="a2", function=my_custom_action(t=2)),
                export_data(file_format="xlsx", id="a3"),
            ],
        ),
    ],
    controls=[
        vm.Filter(id="page_2_filter", column="continent", selector=vm.RadioItems()),
    ],
)

page_3 = vm.Page(
    title="Filter interaction graph - [1 guard]",
    components=[
        vm.Graph(
            id="page_3_graph",
            figure=px.box(
                df_gapminder,
                x="continent",
                y="lifeExp",
                color="continent",
                custom_data=["continent"],
            ),
            actions=[filter_interaction(id="page_3_action", targets=["page_3_graph_2"])],
        ),
        vm.Graph(
            id="page_3_graph_2",
            figure=px.scatter(
                df_gapminder,
                x="gdpPercap",
                y="lifeExp",
                size="pop",
                color="continent",
            ),
        ),
    ],
    controls=[
        vm.Filter(id="page_3_filter", column="continent"),
    ],
)

page_4 = vm.Page(
    title="Filter interaction grid - [2 guards]",
    components=[
        vm.AgGrid(
            id="page_4_grid",
            figure=dash_ag_grid(data_frame=df_gapminder),
            actions=[vm.Action(function=filter_interaction(targets=["page_4_graph"]))],
        ),
        vm.Graph(
            id="page_4_graph",
            figure=px.scatter(
                df_gapminder,
                x="gdpPercap",
                y="lifeExp",
                size="pop",
                color="continent",
            ),
        ),
    ],
    controls=[
        vm.Filter(id="page_4_filter", column="continent"),
    ],
)

page_5 = vm.Page(
    title="Dynamic filter - [2 guards]",
    components=[
        vm.Graph(
            id="page_5_graph",
            figure=px.scatter("dynamic_df_gapminder", x="gdpPercap", y="lifeExp", size="pop", color="continent"),
        ),
    ],
    controls=[
        vm.Filter(id="page_4_dynamic_filter", column="continent", selector=vm.RadioItems(id="selector")),
    ],
)

page_6 = vm.Page(
    title="DataFrame Parameter - [2 guards]",
    components=[
        vm.Graph(
            id="page_6_graph", figure=px.box("dynamic_df_gapminder_arg", x="continent", y="lifeExp", color="continent")
        ),
    ],
    controls=[
        vm.Filter(id="page_6_filter", column="continent", selector=vm.Dropdown(id="page_6_filter_selector")),
        vm.Parameter(
            id="page_6_dfp_parameter",
            targets=["page_6_graph.data_frame.continent"],
            selector=vm.RadioItems(
                title="DFP - [1 guard]",
                options=list(set(df_gapminder["continent"])), value="Europe", id="page_6_dfp_selector"
            ),
        ),
    ],
)

page_7 = vm.Page(
    title="URL parameter filters - [2 guards on refresh]",
    components=[
        vm.Graph(
            id="page_7_graph",
            figure=px.scatter(df_gapminder, x="gdpPercap", y="lifeExp", size="pop", color="continent"),
        ),
    ],
    controls=[
        vm.Filter(id="page_7_filter", column="continent", show_in_url=True),
    ]
)


"""
Test cases:
1. navigate to page_8
2. refresh the page_8 (this made issues as filters in this process were changed by sync_url clientside callback)
3. change page_8_filter_1 and page_8_filter_2 values and check everything is ok
4. copy the part of the URL that contains page_8_filter_1 but not page_8_filter_2. Open it in the new browser tab.
5. check that page_8_filter_1 is set to the value from the URL and page_8_filter_2 is set to the default value.
6. check that both filters are shown in the URL.
7. change page_8_filter_1 and see how the filter-action is triggered.
8. change page_8_filter_2 and see how the filter-action is triggered. (this was the problem if 
    guardian is not changed from the sync_url clientside callback)
"""
page_8 = vm.Page(
    title="Multi URL parameter filters - [3 guards or refresh]",
    components=[
        vm.Graph(
            id="page_8_graph",
            figure=px.scatter(df_gapminder, x="gdpPercap", y="lifeExp", size="pop", color="continent"),
        ),
    ],
    controls=[
        vm.Filter(id="page_8_filter_1", column="continent", show_in_url=True, selector=vm.RadioItems()),
        vm.Filter(id="page_8_filter_2", column="continent", show_in_url=True, selector=vm.RadioItems()),
    ]
)


page_9 = vm.Page(
    title="DataFrame Parameter and URL Filter- [2 guards]",
    components=[
        vm.Graph(
            id="page_9_graph", figure=px.box("dynamic_df_gapminder_arg", x="continent", y="lifeExp", color="continent")
        ),
    ],
    controls=[
        vm.Filter(id="page_9_filter", column="continent", selector=vm.Dropdown(id="page_9_filter_selector"), show_in_url=True),
        vm.Parameter(
            id="page_9_dfp_parameter",
            targets=["page_9_graph.data_frame.continent"],
            selector=vm.RadioItems(
                title="DFP - [1 guard]",
                options=list(set(df_gapminder["continent"])), value="Europe", id="page_9_dfp_selector"
            ),
        ),
    ],
)

# TODO: Solve bug when DFP changes and after that filter changes. Correct number of guards on DFP.
page_10 = vm.Page(
    title="DFP + Dynamic filter + URL + filter interaction - [5 guards on refresh]",
    components=[
        vm.AgGrid(
            id="page_10_grid",
            figure=dash_ag_grid(data_frame="dynamic_df_gapminder_arg"),
            actions=[vm.Action(function=filter_interaction(id="page_10_filter_interaction", targets=["page_10_graph"]))],
        ),
        vm.Graph(
            id="page_10_graph",
            figure=px.scatter("dynamic_df_gapminder_arg", x="gdpPercap", y="lifeExp", size="pop", color="continent"),
        ),
    ],
    controls=[
        # TODO: Try with different selectors
        vm.Filter(
            id="page_10_filter",
            column="continent",
            selector=vm.Dropdown(id="page_10_filter_selector"),
            show_in_url=True
        ),
        vm.Parameter(
            id="page_10_dfp_parameter",
            targets=[
                "page_10_grid.data_frame.continent",
                "page_10_graph.data_frame.continent",
            ],
            selector=vm.RadioItems(
                title="DFP - [3 guards]",
                options=list(set(df_gapminder["continent"])), value="Europe", id="page_10_dfp_selector"
            ),
            show_in_url=True
        ),
    ]
)

dashboard = vm.Dashboard(pages=[page_1, page_2, page_3, page_4, page_5, page_6, page_7, page_8, page_9, page_10])

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
