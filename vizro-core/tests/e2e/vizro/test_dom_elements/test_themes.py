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
    "dash_br, dashboard_id",
    [({"port": cnst.DEFAULT_PORT}, cnst.DASHBOARD_DEFAULT)],
    ids=[cnst.DASHBOARD_DEFAULT],
    indirect=["dash_br"],
)
def test_themes(dash_br, dashboard_id):
    page_select(dash_br, page_path=cnst.FILTERS_PAGE_PATH, page_name=cnst.FILTERS_PAGE, graph_id=cnst.SCATTER_GRAPH_ID)

    if dashboard_id == cnst.DASHBOARD_DEFAULT:
        check_graph_color(dash_br, style_background=cnst.STYLE_TRANSPARENT, color=cnst.RGBA_TRANSPARENT)
        check_theme_color(dash_br, color=cnst.THEME_LIGHT)
        dash_br.multiple_click(theme_toggle_path(), 1)
        check_graph_color(dash_br, style_background=cnst.STYLE_TRANSPARENT, color=cnst.RGBA_TRANSPARENT)
        check_theme_color(dash_br, color=cnst.THEME_DARK)
        dash_br.multiple_click(theme_toggle_path(), 1)
        check_graph_color(dash_br, style_background=cnst.STYLE_TRANSPARENT, color=cnst.RGBA_TRANSPARENT)
        check_theme_color(dash_br, color=cnst.THEME_LIGHT)
    else:
        check_graph_color(dash_br, style_background=cnst.STYLE_TRANSPARENT, color=cnst.RGBA_TRANSPARENT)
        check_theme_color(dash_br, color=cnst.THEME_DARK)
        dash_br.multiple_click(theme_toggle_path(), 1)
        check_graph_color(dash_br, style_background=cnst.STYLE_TRANSPARENT, color=cnst.RGBA_TRANSPARENT)
        check_theme_color(dash_br, color=cnst.THEME_LIGHT)
        dash_br.multiple_click(theme_toggle_path(), 1)
        check_graph_color(dash_br, style_background=cnst.STYLE_TRANSPARENT, color=cnst.RGBA_TRANSPARENT)
        check_theme_color(dash_br, color=cnst.THEME_DARK)


@pytest.mark.parametrize(
    "dash_br, dashboard_id",
    [({"port": cnst.DEFAULT_PORT}, cnst.DASHBOARD_DEFAULT)],
    ids=[cnst.DASHBOARD_DEFAULT],
    indirect=["dash_br"],
)
def test_ag_grid_themes(dash_br, dashboard_id):
    accordion_select(
        dash_br, accordion_name=cnst.AG_GRID_ACCORDION.upper(), accordion_number=cnst.AG_GRID_ACCORDION_NUMBER
    )
    page_select(
        dash_br,
        page_path=cnst.TABLE_AG_GRID_PAGE_PATH,
        page_name=cnst.TABLE_AG_GRID_PAGE,
        graph_id=cnst.BOX_AG_GRID_PAGE_ID,
    )
    if dashboard_id == cnst.DASHBOARD_DEFAULT:
        check_ag_grid_theme_color(dash_br, ag_grid_id=cnst.TABLE_AG_GRID_ID, color=cnst.AG_GRID_LIGHT)
        dash_br.multiple_click(theme_toggle_path(), 1)
        check_ag_grid_theme_color(dash_br, ag_grid_id=cnst.TABLE_AG_GRID_ID, color=cnst.AG_GRID_DARK)
    else:
        check_ag_grid_theme_color(dash_br, ag_grid_id=cnst.TABLE_AG_GRID_ID, color=cnst.AG_GRID_DARK)
        dash_br.multiple_click(theme_toggle_path(), 1)
        check_ag_grid_theme_color(dash_br, ag_grid_id=cnst.TABLE_AG_GRID_ID, color=cnst.AG_GRID_LIGHT)


@pytest.mark.parametrize(
    "dash_br, dashboard_id",
    [({"port": cnst.DEFAULT_PORT}, cnst.DASHBOARD_DEFAULT)],
    ids=[cnst.DASHBOARD_DEFAULT],
    indirect=["dash_br"],
)
def test_themes_page_change(dash_br, dashboard_id):
    page_select(
        dash_br,
        page_path=cnst.PARAMETERS_PAGE_PATH,
        page_name=cnst.PARAMETERS_PAGE,
        graph_id=cnst.BAR_GRAPH_ID,
    )
    dash_br.multiple_click(theme_toggle_path(), 1)

    def _logic(style_background, graph_color, theme_color):
        check_graph_color(dash_br, style_background=style_background, color=graph_color)
        check_theme_color(dash_br, color=theme_color)
        dash_br.multiple_click(tab_path(tab_id=cnst.PARAMETERS_SUB_TAB_ID, classname="nav-link"), 1)
        check_graph_color(dash_br, style_background=style_background, color=graph_color)
        page_select(
            dash_br,
            page_path=cnst.FILTERS_PAGE_PATH,
            page_name=cnst.FILTERS_PAGE,
            graph_id=cnst.SCATTER_GRAPH_ID,
        )
        page_select(
            dash_br,
            page_path=cnst.PARAMETERS_PAGE_PATH,
            page_name=cnst.PARAMETERS_PAGE,
            graph_id=cnst.BAR_GRAPH_ID,
        )
        dash_br.wait_for_text_to_equal(
            tab_path(tab_id=cnst.PARAMETERS_SUB_TAB_ID, classname="active nav-link"),
            cnst.PARAMETERS_SUB_TAB_CONTAINER_TWO,
        )
        check_graph_color(dash_br, style_background=style_background, color=graph_color)
        check_theme_color(dash_br, color=theme_color)

    if dashboard_id == cnst.DASHBOARD_DEFAULT:
        _logic(style_background=cnst.STYLE_TRANSPARENT, graph_color=cnst.RGBA_TRANSPARENT, theme_color=cnst.THEME_DARK)
    else:
        _logic(style_background=cnst.STYLE_TRANSPARENT, graph_color=cnst.RGBA_TRANSPARENT, theme_color=cnst.THEME_LIGHT)
