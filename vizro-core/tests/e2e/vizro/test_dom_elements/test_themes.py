import e2e.vizro.constants as cnst
import pytest
from e2e.vizro.checkers import (
    check_ag_grid_theme_color,
    check_graph_color,
    check_theme_color,
)
from e2e.vizro.navigation import accordion_select, page_select
from e2e.vizro.paths import tab_path, theme_toggle_path


@pytest.mark.parametrize(
    "dash_br_driver, dashboard_id",
    [
        ({"port": cnst.DEFAULT_PORT}, cnst.DASHBOARD_DEFAULT),
        ({"port": cnst.YAML_PORT}, cnst.DASHBOARD_YAML),
    ],
    ids=[cnst.DASHBOARD_DEFAULT, cnst.DASHBOARD_YAML],
    indirect=["dash_br_driver"],
)
def test_themes(dash_br_driver, dashboard_id):
    """Test switching the themes and checking the graph and theme color."""
    page_select(dash_br_driver, page_path=cnst.FILTERS_PAGE_PATH, page_name=cnst.FILTERS_PAGE)

    if dashboard_id == cnst.DASHBOARD_DEFAULT:
        # dashboard loaded with light theme
        check_graph_color(dash_br_driver, style_background=cnst.STYLE_TRANSPARENT, color=cnst.RGBA_TRANSPARENT)
        check_theme_color(dash_br_driver, color=cnst.THEME_LIGHT)

        # switch theme to dark
        dash_br_driver.multiple_click(theme_toggle_path(), 1)
        check_graph_color(dash_br_driver, style_background=cnst.STYLE_TRANSPARENT, color=cnst.RGBA_TRANSPARENT)
        check_theme_color(dash_br_driver, color=cnst.THEME_DARK)

        # switch theme back to light
        dash_br_driver.multiple_click(theme_toggle_path(), 1)
        check_graph_color(dash_br_driver, style_background=cnst.STYLE_TRANSPARENT, color=cnst.RGBA_TRANSPARENT)
        check_theme_color(dash_br_driver, color=cnst.THEME_LIGHT)
    else:
        # dashboard loaded with dark theme
        check_graph_color(dash_br_driver, style_background=cnst.STYLE_TRANSPARENT, color=cnst.RGBA_TRANSPARENT)
        check_theme_color(dash_br_driver, color=cnst.THEME_DARK)

        # switch theme to light
        dash_br_driver.multiple_click(theme_toggle_path(), 1)
        check_graph_color(dash_br_driver, style_background=cnst.STYLE_TRANSPARENT, color=cnst.RGBA_TRANSPARENT)
        check_theme_color(dash_br_driver, color=cnst.THEME_LIGHT)

        # switch theme back to dark
        dash_br_driver.multiple_click(theme_toggle_path(), 1)
        check_graph_color(dash_br_driver, style_background=cnst.STYLE_TRANSPARENT, color=cnst.RGBA_TRANSPARENT)
        check_theme_color(dash_br_driver, color=cnst.THEME_DARK)


@pytest.mark.parametrize(
    "dash_br_driver, dashboard_id",
    [
        ({"port": cnst.DEFAULT_PORT}, cnst.DASHBOARD_DEFAULT),
        ({"port": cnst.YAML_PORT}, cnst.DASHBOARD_YAML),
    ],
    ids=[cnst.DASHBOARD_DEFAULT, cnst.DASHBOARD_YAML],
    indirect=["dash_br_driver"],
)
def test_ag_grid_themes(dash_br_driver, dashboard_id):
    """Test switching themes for ag_grid."""
    accordion_select(dash_br_driver, accordion_name=cnst.AG_GRID_ACCORDION)
    page_select(
        dash_br_driver,
        page_name=cnst.TABLE_AG_GRID_PAGE,
    )
    if dashboard_id == cnst.DASHBOARD_DEFAULT:
        # dashboard loaded with light theme
        check_ag_grid_theme_color(dash_br_driver, ag_grid_id=cnst.TABLE_AG_GRID_ID, color=cnst.AG_GRID_LIGHT)

        # switch theme to dark
        dash_br_driver.multiple_click(theme_toggle_path(), 1)
        check_ag_grid_theme_color(dash_br_driver, ag_grid_id=cnst.TABLE_AG_GRID_ID, color=cnst.AG_GRID_DARK)
    else:
        # dashboard loaded with dark theme
        check_ag_grid_theme_color(dash_br_driver, ag_grid_id=cnst.TABLE_AG_GRID_ID, color=cnst.AG_GRID_DARK)

        # switch theme to light
        dash_br_driver.multiple_click(theme_toggle_path(), 1)
        check_ag_grid_theme_color(dash_br_driver, ag_grid_id=cnst.TABLE_AG_GRID_ID, color=cnst.AG_GRID_LIGHT)


@pytest.mark.parametrize(
    "dash_br_driver, dashboard_id",
    [
        ({"port": cnst.DEFAULT_PORT}, cnst.DASHBOARD_DEFAULT),
        ({"port": cnst.YAML_PORT}, cnst.DASHBOARD_YAML),
    ],
    ids=[cnst.DASHBOARD_DEFAULT, cnst.DASHBOARD_YAML],
    indirect=["dash_br_driver"],
)
def test_themes_page_change(dash_br_driver, dashboard_id):
    """Test switching themes after reloading the page with two tabs."""
    page_select(
        dash_br_driver,
        page_path=cnst.PARAMETERS_PAGE_PATH,
        page_name=cnst.PARAMETERS_PAGE,
    )

    def _logic(style_background, graph_color, theme_color):
        check_graph_color(dash_br_driver, style_background=style_background, color=graph_color)
        check_theme_color(dash_br_driver, color=theme_color)

        # switch to the second tab
        dash_br_driver.multiple_click(tab_path(tab_id=cnst.PARAMETERS_SUB_TAB_ID, classname="nav-link"), 1)
        check_graph_color(dash_br_driver, style_background=style_background, color=graph_color)

        # simulate reloading the page
        page_select(
            dash_br_driver,
            page_path=cnst.FILTERS_PAGE_PATH,
            page_name=cnst.FILTERS_PAGE,
        )
        page_select(
            dash_br_driver,
            page_path=cnst.PARAMETERS_PAGE_PATH,
            page_name=cnst.PARAMETERS_PAGE,
        )

        # check that second tab still active
        dash_br_driver.wait_for_text_to_equal(
            tab_path(tab_id=cnst.PARAMETERS_SUB_TAB_ID, classname="active nav-link"),
            cnst.PARAMETERS_SUB_TAB_CONTAINER_TWO,
        )

        # check that graph and theme color is the same as before page reload
        check_graph_color(dash_br_driver, style_background=style_background, color=graph_color)
        check_theme_color(dash_br_driver, color=theme_color)

    if dashboard_id == cnst.DASHBOARD_DEFAULT:
        # dashboard switched to dark theme
        dash_br_driver.multiple_click(theme_toggle_path(), 1)
        _logic(style_background=cnst.STYLE_TRANSPARENT, graph_color=cnst.RGBA_TRANSPARENT, theme_color=cnst.THEME_DARK)
    else:
        # dashboard switched to light theme
        dash_br_driver.multiple_click(theme_toggle_path(), 1)
        _logic(style_background=cnst.STYLE_TRANSPARENT, graph_color=cnst.RGBA_TRANSPARENT, theme_color=cnst.THEME_LIGHT)
