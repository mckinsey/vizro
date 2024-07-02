"""Example to show dashboard configuration specified as pydantic models."""

import vizro.models as vm
from utils._home import *
from utils._magnitude import *
from vizro import Vizro

# HOME PAGE -----
homepage = vm.Page(
    title="Overview",
    components=[
        vm.Tabs(
            tabs=[
                home_all,
                home_deviation,
                home_correlation,
                home_ranking,
                home_distribution,
                home_magnitude,
                home_time,
                home_part,
                home_flow,
                home_spatial,
            ]
        ),
    ],
)


dashboard = vm.Dashboard(
    pages=[homepage, bar],
    navigation=vm.Navigation(
        nav_selector=vm.NavBar(
            items=[
                vm.NavLink(label="Overview", pages=["Overview"], icon="Home"),
                vm.NavLink(
                    label="Magnitude",
                    pages=["Bar Chart"],
                    icon="Bar Chart",
                ),
            ]
        )
    ),
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
