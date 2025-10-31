from time import sleep

import e2e.vizro.constants as cnst
import pandas as pd
from pages.ag_grid_interactions_page import ag_grid_interactions_page
from pages.filters_inside_containters_page import filters_inside_containers_page
from pages.set_control_cross_filter_page import (
    cross_filter_ag_grid_page,
    cross_filter_graph_page,
)
from pages.set_control_drill_down import drill_down_graph_page
from pages.set_control_drill_through import (
    drill_through_filter_ag_grid_source_page,
    drill_through_filter_ag_grid_target_page,
    drill_through_filter_graph_source_page,
    drill_through_filter_graph_target_page,
    drill_through_parameter_graph_source_page,
    drill_through_parameter_graph_target_page,
)

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import export_data, filter_interaction
from vizro.managers import data_manager
from vizro.models.types import capture
from vizro.tables import dash_ag_grid

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


page_without_chart = vm.Page(
    title=cnst.PAGE_WITHOUT_CHART,
    components=[
        vm.Button(
            id=f"{cnst.PAGE_WITHOUT_CHART}_button",
            actions=[
                vm.Action(
                    function=capture("action")(lambda x: x)(f"{cnst.PAGE_WITHOUT_CHART}_button"),
                    outputs=f"{cnst.PAGE_WITHOUT_CHART}_button.text",
                )
            ],
        ),
    ],
)

page_with_one_chart = vm.Page(
    title=cnst.PAGE_WITH_ONE_CHART,
    components=[
        vm.Graph(figure=px.histogram(df_gapminder, x="lifeExp", color="continent", barmode="group")),
    ],
    controls=[
        vm.Filter(column="continent", selector=vm.Dropdown()),
    ],
)

page_explicit_actions_chain = vm.Page(
    title=cnst.PAGE_EXPLICIT_ACIONS_CHAIN,
    components=[
        vm.Graph(
            figure=px.scatter(df_gapminder, x="gdpPercap", y="lifeExp", size="pop", color="continent"),
        ),
        vm.Button(
            text="Export data",
            id=f"{cnst.PAGE_EXPLICIT_ACIONS_CHAIN}_button",
            actions=[
                export_data(),
                vm.Action(function=my_custom_action(t=2)),
                export_data(file_format="xlsx"),
            ],
        ),
    ],
    controls=[
        vm.Filter(column="continent", selector=vm.RadioItems()),
    ],
)

vm.Page.add_type("components", vm.RadioItems)
radio_items_options = ["Option 1", "Option 2", "Option 3"]

page_implicit_actions_chain = vm.Page(
    title=cnst.PAGE_IMPLICIT_ACIONS_CHAIN,
    layout=vm.Grid(grid=[[0, 1, 2]]),
    components=[
        vm.Button(
            id=f"{cnst.PAGE_IMPLICIT_ACIONS_CHAIN}_button",
            text="Change checklist value",
            actions=[
                vm.Action(
                    function=capture("action")(lambda x: radio_items_options[int(x) % 3])(
                        f"{cnst.PAGE_IMPLICIT_ACIONS_CHAIN}_button"
                    ),
                    outputs=f"{cnst.PAGE_IMPLICIT_ACIONS_CHAIN}_checklist",
                )
            ],
        ),
        vm.RadioItems(
            id=f"{cnst.PAGE_IMPLICIT_ACIONS_CHAIN}_checklist",
            options=radio_items_options,
            value=radio_items_options[0],
            actions=[
                vm.Action(
                    function=capture("action")(lambda x: x)(f"{cnst.PAGE_IMPLICIT_ACIONS_CHAIN}_checklist"),
                    outputs=f"{cnst.PAGE_IMPLICIT_ACIONS_CHAIN}_card.text",
                )
            ],
        ),
        vm.Card(
            id=f"{cnst.PAGE_IMPLICIT_ACIONS_CHAIN}_card",
            text="Card text",
        ),
    ],
)

page_chart_with_filter_interaction = vm.Page(
    title=cnst.PAGE_CHART_WITH_FILTER_INTERACTION,
    components=[
        vm.Graph(
            figure=px.box(
                df_gapminder,
                x="continent",
                y="lifeExp",
                color="continent",
                custom_data=["continent"],
            ),
            actions=filter_interaction(targets=[f"{cnst.PAGE_CHART_WITH_FILTER_INTERACTION}_graph_2"]),
        ),
        vm.Graph(
            id=f"{cnst.PAGE_CHART_WITH_FILTER_INTERACTION}_graph_2",
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
        vm.Filter(column="continent", selector=vm.Dropdown()),
    ],
)

page_ag_grid_with_filter_interaction = vm.Page(
    title=cnst.PAGE_AG_GRID_WITH_FILTER_INTERACTION,
    components=[
        vm.AgGrid(
            id=f"{cnst.PAGE_AG_GRID_WITH_FILTER_INTERACTION}_grid",
            figure=dash_ag_grid(data_frame=df_gapminder),
            actions=filter_interaction(targets=[f"{cnst.PAGE_AG_GRID_WITH_FILTER_INTERACTION}_graph"]),
        ),
        vm.Graph(
            id=f"{cnst.PAGE_AG_GRID_WITH_FILTER_INTERACTION}_graph",
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
            column="continent",
            targets=[f"{cnst.PAGE_AG_GRID_WITH_FILTER_INTERACTION}_grid"],
            selector=vm.Dropdown(),
        ),
    ],
)

page_dynamic_parametrisation = vm.Page(
    title=cnst.PAGE_DYNAMIC_PARAMETRISATION,
    components=[
        vm.AgGrid(
            id=f"{cnst.PAGE_DYNAMIC_PARAMETRISATION}_grid",
            figure=dash_ag_grid(data_frame="dynamic_df_gapminder_arg"),
            actions=[filter_interaction(targets=[f"{cnst.PAGE_DYNAMIC_PARAMETRISATION}_graph"])],
        ),
        vm.Graph(
            id=f"{cnst.PAGE_DYNAMIC_PARAMETRISATION}_graph",
            figure=px.scatter("dynamic_df_gapminder_arg", x="gdpPercap", y="lifeExp", size="pop", color="continent"),
        ),
    ],
    controls=[
        vm.Filter(
            column="continent",
            selector=vm.Dropdown(),
        ),
        vm.Parameter(
            targets=[
                f"{cnst.PAGE_DYNAMIC_PARAMETRISATION}_grid.data_frame.continent",
                f"{cnst.PAGE_DYNAMIC_PARAMETRISATION}_graph.data_frame.continent",
            ],
            selector=vm.RadioItems(
                options=list(set(df_gapminder["continent"])),
                value="Europe",
            ),
        ),
    ],
)

page_all_selectors = vm.Page(
    title=cnst.PAGE_ALL_SELECTORS,
    components=[
        vm.Graph(
            id=f"{cnst.PAGE_ALL_SELECTORS}_graph",
            figure=px.scatter("dynamic_df_gapminder_arg", x="gdpPercap", y="lifeExp", size="pop", color="continent"),
        ),
    ],
    controls=[
        vm.Parameter(
            targets=[
                f"{cnst.PAGE_ALL_SELECTORS}_graph.data_frame.continent",
            ],
            selector=vm.RadioItems(
                options=list(set(df_gapminder["continent"])),
                value="Europe",
            ),
        ),
        vm.Filter(column="continent", selector=vm.Dropdown()),
        vm.Filter(column="continent", selector=vm.RadioItems()),
        vm.Filter(column="continent", selector=vm.Checklist()),
        vm.Filter(column="number_column", selector=vm.Slider()),
        vm.Filter(column="number_column", selector=vm.RangeSlider()),
        vm.Filter(column="date_column", selector=vm.DatePicker()),
        vm.Filter(column="is_europe", selector=vm.Switch(title="Is Europe?")),
    ],
)


page_all_selectors_in_url = vm.Page(
    title=cnst.PAGE_ALL_SELECTORS_IN_URL,
    components=[
        vm.Graph(
            id=f"{cnst.PAGE_ALL_SELECTORS_IN_URL}_graph",
            figure=px.scatter("dynamic_df_gapminder_arg", x="gdpPercap", y="lifeExp", size="pop", color="continent"),
        ),
    ],
    controls=[
        vm.Parameter(
            targets=[
                f"{cnst.PAGE_ALL_SELECTORS_IN_URL}_graph.data_frame.continent",
            ],
            selector=vm.RadioItems(
                options=list(set(df_gapminder["continent"])),
                value="Europe",
            ),
            show_in_url=True,
        ),
        vm.Filter(column="continent", selector=vm.Dropdown(), show_in_url=True),
        vm.Filter(column="continent", selector=vm.RadioItems(), show_in_url=True),
        vm.Filter(column="continent", selector=vm.Checklist(), show_in_url=True),
        vm.Filter(column="number_column", selector=vm.Slider(), show_in_url=True),
        vm.Filter(column="number_column", selector=vm.RangeSlider(), show_in_url=True),
        vm.Filter(column="date_column", selector=vm.DatePicker(), show_in_url=True),
        vm.Filter(column="is_europe", selector=vm.Switch(title="Is Europe?"), show_in_url=True),
    ],
)


dashboard = vm.Dashboard(
    pages=[
        page_without_chart,
        page_with_one_chart,
        page_explicit_actions_chain,
        page_implicit_actions_chain,
        page_chart_with_filter_interaction,
        page_ag_grid_with_filter_interaction,
        page_dynamic_parametrisation,
        page_all_selectors,
        page_all_selectors_in_url,
        cross_filter_graph_page,
        cross_filter_ag_grid_page,
        drill_through_filter_ag_grid_source_page,
        drill_through_filter_ag_grid_target_page,
        drill_through_filter_graph_source_page,
        drill_through_filter_graph_target_page,
        drill_through_parameter_graph_source_page,
        drill_through_parameter_graph_target_page,
        drill_down_graph_page,
        ag_grid_interactions_page,
        filters_inside_containers_page,
    ]
)

app = Vizro().build(dashboard)

if __name__ == "__main__":
    app.run(debug=True)
