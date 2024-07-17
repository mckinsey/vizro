"""App configuration for chart gallery dashboard."""

import vizro.models as vm
from utils.chart_pages import (
    bar,
    boxplot,
    butterfly_page,
    choropleth,
    column,
    distribution_butterfly,
    donut,
    line,
    magnitude_treemap,
    ordered_bar,
    ordered_column,
    pie,
    sankey_page,
    scatter,
    time_column,
    treemap,
    violin,
)
from utils.tab_containers import (
    container_all,
    container_correlation,
    container_deviation,
    container_distribution,
    container_flow,
    container_magnitude,
    container_part,
    container_ranking,
    container_spatial,
    container_time,
)
from vizro import Vizro

homepage = vm.Page(
    title="Overview",
    components=[
        vm.Tabs(
            tabs=[
                container_all,
                container_deviation,
                container_correlation,
                container_ranking,
                container_distribution,
                container_magnitude,
                container_time,
                container_part,
                container_flow,
                container_spatial,
            ]
        ),
    ],
)


dashboard = vm.Dashboard(
    pages=[
        homepage,
        bar,
        column,
        line,
        scatter,
        pie,
        donut,
        boxplot,
        violin,
        ordered_bar,
        ordered_column,
        time_column,
        treemap,
        magnitude_treemap,
        butterfly_page,
        distribution_butterfly,
        choropleth,
        sankey_page,
    ],
    navigation=vm.Navigation(
        nav_selector=vm.NavBar(
            items=[
                vm.NavLink(label="Overview", pages=["Overview"], icon="Home"),
                vm.NavLink(
                    label="Deviation",
                    pages={"Deviation": ["Butterfly"]},
                    icon="Planner Review",
                ),
                vm.NavLink(
                    label="Correlation",
                    pages={"Correlation": ["Scatter"]},
                    icon="Bubble Chart",
                ),
                vm.NavLink(
                    label="Ranking",
                    pages={"Ranking": ["Ordered Bar", "Ordered Column"]},
                    icon="Stacked Bar Chart",
                ),
                vm.NavLink(
                    label="Distribution",
                    pages={"Distribution": ["Boxplot", "Violin", "Distribution-Butterfly"]},
                    icon="Waterfall Chart",
                ),
                vm.NavLink(
                    label="Magnitude",
                    pages={"Magnitude": ["Bar", "Column", "Magnitude-Treemap"]},
                    icon="Bar Chart",
                ),
                vm.NavLink(
                    label="Time",
                    pages={"Time": ["Line", "Time-Column"]},
                    icon="Timeline",
                ),
                vm.NavLink(
                    label="Part-to-whole",
                    pages={"Part-to-whole": ["Donut", "Pie", "Treemap"]},
                    icon="Donut Small",
                ),
                vm.NavLink(
                    label="Flow",
                    pages={"Flow": ["Sankey"]},
                    icon="Stacked Line Chart",
                ),
                vm.NavLink(
                    label="Spatial",
                    pages={"Spatial": ["Choropleth"]},
                    icon="Map",
                ),
            ]
        )
    ),
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
