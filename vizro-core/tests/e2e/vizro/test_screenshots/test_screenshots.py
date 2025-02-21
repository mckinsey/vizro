import subprocess
from pathlib import Path

import pytest
from e2e.asserts import assert_image_equal, assert_pixelmatch, make_screenshot_and_paths
from e2e.vizro import constants as cnst
from e2e.vizro.checkers import check_graph_color, check_theme_color
from e2e.vizro.navigation import accordion_select, page_select, select_slider_handler
from e2e.vizro.paths import nav_card_link_path, theme_toggle_path
from e2e.vizro.waiters import callbacks_finish_waiter, graph_load_waiter


def image_assertion(func):
    def wrapper(dash_br, request):
        result = func(dash_br)
        callbacks_finish_waiter(dash_br)
        result_image_path, expected_image_path = make_screenshot_and_paths(dash_br.driver, request.node.name)
        assert_image_equal(result_image_path, expected_image_path)
        return result

    return wrapper


@image_assertion
def test_kpi_indicators_page(dash_br):
    page_select(dash_br, page_path=cnst.KPI_INDICATORS_PAGE_PATH, page_name=cnst.KPI_INDICATORS_PAGE)
    dash_br.wait_for_text_to_equal(".card-body", "73902")


@image_assertion
def test_homepage(dash_br):
    graph_load_waiter(dash_br, graph_id=cnst.AREA_GRAPH_ID)


@image_assertion
def test_ag_grid_page(dash_br):
    accordion_select(
        dash_br, accordion_name=cnst.AG_GRID_ACCORDION.upper(), accordion_number=cnst.AG_GRID_ACCORDION_NUMBER
    )
    page_select(
        dash_br,
        page_path=cnst.TABLE_AG_GRID_PAGE_PATH,
        page_name=cnst.TABLE_AG_GRID_PAGE,
        graph_id=cnst.BOX_AG_GRID_PAGE_ID,
    )
    dash_br.wait_for_element(f"div[id='{cnst.TABLE_AG_GRID_ID}'] div:nth-of-type(1) div[col-id='country']")


@image_assertion
def test_table_page(dash_br):
    accordion_select(
        dash_br, accordion_name=cnst.AG_GRID_ACCORDION.upper(), accordion_number=cnst.AG_GRID_ACCORDION_NUMBER
    )
    page_select(
        dash_br,
        page_path=cnst.TABLE_PAGE_PATH,
        page_name=cnst.TABLE_PAGE,
    )
    dash_br.wait_for_text_to_equal(
        f"div[id='{cnst.TABLE_ID}'] tr:nth-of-type(2) div[class='unfocused selectable dash-cell-value']", "Albania"
    )


@image_assertion
def test_table_interactions_page(dash_br):
    accordion_select(
        dash_br, accordion_name=cnst.AG_GRID_ACCORDION.upper(), accordion_number=cnst.AG_GRID_ACCORDION_NUMBER
    )
    page_select(
        dash_br,
        page_path=cnst.TABLE_INTERACTIONS_PAGE_PATH,
        page_name=cnst.TABLE_INTERACTIONS_PAGE,
        graph_id=cnst.LINE_INTERACTIONS_ID_ONE,
    )
    dash_br.multiple_click(
        f"div[id='{cnst.TABLE_INTERACTIONS_ID}'] tr:nth-of-type(5) div[class='unfocused selectable dash-cell-value']", 1
    )


@image_assertion
def test_tabs_parameters_page(dash_br):
    page_select(
        dash_br,
        page_path=cnst.PARAMETERS_PAGE_PATH,
        page_name=cnst.PARAMETERS_PAGE,
        graph_id=cnst.BAR_GRAPH_ID,
    )


@pytest.mark.parametrize(
    "cache, slider_id",
    [
        ("cached", cnst.SLIDER_DYNAMIC_DATA_CACHED_ID, cnst.SCATTER_DYNAMIC_CACHED_ID),
        ("cached_not", cnst.SLIDER_DYNAMIC_DATA_ID, cnst.SCATTER_DYNAMIC_ID),
    ],
)
def test_data_dynamic_parametrization(dash_br, cache, slider_id):
    first_screen = f"{cache}_screen_first_test_data_dynamic_parametrization.png"
    second_screen = f"{cache}_screen_second_test_data_dynamic_parametrization.png"
    third_screen = f"{cache}_screen_third_test_data_dynamic_parametrization.png"
    accordion_select(
        dash_br, accordion_name=cnst.DYNAMIC_DATA_ACCORDION.upper(), accordion_number=cnst.DYNAMIC_DATA_ACCORDION_NUMBER
    )
    page_select(
        dash_br,
        page_path=cnst.DYNAMIC_DATA_PAGE_PATH,
        page_name=cnst.DYNAMIC_DATA_PAGE,
        graph_id=cnst.SCATTER_DYNAMIC_ID,
    )
    select_slider_handler(dash_br, elem_id=slider_id, value=2)
    select_slider_handler(dash_br, elem_id=slider_id, value=1)
    callbacks_finish_waiter(dash_br)
    dash_br.driver.save_screenshot(first_screen)
    select_slider_handler(dash_br, elem_id=slider_id, value=6)
    callbacks_finish_waiter(dash_br)
    dash_br.driver.save_screenshot(second_screen)
    select_slider_handler(dash_br, elem_id=slider_id, value=2)
    select_slider_handler(dash_br, elem_id=slider_id, value=1)
    callbacks_finish_waiter(dash_br)
    dash_br.driver.save_screenshot(third_screen)
    assert_pixelmatch(first_screen, third_screen)
    try:
        assert_pixelmatch(first_screen, second_screen)
        pytest.fail("Images should be different")
    except subprocess.CalledProcessError:
        pass
    for file in Path(".").glob("*test_data_dynamic_parametrization*"):
        file.unlink()


@image_assertion
def test_nested_tabs_filters_page(dash_br):
    page_select(dash_br, page_path=cnst.FILTERS_PAGE_PATH, page_name=cnst.FILTERS_PAGE, graph_id=cnst.SCATTER_GRAPH_ID)


@pytest.mark.parametrize(
    "dash_br_driver", [({"port": cnst.ONE_PAGE_PORT})], ids=["one_page"], indirect=["dash_br_driver"]
)
@image_assertion
def test_export_action_page(dash_br_driver):
    graph_load_waiter(dash_br_driver, graph_id=cnst.LINE_EXPORT_ID)


@pytest.mark.parametrize(
    "dash_br_driver",
    [
        ({"port": cnst.NAVBAR_ACCORDIONS_PORT}),
        ({"port": cnst.NAVBAR_NAVLINK_PORT}),
    ],
    ids=["navbar_accordions", "navbar_navlink"],
    indirect=["dash_br_driver"],
)
@image_assertion
def test_navbar_kpi_indicators_page(dash_br_driver):
    dash_br_driver.multiple_click(nav_card_link_path(cnst.KPI_INDICATORS_PAGE_PATH), 1)
    dash_br_driver.wait_for_text_to_equal(".card-body", "73902")


@pytest.mark.parametrize(
    "dash_br_driver", [({"port": cnst.NAVBAR_PAGES_PORT})], ids=["navbar_pages"], indirect=["dash_br_driver"]
)
@image_assertion
def test_navbar_filters_page(dash_br_driver):
    dash_br_driver.multiple_click(nav_card_link_path(cnst.FILTERS_PAGE_PATH), 1)


@pytest.mark.mobile_screenshots
@image_assertion
def test_homepage_mobile(dash_br):
    graph_load_waiter(dash_br, graph_id=cnst.AREA_GRAPH_ID)


@pytest.mark.mobile_screenshots
@pytest.mark.parametrize(
    "dash_br_driver", [({"path": "filter-interactions-page"})], ids=["mobile"], indirect=["dash_br_driver"]
)
@image_assertion
def test_filter_interactions_page(dash_br_driver):
    graph_load_waiter(dash_br_driver, graph_id=cnst.BOX_INTERACTIONS_ID)


@pytest.mark.mobile_screenshots
@pytest.mark.parametrize(
    "dash_br_driver", [({"path": "filter-interactions-page"})], ids=["mobile"], indirect=["dash_br_driver"]
)
@image_assertion
def test_filter_interactions_dark_theme_page(dash_br_driver):
    graph_load_waiter(dash_br_driver, graph_id=cnst.BOX_INTERACTIONS_ID)
    dash_br_driver.multiple_click(theme_toggle_path(), 1)
    check_graph_color(dash_br_driver, style_background=cnst.STYLE_TRANSPARENT, color=cnst.RGBA_TRANSPARENT)
    check_theme_color(dash_br_driver, color=cnst.THEME_DARK)
