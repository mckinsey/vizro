"""Example to show dashboard configuration specified as pydantic models."""

import vizro.models as vm
from utils._containers import (
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
from utils._pages import (
    bar,
    boxplot,
    column,
    donut,
    line,
    ordered_bar,
    ordered_column,
    pie,
    scatter,
    time_column,
    time_line,
    violin,
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
        time_line,
        time_column,
    ],
    navigation=vm.Navigation(
        nav_selector=vm.NavBar(
            items=[
                vm.NavLink(label="Overview", pages=["Overview"], icon="Home"),
                vm.NavLink(
                    label="Deviation",
                    pages={"Deviation": ["Line", "Scatter"]},  # Replace with diverging bar
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
                    pages={"Distribution": ["Boxplot", "Violin"]},
                    icon="Waterfall Chart",
                ),
                vm.NavLink(
                    label="Magnitude",
                    pages={"Magnitude": ["Bar", "Column"]},
                    icon="Bar Chart",
                ),
                vm.NavLink(
                    label="Time",
                    pages={"Time": ["Time-Line", "Time-Column"]},
                    icon="Timeline",
                ),
                vm.NavLink(
                    label="Part-to-whole",
                    pages={"Part-to-whole": ["Donut", "Pie"]},
                    icon="Donut Small",
                ),
                vm.NavLink(
                    label="Flow",
                    pages={"Flow": ["Line"]},  # TODO: Replace with Sankey
                    icon="Stacked Line Chart",
                ),
                vm.NavLink(
                    label="Spatial",
                    pages={"Spatial": ["Line"]},  # TODO: Replace with map
                    icon="Map",
                ),
            ]
        )
    ),
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
