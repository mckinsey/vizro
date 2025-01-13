import e2e_constants as cnst
import pytest
from e2e_checkers import (
    check_graph_is_loading,
    check_range_slider_value,
    check_slider_value,
)
from e2e_helpers import graph_load_waiter, webdriver_click_waiter, webdriver_waiter
from e2e_navigation import page_select
from e2e_paths import (
    checklist_value_path,
    dropdown_arrow_path,
    dropdown_clear_all_path,
    dropdown_value_path,
    kpi_card_text_path,
    radio_items_value_path,
    range_slider_value_path,
    slider_value_path,
)
from hamcrest import assert_that, equal_to
from selenium.webdriver.common.by import By

pytestmark = pytest.mark.e2e_integration_tests


def test_dropdown(dash_br_driver):
    page_select(dash_br_driver, page_name=cnst.FILTERS_PAGE, graph_id=cnst.SCATTER_GRAPH_ID)
    webdriver_click_waiter(dash_br_driver, xpath=dropdown_clear_all_path())
    webdriver_click_waiter(dash_br_driver, xpath=dropdown_arrow_path())
    webdriver_click_waiter(dash_br_driver, xpath=dropdown_value_path(value=1))
    check_graph_is_loading(dash_br_driver, graph_id=cnst.SCATTER_GRAPH_ID)


def test_radio_items(dash_br_driver):
    page_select(dash_br_driver, page_name=cnst.FILTERS_PAGE, graph_id=cnst.SCATTER_GRAPH_ID)
    webdriver_click_waiter(dash_br_driver, xpath=radio_items_value_path(title="Species", value=2))
    check_graph_is_loading(dash_br_driver, graph_id=cnst.SCATTER_GRAPH_ID)


def test_checklist(dash_br_driver):
    page_select(dash_br_driver, page_name=cnst.FILTERS_PAGE, graph_id=cnst.SCATTER_GRAPH_ID)
    webdriver_click_waiter(dash_br_driver, xpath=checklist_value_path(title="Species", value=2))
    check_graph_is_loading(dash_br_driver, graph_id=cnst.SCATTER_GRAPH_ID)


def test_slider(dash_br_driver):
    page_select(dash_br_driver, page_name=cnst.FILTERS_PAGE, graph_id=cnst.SCATTER_GRAPH_ID)
    webdriver_click_waiter(
        dash_br_driver,
        slider_value_path(elem_id=cnst.SLIDER_FILTER_FILTERS_PAGE, value=2),
    )
    check_graph_is_loading(dash_br_driver, graph_id=cnst.SCATTER_GRAPH_ID)
    check_slider_value(dash_br_driver, num="0.6", elem_id=cnst.SLIDER_FILTER_FILTERS_PAGE)


@pytest.mark.xfail(reason="Should be fixed later in vizro by Petar")
# Right now is failing with the next error:
# AssertionError: Element number is '4', but expected number is '4.3'
def test_range_slider(dash_br_driver):
    page_select(dash_br_driver, page_name=cnst.FILTERS_PAGE)
    graph_load_waiter(dash_br_driver, graph_id=cnst.SCATTER_GRAPH_ID)
    webdriver_click_waiter(
        dash_br_driver,
        range_slider_value_path(elem_id=cnst.RANGE_SLIDER_FILTER_FILTERS_PAGE, value=4),
    )
    check_graph_is_loading(dash_br_driver, graph_id=cnst.SCATTER_GRAPH_ID)
    check_range_slider_value(
        dash_br_driver, left_num="4.3", right_num="7", elem_id=cnst.RANGE_SLIDER_FILTER_FILTERS_PAGE
    )


def test_dropdown_homepage(dash_br_driver):
    graph_load_waiter(dash_br_driver, graph_id=cnst.AREA_GRAPH_ID)
    webdriver_click_waiter(dash_br_driver, xpath=dropdown_clear_all_path())
    webdriver_click_waiter(dash_br_driver, xpath=dropdown_arrow_path())
    webdriver_click_waiter(dash_br_driver, xpath=dropdown_value_path(value=1))
    check_graph_is_loading(dash_br_driver, cnst.AREA_GRAPH_ID)


def test_dropdown_kpi_indicators_page(dash_br_driver):
    page_select(dash_br_driver, page_name=cnst.KPI_INDICATORS_PAGE)
    webdriver_waiter(dash_br_driver, xpath=kpi_card_text_path())
    values = dash_br_driver.find_elements(by=By.XPATH, value=kpi_card_text_path())
    values_text = [value.text for value in values]
    assert_that(
        actual_or_assertion=values_text,
        matcher=equal_to(
            [
                "73902",
                "24634.0",
                "6434.0",
                "72159",
                "73902",
                "6434.0",
                "$73902.00",
                "24634€",
                "6434.0",
            ]
        ),
    )
    webdriver_click_waiter(dash_br_driver, xpath=dropdown_clear_all_path())
    webdriver_click_waiter(dash_br_driver, xpath=dropdown_arrow_path())
    webdriver_click_waiter(dash_br_driver, xpath=dropdown_value_path(value=2))
    webdriver_waiter(dash_br_driver, xpath=kpi_card_text_path())
    values = dash_br_driver.find_elements(by=By.XPATH, value=kpi_card_text_path())
    values_text = [value.text for value in values]
    assert_that(
        actual_or_assertion=values_text,
        matcher=equal_to(
            [
                "67434",
                "67434.0",
                "67434.0",
                "65553",
                "67434",
                "67434.0",
                "$67434.00",
                "67434€",
                "67434.0",
            ]
        ),
    )
