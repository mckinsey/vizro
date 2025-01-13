import pytest

import e2e_constants as cnst
from e2e_checkers import (
    check_accordion,
    check_graph_color,
    check_text,
    check_theme_color, check_ag_grid_theme_color,
)
from e2e_helpers import (
    webdriver_click_waiter,
    webdriver_waiter, graph_load_waiter,
)
from e2e_navigation import page_select
from e2e_paths import (
    button_path,
    graph_path,
    href_path,
    nav_card_text_path,
    tab_path,
    theme_toggle_path,
)

pytestmark = pytest.mark.e2e_integration_tests


def test_pages(dash_br_driver):
    graph_load_waiter(dash_br_driver, graph_id=cnst.AREA_GRAPH_ID)
    check_text(dash_br_driver, xpath=href_path(href=cnst.HOME_PAGE_PATH), text=cnst.HOME_PAGE)
    webdriver_click_waiter(dash_br_driver, xpath=nav_card_text_path(href=cnst.FILTERS_PAGE_PATH))
    graph_load_waiter(dash_br_driver, graph_id=cnst.SCATTER_GRAPH_ID)
    check_text(dash_br_driver, xpath=href_path(href=cnst.FILTERS_PAGE_PATH), text=cnst.FILTERS_PAGE)
    webdriver_click_waiter(dash_br_driver, xpath=nav_card_text_path(href=cnst.HOME_PAGE_PATH))
    graph_load_waiter(dash_br_driver, graph_id=cnst.AREA_GRAPH_ID)
    check_text(dash_br_driver, xpath=href_path(href=cnst.HOME_PAGE_PATH), text=cnst.HOME_PAGE)


def test_active_accordion(dash_br_driver):
    graph_load_waiter(dash_br_driver, graph_id=cnst.AREA_GRAPH_ID)
    webdriver_click_waiter(dash_br_driver, xpath=nav_card_text_path(href=cnst.DATEPICKER_PAGE_PATH))
    graph_load_waiter(dash_br_driver, graph_id=cnst.BAR_POP_DATE_ID)
    check_text(dash_br_driver, xpath=href_path(href=cnst.DATEPICKER_PAGE_PATH), text=cnst.DATEPICKER_PAGE)
    check_accordion(dash_br_driver, accordion_name=cnst.DATEPICKER_ACCORDION.upper())


@pytest.mark.parametrize(
    "dash_br_driver, dashboard_id",
    [({"port": cnst.DEFAULT_PORT}, cnst.DASHBOARD_DEFAULT)],
    ids=[cnst.DASHBOARD_DEFAULT],
    indirect=["dash_br_driver"],
)
def test_themes(dash_br_driver, dashboard_id):
    page_select(dash_br_driver, page_name=cnst.FILTERS_PAGE, graph_id=cnst.SCATTER_GRAPH_ID)
    graph_xpath = graph_path(cnst.SCATTER_GRAPH_ID)
    if dashboard_id == cnst.DASHBOARD_DEFAULT:
        check_graph_color(dash_br_driver, xpath=graph_xpath, style_background=cnst.STYLE_GREY, color=cnst.HEX_GREY)
        check_theme_color(dash_br_driver, color=cnst.THEME_LIGHT)
        webdriver_click_waiter(dash_br_driver, xpath=theme_toggle_path())
        check_graph_color(dash_br_driver, xpath=graph_xpath, style_background=cnst.STYLE_BLACK, color=cnst.HEX_BLACK)
        check_theme_color(dash_br_driver, color=cnst.THEME_DARK)
        webdriver_click_waiter(dash_br_driver, xpath=theme_toggle_path())
        check_graph_color(dash_br_driver, xpath=graph_xpath, style_background=cnst.STYLE_GREY, color=cnst.HEX_GREY)
        check_theme_color(dash_br_driver, color=cnst.THEME_LIGHT)
    else:
        check_graph_color(dash_br_driver, xpath=graph_xpath, style_background=cnst.STYLE_BLACK, color=cnst.HEX_BLACK)
        check_theme_color(dash_br_driver, color=cnst.THEME_DARK)
        webdriver_click_waiter(dash_br_driver, xpath=theme_toggle_path())
        check_graph_color(dash_br_driver, xpath=graph_xpath, style_background=cnst.STYLE_GREY, color=cnst.HEX_GREY)
        check_theme_color(dash_br_driver, color=cnst.THEME_LIGHT)
        webdriver_click_waiter(dash_br_driver, xpath=theme_toggle_path())
        check_graph_color(dash_br_driver, xpath=graph_xpath, style_background=cnst.STYLE_BLACK, color=cnst.HEX_BLACK)
        check_theme_color(dash_br_driver, color=cnst.THEME_DARK)


@pytest.mark.parametrize(
    "dash_br_driver, dashboard_id",
    [({"port": cnst.DEFAULT_PORT}, cnst.DASHBOARD_DEFAULT)],
    ids=[cnst.DASHBOARD_DEFAULT],
    indirect=["dash_br_driver"],
)
def test_ag_grid_themes(dash_br_driver, dashboard_id):
    page_select(dash_br_driver, page_name=cnst.TABLE_AG_GRID_PAGE,
                graph_id=cnst.BOX_AG_GRID_PAGE_ID, accordion_name=cnst.AG_GRID_ACCORDION)
    if dashboard_id == cnst.DASHBOARD_DEFAULT:
        check_ag_grid_theme_color(dash_br_driver, ag_grid_id=cnst.TABLE_AG_GRID_ID, color=cnst.AG_GRID_LIGHT)
        webdriver_click_waiter(dash_br_driver, xpath=theme_toggle_path())
        check_ag_grid_theme_color(dash_br_driver, ag_grid_id=cnst.TABLE_AG_GRID_ID, color=cnst.AG_GRID_DARK)
    else:
        check_ag_grid_theme_color(dash_br_driver, ag_grid_id=cnst.TABLE_AG_GRID_ID, color=cnst.AG_GRID_DARK)
        webdriver_click_waiter(dash_br_driver, xpath=theme_toggle_path())
        check_ag_grid_theme_color(dash_br_driver, ag_grid_id=cnst.TABLE_AG_GRID_ID, color=cnst.AG_GRID_LIGHT)


@pytest.mark.parametrize(
    "dash_br_driver, dashboard_id",
    [({"port": cnst.DEFAULT_PORT}, cnst.DASHBOARD_DEFAULT)],
    ids=[cnst.DASHBOARD_DEFAULT],
    indirect=["dash_br_driver"],
)
def test_themes_page_change(dash_br_driver, dashboard_id):
    page_select(dash_br_driver, page_name=cnst.PARAMETERS_PAGE, graph_id=cnst.BAR_GRAPH_ID)
    webdriver_click_waiter(dash_br_driver, xpath=theme_toggle_path())
    graph_bar = graph_path(graph_id=cnst.BAR_GRAPH_ID)
    graph_histogram = graph_path(graph_id=cnst.HISTOGRAM_GRAPH_ID)

    def _logic(style_background, graph_color, theme_color):
        check_graph_color(dash_br_driver, xpath=graph_bar, style_background=style_background, color=graph_color)
        check_theme_color(dash_br_driver, color=theme_color)
        webdriver_click_waiter(dash_br_driver, tab_path(tab_id=cnst.PARAMETERS_SUB_TAB_CONTAINER_TWO, classname="nav-link"))
        check_graph_color(dash_br_driver, xpath=graph_bar, style_background=style_background, color=graph_color)
        page_select(dash_br_driver, page_name=cnst.FILTERS_PAGE, graph_id=cnst.SCATTER_GRAPH_ID)
        page_select(dash_br_driver, page_name=cnst.PARAMETERS_PAGE, graph_id=cnst.BAR_GRAPH_ID)
        webdriver_waiter(
            dash_br_driver, tab_path(tab_id=cnst.PARAMETERS_SUB_TAB_CONTAINER_TWO, classname="active nav-link")
        )
        check_graph_color(dash_br_driver, xpath=graph_bar, style_background=style_background, color=graph_color)
        check_graph_color(dash_br_driver, xpath=graph_histogram, style_background=style_background, color=graph_color)
        check_theme_color(dash_br_driver, color=theme_color)

    if dashboard_id == cnst.DASHBOARD_DEFAULT:
        _logic(style_background=cnst.STYLE_BLACK, graph_color=cnst.HEX_BLACK, theme_color=cnst.THEME_DARK)
    else:
        _logic(style_background=cnst.STYLE_BLACK, graph_color=cnst.HEX_GREY, theme_color=cnst.THEME_LIGHT)


def test_404_page(dash_br_driver):
    graph_load_waiter(dash_br_driver, graph_id=cnst.AREA_GRAPH_ID)
    webdriver_click_waiter(dash_br_driver, xpath=nav_card_text_path(href=cnst.PAGE_404_PATH))
    webdriver_waiter(dash_br_driver, xpath=button_path(button_text="Take me home"))
    webdriver_click_waiter(dash_br_driver, xpath=button_path(button_text="Take me home"))
    graph_load_waiter(dash_br_driver, graph_id=cnst.AREA_GRAPH_ID)
    check_text(dash_br_driver, xpath=href_path(href=cnst.HOME_PAGE_PATH), text=cnst.HOME_PAGE)


@pytest.mark.parametrize(
    "dash_br_driver",
    [{"port": cnst.DEFAULT_PORT, "path": "?unexpercted_param=parampampam"}],
    indirect=["dash_br_driver"],
)
def test_unexpected_query_parameters_page(dash_br_driver):
    graph_load_waiter(dash_br_driver, graph_id=cnst.AREA_GRAPH_ID)
