# # Vizro is an open-source toolkit for creating modular data visualization applications.
# # check out https://github.com/mckinsey/vizro for more info about Vizro
# # and checkout https://vizro.readthedocs.io/en/stable/ for documentation.

from dash import callback, Input, Output, dcc
import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_ag_grid, dash_data_table
from vizro.actions import filter_interaction, export_data
from vizro.models.types import capture
from time import sleep
from vizro.managers import data_manager
from vizro.models.types import capture

df_gapminder = px.data.gapminder().query("year == 2007")
df_gapminder["date_column"] = pd.date_range(start=pd.to_datetime("2025-01-01"), periods=len(df_gapminder), freq="D")
df_gapminder["number_column"] = range(len(df_gapminder))
df_gapminder["is_europe"] = df_gapminder["continent"] == "Europe"


def load_dynamic_gapminder_data(continent: str = "Europe"):
    return df_gapminder[df_gapminder["continent"] == continent]


data_manager["dynamic_df_gapminder_arg"] = load_dynamic_gapminder_data
data_manager["dynamic_df_gapminder"] = lambda: df_gapminder


@capture("action")
def my_custom_action(t: int):
    """Custom action."""
    sleep(t)


page_1 = vm.Page(
    title="My first dashboard - [0 guards]",
    components=[
        vm.Graph(id="page_1_graph", figure=px.histogram(df_gapminder, x="lifeExp", color="continent", barmode="group")),
    ],
    controls=[
        vm.Filter(id="page_1_filter", column="continent", selector=vm.Dropdown(id="page_1_filter_selector")),
    ],
)

page_2 = vm.Page(
    title="Export data -> custom sleep action -> export data - [0 guard]",
    components=[
        vm.Graph(
            id="page_2_graph",
            figure=px.scatter(df_gapminder, x="gdpPercap", y="lifeExp", size="pop", color="continent"),
        ),
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
        vm.Filter(id="page_2_filter", column="continent", selector=vm.RadioItems(id="page_2_filter_selector")),
    ],
)

page_3 = vm.Page(
    title="Filter interaction graph - [0 guard]",
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
            actions=filter_interaction(id="page_3_action", targets=["page_3_graph_2"]),
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
        vm.Filter(id="page_3_filter", column="continent", selector=vm.Dropdown(id="page_3_filter_selector")),
    ],
)

page_4 = vm.Page(
    title="Filter interaction grid - [1 guard]",
    components=[
        vm.AgGrid(
            id="page_4_grid",
            figure=dash_ag_grid(data_frame=df_gapminder),
            actions=filter_interaction(targets=["page_4_graph"]),
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
        vm.Filter(
            id="page_4_filter",
            column="continent",
            targets=["page_4_grid"],
            selector=vm.Dropdown(title="Filter AgGrid - [1 guard]", id="page_4_filter_selector"),
        ),
    ],
)

page_5 = vm.Page(
    title="Dynamic filter - [1 guard]",
    components=[
        vm.Graph(
            id="page_5_graph",
            figure=px.scatter("dynamic_df_gapminder", x="gdpPercap", y="lifeExp", size="pop", color="continent"),
        ),
    ],
    controls=[
        vm.Filter(id="page_5_dynamic_filter", column="continent", selector=vm.RadioItems(id="page_5_filter_selector")),
    ],
)

page_6 = vm.Page(
    title="DataFrame Parameter - [1 guard]",
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
                options=list(set(df_gapminder["continent"])),
                value="Europe",
                id="page_6_dfp_selector",
            ),
        ),
    ],
)

page_7 = vm.Page(
    title="URL parameter filters - [1 guard on refresh]",
    components=[
        vm.Graph(
            id="page_7_graph",
            figure=px.scatter(df_gapminder, x="gdpPercap", y="lifeExp", size="pop", color="continent"),
        ),
    ],
    controls=[
        vm.Filter(
            id="page_7_filter", column="continent", show_in_url=True, selector=vm.Dropdown(id="page_7_filter_selector")
        ),
    ],
)


"""
Test case:
1. navigate to page_8
2. refresh the page_8 (this previously caused issues as filters in this process were changed by sync_url callback)
3. change page_8_filter_1 and page_8_filter_2 values and check everything is ok
4. copy the part of the URL that contains page_8_filter_1 but not page_8_filter_2. Open it in the new browser tab.
5. check that page_8_filter_1 is set to the value from the URL and page_8_filter_2 is set to the default value.
6. check that both filters are shown in the URL.
7. change page_8_filter_1 and see how the filter-action is triggered.
8. change page_8_filter_2 and see how the filter-action is triggered. (this previously caused issues. It's solved
   by setting the guard to True from the url_sync callback)
"""
page_8 = vm.Page(
    title="Multi URL parameter filters - [2 guards or refresh]",
    components=[
        vm.Graph(
            id="page_8_graph",
            figure=px.scatter(df_gapminder, x="gdpPercap", y="lifeExp", size="pop", color="continent"),
        ),
    ],
    controls=[
        vm.Filter(
            id="page_8_filter_1",
            column="continent",
            show_in_url=True,
            selector=vm.RadioItems(id="page_8_filter_1_selector"),
        ),
        vm.Filter(
            id="page_8_filter_2",
            column="continent",
            show_in_url=True,
            selector=vm.RadioItems(id="page_8_filter_2_selector"),
        ),
    ],
)


page_9 = vm.Page(
    title="DataFrame Parameter and URL Filter - [2 guards on refresh]",
    components=[
        vm.Graph(
            id="page_9_graph", figure=px.box("dynamic_df_gapminder_arg", x="continent", y="lifeExp", color="continent")
        ),
    ],
    controls=[
        vm.Filter(
            id="page_9_dropdown_filter",
            column="continent",
            selector=vm.Dropdown(id="page_9_dropdown_filter_selector"),
            show_in_url=True,
        ),
        vm.Parameter(
            id="page_9_dfp_parameter",
            targets=["page_9_graph.data_frame.continent"],
            selector=vm.RadioItems(
                title="DFP - [1 guard]",
                options=list(set(df_gapminder["continent"])),
                value="Europe",
                id="page_9_dfp_selector",
            ),
        ),
    ],
)

"""
Test case:
1. navigate to page_10
2. refresh the page_10
3. change page_10_dfp_parameter value and check everything is ok
4. change page_10_filter value and check everything is ok.
   This used to fail because the "sync_url" callback made that the guard callback doesn't trigger.
   The issue: when the filter value was changed for the first time after a DFP update, nothing happened.
   Fix: in the "url_sync" callback, set "guard.data = False" for these filters so the filter change is detected.
"""
page_10 = vm.Page(
    title="DFP + Dynamic filter + URL + filter interaction - [4 guards on refresh]",
    components=[
        vm.AgGrid(
            id="page_10_grid",
            figure=dash_ag_grid(data_frame="dynamic_df_gapminder_arg"),
            actions=[
                vm.Action(function=filter_interaction(id="page_10_filter_interaction", targets=["page_10_graph"]))
            ],
        ),
        vm.Graph(
            id="page_10_graph",
            figure=px.scatter("dynamic_df_gapminder_arg", x="gdpPercap", y="lifeExp", size="pop", color="continent"),
        ),
    ],
    controls=[
        vm.Filter(
            id="page_10_filter",
            column="continent",
            selector=vm.Dropdown(title="Filter AgGrid - [1 guard]", id="page_10_filter_selector"),
            show_in_url=True,
        ),
        vm.Parameter(
            id="page_10_dfp_parameter",
            targets=[
                "page_10_grid.data_frame.continent",
                "page_10_graph.data_frame.continent",
            ],
            selector=vm.RadioItems(
                id="page_10_dfp_parameter_selector",
                title="DFP - [2 guards]",
                options=list(set(df_gapminder["continent"])),
                value="Europe",
            ),
            show_in_url=True,
        ),
    ],
)


page_11 = vm.Page(
    title="Test all selectors - [14 guards on refresh]",
    components=[
        vm.Graph(
            id="page_11_graph",
            figure=px.scatter("dynamic_df_gapminder_arg", x="gdpPercap", y="lifeExp", size="pop", color="continent"),
        ),
    ],
    controls=[
        vm.Filter(
            id="page_11_filter_dropdown",
            column="continent",
            selector=vm.Dropdown(id="page_11_filter_dropdown_selector"),
            show_in_url=True,
        ),
        vm.Filter(
            id="page_11_filter_radio_items",
            column="continent",
            selector=vm.RadioItems(id="page_11_filter_radio_items_selector"),
            show_in_url=True,
        ),
        vm.Filter(
            id="page_11_filter_checklist",
            column="continent",
            selector=vm.Checklist(id="page_11_filter_checklist_selector"),
            show_in_url=True,
        ),
        vm.Filter(
            id="page_11_filter_slider",
            column="number_column",
            selector=vm.Slider(id="page_11_filter_slider_selector"),
            show_in_url=True,
        ),
        vm.Filter(
            id="page_11_filter_range_slider",
            column="number_column",
            selector=vm.RangeSlider(id="page_11_filter_range_slider_selector"),
            show_in_url=True,
        ),
        vm.Filter(
            id="page_11_filter_date_picker",
            column="date_column",
            selector=vm.DatePicker(id="page_11_filter_date_picker_selector"),
            show_in_url=True,
        ),
        vm.Filter(
            id="page_11_filter_switch",
            column="is_europe",
            selector=vm.Switch(id="page_11_filter_switch_selector", title="Is Europe?"),
            show_in_url=True,
        ),
        vm.Parameter(
            id="page_11_dfp_parameter",
            targets=[
                "page_11_graph.data_frame.continent",
            ],
            selector=vm.RadioItems(
                id="page_11_dfp_parameter_selector",
                title="DFP - [6 guard]",
                options=list(set(df_gapminder["continent"])),
                value="Europe",
            ),
            show_in_url=True,
        ),
    ],
)

page_12 = vm.Page(
    title="Test bidirectional interactions - [4 guards on refresh]",
    layout=vm.Grid(grid=[[0, 2], [1, 3]]),
    components=[
        vm.AgGrid(
            id="page_12_grid_1",
            title="On click - [1 guard]",
            figure=dash_ag_grid(data_frame=df_gapminder),
            actions=[vm.Action(function=filter_interaction(targets=["page_12_grid_2"]))],
        ),
        vm.AgGrid(
            id="page_12_grid_2",
            title="On click - [1 guard]",
            figure=dash_ag_grid(data_frame=df_gapminder),
            actions=[vm.Action(function=filter_interaction(targets=["page_12_grid_1"]))],
        ),
        vm.Graph(
            id="page_12_graph_1",
            title="On click - [0 guards]",
            figure=px.scatter(
                df_gapminder, x="gdpPercap", y="lifeExp", size="pop", color="continent", custom_data=["continent"]
            ),
            actions=[vm.Action(function=filter_interaction(targets=["page_12_graph_2"]))],
        ),
        vm.Graph(
            id="page_12_graph_2",
            title="On click - [0 guards]",
            figure=px.scatter(
                df_gapminder, x="gdpPercap", y="lifeExp", size="pop", color="continent", custom_data=["continent"]
            ),
            actions=[vm.Action(function=filter_interaction(targets=["page_12_graph_1"]))],
        ),
    ],
)

# TODO-NOW: Reusing the action does not work as expected. It probably does not work due to duplicate dcc.Store IDs.
#  This doesn't

page_13_export_data_action = export_data()
page_13 = vm.Page(
    title="Test reusing the action",
    components=[
        vm.Graph(
            id="page_13_graph",
            figure=px.scatter(df_gapminder, x="gdpPercap", y="lifeExp", size="pop", color="continent"),
        ),
        vm.Button(
            id="page_13_button",
            text="Export data",
            actions=[
                page_13_export_data_action,
                page_13_export_data_action,
            ],
        ),
    ],
)


page_14 = vm.Page(
    title="Page without OPL",
    components=[
        vm.Button(
            id="page_14_button",
            actions=[
                vm.Action(
                    function=capture("action")(lambda x: x)("page_14_button.n_clicks"), outputs=["page_14_button.text"]
                )
            ],
        ),
    ],
)


vm.Page.add_type("components", vm.RadioItems)
radio_items_options = ["Option 1", "Option 2", "Option 3"]
page_15 = vm.Page(
    title="Action chain triggers another action chain",
    layout=vm.Grid(grid=[[0, 1, 2]]),
    components=[
        vm.Button(
            id="page_15_button",
            text="Change checklist value",
            actions=[
                vm.Action(
                    function=capture("action")(lambda x: radio_items_options[int(x) % 3])("page_15_button.n_clicks"),
                    outputs=["page_15_checklist.value"],
                )
            ],
        ),
        vm.RadioItems(
            id="page_15_checklist",
            options=radio_items_options,
            value=radio_items_options[0],
            actions=[
                vm.Action(
                    function=capture("action")(lambda x: x)("page_15_checklist.value"), outputs=["page_15_card.text"]
                )
            ],
        ),
        vm.Card(
            id="page_15_card",
            text="Card text",
        ),
    ],
)


@capture("action")
def my_custom_export():
    return dcc.send_data_frame(df_gapminder.to_csv, "mydf.csv")


@capture("action")
def my_custom_location(x=17):
    return f"/page-{x}"


page_16 = vm.Page(
    title="Test vizro_download and vizro_url using vizro actions",
    path="page-16",
    components=[
        vm.Container(
            components=[
                vm.Graph(
                    id="page_16_graph",
                    figure=px.scatter(df_gapminder, x="gdpPercap", y="lifeExp", size="pop", color="continent"),
                ),
                vm.Button(
                    id="page_16_button_download",
                    text="Export data!",
                    actions=[vm.Action(function=my_custom_export(), outputs=["vizro_download.data"])],
                ),
                vm.Button(
                    id="copy_page_16_button_download",
                    text="Copy Export data!",
                    actions=[vm.Action(function=my_custom_export(), outputs=["vizro_download.data"])],
                ),
                vm.Button(
                    id="page_16_button_location",
                    text="Go to page 17!",
                    actions=[vm.Action(function=my_custom_location(), outputs=["vizro_url.href"])],
                ),
                vm.Button(
                    id="copy_page_16_button_location",
                    text="Copy Go to page 17!",
                    actions=[vm.Action(function=my_custom_location(), outputs=["vizro_url.href"])],
                ),
            ],
        ),
    ],
)


# - Callbacks -
# --- Download ---
@callback(
    Output("vizro_download", "data", allow_duplicate=True),
    Input("page_17_button_download", "n_clicks"),
    prevent_initial_call=True,
)
def export_callback(_):
    return dcc.send_data_frame(iris.to_csv, "mydf.csv")


@callback(
    Output("vizro_download", "data", allow_duplicate=True),
    Input("copy_page_17_button_download", "n_clicks"),
    prevent_initial_call=True,
)
def export_callback(_):
    return dcc.send_data_frame(iris.to_csv, "mydf.csv")


# --- Location ---
@callback(
    Output("vizro_url", "href", allow_duplicate=True),
    Input("page_17_button_location", "n_clicks"),
    prevent_initial_call=True,
)
def change_location_callback(_):
    return "/page-16"


@callback(
    Output("vizro_url", "href", allow_duplicate=True),
    Input("copy_page_17_button_location", "n_clicks"),
    prevent_initial_call=True,
)
def change_location_callback(_):
    return "/page-16"


page_17 = vm.Page(
    title="Test vizro_download and vizro_url using dash callbacks",
    path="page-17",
    components=[
        vm.Container(
            components=[
                vm.Graph(
                    id="page_17_graph",
                    figure=px.scatter(df_gapminder, x="gdpPercap", y="lifeExp", size="pop", color="continent"),
                ),
                vm.Button(id="page_17_button_download", text="Export data!"),
                vm.Button(id="copy_page_17_button_download", text="Copy Export data!"),
                vm.Button(id="page_17_button_location", text="Go to page 16!"),
                vm.Button(id="copy_page_17_button_location", text="Copy Go to page 16!"),
            ],
        ),
    ],
)

dashboard = vm.Dashboard(
    pages=[
        page_1,
        page_2,
        page_3,
        page_4,
        page_5,
        page_6,
        page_7,
        page_8,
        page_9,
        page_10,
        page_11,
        page_12,
        page_13,
        page_14,
        page_15,
        page_16,
        page_17,
    ]
)

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
