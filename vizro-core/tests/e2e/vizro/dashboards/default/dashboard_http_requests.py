from time import sleep

import e2e.vizro.constants as cnst
import pandas as pd
from pages.ag_grid_interactions_page import ag_grid_interactions_page
from pages.cascader_pages import cascader_leaf_page, cascader_path_page
from pages.conditional_notifications import conditional_notifications_page
from pages.datetimepicker_pages import datetimepicker_range
from pages.filters_inside_containters_page import filters_inside_containers_page
from pages.page_actions_none_page import page_actions_none
from pages.set_controls_cross_filter_page import (
    cross_filter_ag_grid_page,
    cross_filter_graph_page,
)
from pages.set_controls_drill_down import drill_down_graph_page
from pages.set_controls_drill_through import (
    drill_through_filter_ag_grid_source_page,
    drill_through_filter_ag_grid_target_page,
    drill_through_filter_graph_source_page,
    drill_through_filter_graph_target_page,
    drill_through_parameter_graph_source_page,
    drill_through_parameter_graph_target_page,
)
from pages.set_controls_multi_select_pages import (
    filtered_graph_aggrid_trigger_set_controls,
    self_filter_set_controls_page,
)
from pages.sync_controls_pages import (
    sync_cross_page_source_page,
    sync_cross_page_target_page,
    sync_drill_through_source_page,
    sync_drill_through_target_page,
    sync_hidden_parameter_page,
    sync_multiple_controls_same_page,
)
from pages.timepicker_pages import timepicker_range
from pages.update_targets_page import apply_controls_on_button_click_page

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.actions import export_data
from vizro.managers import data_manager
from vizro.models.types import capture
from vizro.tables import dash_ag_grid

df_gapminder = px.data.gapminder().query("year == 2007")
df_gapminder["date_column"] = pd.date_range(start=pd.to_datetime("2025-01-01"), periods=len(df_gapminder), freq="D")
df_gapminder["datetime_utc"] = pd.to_datetime(df_gapminder["date_column"]) + pd.to_timedelta(
    df_gapminder.index % 24, unit="h"
)
df_gapminder["time_hh_mm_ss"] = df_gapminder["datetime_utc"].dt.time
df_gapminder["number_column"] = range(len(df_gapminder))
df_gapminder["is_europe"] = df_gapminder["continent"] == "Europe"
_gapminder_regions = {
    "North": {
        "Canada",
        "United States",
        "Denmark",
        "Finland",
        "Norway",
        "Sweden",
        "Iceland",
        "Ireland",
        "United Kingdom",
    },
    "South": {
        "Argentina",
        "Brazil",
        "Australia",
        "New Zealand",
        "India",
        "China",
        "Japan",
    },
    "West": {
        "Mexico",
        "Germany",
        "France",
        "Spain",
        "Italy",
        "Nigeria",
        "Egypt",
    },
    "East": {
        "Poland",
        "Ethiopia",
        "Kenya",
        "Korea, Rep.",
        "Thailand",
        "Indonesia",
    },
}
df_gapminder["region"] = df_gapminder["country"].map(
    {country: region for region, countries in _gapminder_regions.items() for country in countries}
)


def load_dynamic_gapminder_data(continent: str = "Europe"):
    return df_gapminder[df_gapminder["continent"] == continent]


data_manager["dynamic_df_gapminder_arg"] = load_dynamic_gapminder_data
data_manager["dynamic_df_gapminder"] = lambda: df_gapminder


@capture("action")
def my_custom_action():
    """Custom action."""
    sleep(2)


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
                vm.Action(function=my_custom_action()),
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

page_dynamic_parametrisation = vm.Page(
    title=cnst.PAGE_DYNAMIC_PARAMETRISATION,
    components=[
        vm.Table(
            id=f"{cnst.PAGE_DYNAMIC_PARAMETRISATION}_grid",
            figure=dash_ag_grid(data_frame="dynamic_df_gapminder_arg"),
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
            id=cnst.PAGE_ALL_SELECTORS_GRAPH_ID,
            figure=px.scatter("dynamic_df_gapminder_arg", x="gdpPercap", y="lifeExp", size="pop", color="continent"),
        ),
    ],
    controls=[
        vm.Parameter(
            targets=[
                f"{cnst.PAGE_ALL_SELECTORS_GRAPH_ID}.data_frame.continent",
            ],
            selector=vm.RadioItems(
                options=list(set(df_gapminder["continent"])),
                value="Europe",
            ),
        ),
        vm.Filter(column="continent", selector=vm.Dropdown()),
        vm.Filter(column="continent", selector=vm.RadioItems()),
        vm.Filter(column="continent", selector=vm.Checklist()),
        vm.Filter(
            column="number_column",
            selector=vm.Slider(id=cnst.PAGE_ALL_SELECTORS_FILTER_SLIDER_ID),
        ),
        vm.Filter(
            column="number_column",
            selector=vm.Slider(range=True, id=cnst.PAGE_ALL_SELECTORS_FILTER_RANGE_SLIDER_ID),
        ),
        vm.Filter(
            column="date_column",
            selector=vm.DatePicker(id=cnst.PAGE_ALL_SELECTORS_FILTER_DATEPICKER_ID),
        ),
        vm.Filter(
            column="time_hh_mm_ss",
            selector=vm.TimePicker(id=cnst.PAGE_ALL_SELECTORS_FILTER_TIMEPICKER_ID, title="Time"),
        ),
        vm.Filter(
            column="datetime_utc",
            selector=vm.DateTimePicker(id=cnst.PAGE_ALL_SELECTORS_FILTER_DATETIMEPICKER_ID, title="Datetime"),
        ),
        vm.Filter(
            column=["continent", "region", "country"],
            selector=vm.Cascader(id=cnst.PAGE_ALL_SELECTORS_FILTER_CASCADER_ID, title="Country"),
        ),
        vm.Filter(
            id=cnst.PAGE_ALL_SELECTORS_FILTER_SWITCH_CONTROL_ID,
            column="is_europe",
            selector=vm.Switch(title="Is Europe?"),
        ),
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
        vm.Filter(column="number_column", selector=vm.Slider(range=True), show_in_url=True),
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
        filtered_graph_aggrid_trigger_set_controls,
        self_filter_set_controls_page,
        conditional_notifications_page,
        timepicker_range,
        datetimepicker_range,
        cascader_leaf_page,
        cascader_path_page,
        apply_controls_on_button_click_page,
        page_actions_none,
        sync_hidden_parameter_page,
        sync_multiple_controls_same_page,
        sync_cross_page_source_page,
        sync_cross_page_target_page,
        sync_drill_through_source_page,
        sync_drill_through_target_page,
    ]
)

app = Vizro().build(dashboard)

if __name__ == "__main__":
    app.run(debug=True)
