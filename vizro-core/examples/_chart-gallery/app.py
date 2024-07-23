"""App configuration for chart gallery dashboard."""
import itertools

import vizro.models as vm
from chart_groups import ChartGroup, CHART_GROUPS, ALL_CHART_GROUP
from utils.custom_extensions import Markdown, FlexContainer

from vizro import Vizro


def make_chart_card(page: vm.Page, complete: bool):
    svg_name = page.title.lower().replace(" ", "-")
    return vm.Card(
        text=f"""
           ![](assets/images/pages/{svg_name}.svg#page-icon)

           #### {page.title}
           """,
        href=f"/{page.path}" if complete else "",
    )


def make_homepage_container(chart_group: ChartGroup):
    return vm.Container(
        title=chart_group.name,
        layout=vm.Layout(grid=[[0, 1, 1, 1]], col_gap="40px"),
        components=[
            Markdown(text=chart_group.intro_text, classname="intro-text"),
            FlexContainer(
                title="",
                components=[
                    make_chart_card(page, page in chart_group.pages)
                    for page in sorted(chart_group.pages | chart_group.incomplete_pages)
                ],
            ),
        ],
    )


def make_navlink(chart_group: ChartGroup):
    return vm.NavLink(
        label=chart_group.name,
        pages={chart_group.name: sorted(page.id for page in chart_group.pages)},
        icon=chart_group.icon,
    )


vm.Container.add_type("components", Markdown)
vm.Container.add_type("components", FlexContainer)


homepage = vm.Page(
    title="Overview",
    components=[
        vm.Tabs(tabs=[make_homepage_container(chart_group) for chart_group in [ALL_CHART_GROUP, *CHART_GROUPS]]),
    ],
)


# CHeck against: pages:
# homepage,
# bar,
# column,
# line,
# scatter,
# pie,
# donut,
# boxplot,
# violin,
# ordered_bar,
# ordered_column,
# time_column,
# treemap,
# magnitude_treemap,
# butterfly_page,
# distribution_butterfly,
# choropleth,
# sankey_page,
# for navigation:
# COMPLETED_CHARTS = [
#     "bar",
#     "ordered-bar",
#     "column",
#     "ordered-column",
#     "pie",
#     "donut",
#     "line",
#     "violin",
#     "scatter",
#     "sankey",
#     "butterfly",
#     "boxplot",
#     "choropleth",
#     "treemap",
# ]
#
#

# TODO: maybe nice to have an overall dashboard title? "Vizro chart gallery" or similar.
dashboard = vm.Dashboard(
    # note has duplicates
    pages=itertools.chain(*chart_group.pages for chart_group in CHART_GROUPS),
    navigation=vm.Navigation(
        nav_selector=vm.NavBar(
            items=[
                vm.NavLink(label="Overview", pages=[homepage.id], icon="Home"),
            ]
            + [make_navlink(chart_group) for chart_group in CHART_GROUPS]
        )
    ),
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
