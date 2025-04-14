"""App configuration for dashboard."""

from typing import Union

import dash_bootstrap_components as dbc
import vizro.models as vm
from chart_groups import ALL_CHART_GROUP, CHART_GROUPS, ChartGroup, IncompletePage
from custom_components import Markdown
from dash import get_asset_url, html
from vizro import Vizro


def make_chart_card(page: Union[vm.Page, IncompletePage]) -> vm.Card:
    """Makes a card with svg icon, linked to the right page if page is complete.

    Args:
        page: page to make card for

    Returns: card with svg icon, linked to the right page if page is complete.

    """
    # There's one SVG per chart title, so that e.g. pages distribution-butterfly and deviation-butterfly, which both
    # have title "Butterfly", correspond to butterfly.svg.
    # Incomplete pages have page.path = "" so won't be linked to here.
    svg_name = page.title.lower().replace(" ", "-")
    return vm.Card(
        text=f"""
           ![](assets/images/charts/{svg_name}.svg#chart-icon)

           #### {page.title}
           """,
        href=page.path,
    )


def make_homepage_container(chart_group: ChartGroup) -> vm.Container:
    """Makes a container with cards for each completed and incomplete chart in chart_group.

    Args:
        chart_group: group of charts to make container for.

    Returns: container with cards for each chart in chart_group.

    """
    # Pages are sorted in title's alphabetical order and deduplicated so that e.g. pages distribution-butterfly and
    # deviation-butterfly, which both have title "Butterfly", correspond to a single card.
    return vm.Container(
        title=chart_group.name,
        layout=vm.Grid(grid=[[0, 1, 1]], col_gap="40px"),
        components=[
            Markdown(text=chart_group.intro_text, classname="intro-text"),
            vm.Container(
                layout=vm.Flex(direction="row", wrap=True),
                components=[
                    make_chart_card(page)
                    for page in sorted(
                        _remove_duplicates(chart_group.pages + chart_group.incomplete_pages),
                        key=lambda page: page.title,
                    )
                ],
            ),
        ],
    )


def _remove_duplicates(pages: list[Union[vm.Page, IncompletePage]]) -> list[Union[vm.Page, IncompletePage]]:
    # Deduplicate pages that have the same title. Using reversed means that the page that is kept is the first one
    # in the dashboard. This will be the one that the card on the homepage links to.
    return list({page.title: page for page in reversed(pages)}.values())


def make_navlink(chart_group: ChartGroup) -> vm.NavLink:
    """Makes a navlink with icon and links to every complete page within chart_group.

    Args:
        chart_group: chart_group to make a navlink for.

    Returns: navlink for chart_group.

    """
    # Pages are sorted in alphabetical order within each chart group.
    return vm.NavLink(
        label=chart_group.name,
        pages={chart_group.name: [page.id for page in sorted(chart_group.pages, key=lambda page: page.title)]},
        icon=chart_group.icon,
    )


homepage = vm.Page(
    title="Overview",
    components=[
        vm.Tabs(tabs=[make_homepage_container(chart_group) for chart_group in [ALL_CHART_GROUP, *CHART_GROUPS]]),
    ],
)

# TODO: consider whether each chart group should have its own individual homepage,
# e.g. at http://localhost:8050/deviation/. This could just repeat the content of the tab from the homepage and would
# work nicely with the hierarchical navigation.
dashboard = vm.Dashboard(
    # ALL_CHART_GROUP.pages has duplicated pages, e.g. both distribution-butterfly and deviation-butterfly.
    title="Visual vocabulary",
    pages=[homepage, *ALL_CHART_GROUP.pages],
    navigation=vm.Navigation(
        nav_selector=vm.NavBar(
            items=[
                vm.NavLink(label="Overview", pages=[homepage.id], icon="Home"),
            ]
            + [make_navlink(chart_group) for chart_group in CHART_GROUPS]
        )
    ),
)

app = Vizro().build(dashboard)
app.dash.layout.children.append(
    dbc.NavLink(
        ["Made with ", html.Img(src=get_asset_url("logo.svg"), id="banner", alt="Vizro logo"), "vizro"],
        href="https://github.com/mckinsey/vizro",
        target="_blank",
        class_name="anchor-container",
    )
)

if __name__ == "__main__":
    app.run(port=8051)
