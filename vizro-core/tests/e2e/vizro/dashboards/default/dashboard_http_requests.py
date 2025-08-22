import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_ag_grid
from vizro.actions import filter_interaction, export_data
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
    title="Page without OPL",
    components=[
        vm.Button(
            id="page_14_button",
            actions=[
                vm.Action(
                    function=capture("action")(lambda x: x)("page_14_button.n_clicks"), outputs="page_14_button.text"
                )
            ],
        ),
    ],
)


page_2 = vm.Page(
    title="My first dashboard - [0 guards]",
    components=[
        vm.Graph(id="page_1_graph", figure=px.histogram(df_gapminder, x="lifeExp", color="continent", barmode="group")),
    ],
    controls=[
        vm.Filter(id="page_1_filter", column="continent", selector=vm.Dropdown(id="page_1_filter_selector")),
    ],
)

page_2_2 = vm.Page(
    title="Export data -> custom sleep action -> export data - [0 guard]",
    components=[
        vm.Graph(
            id="page_2_2_graph",
            figure=px.scatter(df_gapminder, x="gdpPercap", y="lifeExp", size="pop", color="continent"),
        ),
        vm.Button(
            id="page_2_2_button",
            text="Export data",
            actions=[
                export_data(id="a1"),
                vm.Action(id="a2", function=my_custom_action(t=2)),
                export_data(file_format="xlsx", id="a3"),
            ],
        ),
    ],
    controls=[
        vm.Filter(id="page_2_2_filter", column="continent", selector=vm.RadioItems(id="page_2_2_filter_selector")),
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
    title="DFP + Dynamic filter + URL + filter interaction - [4 guards on refresh]",
    components=[
        vm.AgGrid(
            id="page_5_grid",
            figure=dash_ag_grid(data_frame="dynamic_df_gapminder_arg"),
            actions=[
                vm.Action(function=filter_interaction(id="page_5_filter_interaction", targets=["page_5_graph"]))
            ],
        ),
        vm.Graph(
            id="page_5_graph",
            figure=px.scatter("dynamic_df_gapminder_arg", x="gdpPercap", y="lifeExp", size="pop", color="continent"),
        ),
    ],
    controls=[
        vm.Filter(
            id="page_5_filter",
            column="continent",
            selector=vm.Dropdown(title="Filter AgGrid - [1 guard]", id="page_10_filter_selector"),
            show_in_url=True,
        ),
        vm.Parameter(
            id="page_5_dfp_parameter",
            targets=[
                "page_5_grid.data_frame.continent",
                "page_5_graph.data_frame.continent",
            ],
            selector=vm.RadioItems(
                id="page_5_dfp_parameter_selector",
                title="DFP - [2 guards]",
                options=list(set(df_gapminder["continent"])),
                value="Europe",
            ),
            show_in_url=True,
        ),
    ],
)

page_6 = vm.Page(
    title="Test all selectors - [14 guards on refresh]",
    components=[
        vm.Graph(
            id="page_6_graph",
            figure=px.scatter("dynamic_df_gapminder_arg", x="gdpPercap", y="lifeExp", size="pop", color="continent"),
        ),
    ],
    controls=[
        vm.Filter(
            id="page_6_filter_dropdown",
            column="continent",
            selector=vm.Dropdown(id="page_11_filter_dropdown_selector"),
            show_in_url=True,
        ),
        vm.Filter(
            id="page_6_filter_radio_items",
            column="continent",
            selector=vm.RadioItems(id="page_11_filter_radio_items_selector"),
            show_in_url=True,
        ),
        vm.Filter(
            id="page_6_filter_checklist",
            column="continent",
            selector=vm.Checklist(id="page_11_filter_checklist_selector"),
            show_in_url=True,
        ),
        vm.Filter(
            id="page_6_filter_slider",
            column="number_column",
            selector=vm.Slider(id="page_11_filter_slider_selector"),
            show_in_url=True,
        ),
        vm.Filter(
            id="page_6_filter_range_slider",
            column="number_column",
            selector=vm.RangeSlider(id="page_11_filter_range_slider_selector"),
            show_in_url=True,
        ),
        vm.Filter(
            id="page_6_filter_date_picker",
            column="date_column",
            selector=vm.DatePicker(id="page_6_filter_date_picker_selector"),
            show_in_url=True,
        ),
        vm.Filter(
            id="page_6_filter_switch",
            column="is_europe",
            selector=vm.Switch(id="page_6_filter_switch_selector", title="Is Europe?"),
            show_in_url=True,
        ),
        vm.Parameter(
            id="page_6_dfp_parameter",
            targets=[
                "page_6_graph.data_frame.continent",
            ],
            selector=vm.RadioItems(
                id="page_6_dfp_parameter_selector",
                title="DFP - [6 guard]",
                options=list(set(df_gapminder["continent"])),
                value="Europe",
            ),
            show_in_url=True,
        ),
    ],
)


vm.Page.add_type("components", vm.RadioItems)
radio_items_options = ["Option 1", "Option 2", "Option 3"]
page_7 = vm.Page(
    title="Action chain triggers another action chain",
    layout=vm.Grid(grid=[[0, 1, 2]]),
    components=[
        vm.Button(
            id="page_7_button",
            text="Change checklist value",
            actions=[
                vm.Action(
                    function=capture("action")(lambda x: radio_items_options[int(x) % 3])("page_7_button.n_clicks"),
                    outputs="page_7_checklist.value",
                )
            ],
        ),
        vm.RadioItems(
            id="page_7_checklist",
            options=radio_items_options,
            value=radio_items_options[0],
            actions=[
                vm.Action(
                    function=capture("action")(lambda x: x)("page_7_checklist.value"), outputs="page_7_card.text"
                )
            ],
        ),
        vm.Card(
            id="page_7_card",
            text="Card text",
        ),
    ],
)


dashboard = vm.Dashboard(
    pages=[
        page_1,
        page_2,
        page_2_2,
        page_3,
        page_4,
        page_5,
        page_6,
        page_7,
    ]
)

app = Vizro().build(dashboard)

if __name__ == "__main__":
    app.run(debug=True)
