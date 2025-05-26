import os
import time

import pytest
from e2e.asserts import assert_image_equal, make_screenshot_and_paths
from e2e.vizro import constants as cnst
from e2e.vizro.checkers import check_graph_color, check_theme_color
from e2e.vizro.navigation import (
    accordion_select,
    click_element_by_xpath_selenium,
    hover_over_element_by_xpath_selenium,
    page_select,
)
from e2e.vizro.paths import kpi_card_path, nav_card_link_path, theme_toggle_path
from e2e.vizro.waiters import callbacks_finish_waiter, graph_load_waiter


def image_assertion(func):
    """Wait until all callbacks are finished and compare screenshots."""

    def wrapper(dash_br, request):
        result = func(dash_br)
        callbacks_finish_waiter(dash_br)
        time.sleep(1)  # to finish page loading
        result_image_path, expected_image_path = make_screenshot_and_paths(dash_br.driver, request.node.name)
        assert_image_equal(result_image_path, expected_image_path)
        return result

    return wrapper


@image_assertion
def test_kpi_indicators_page(dash_br):
    page_select(dash_br, page_name=cnst.KPI_INDICATORS_PAGE, graph_check=False)
    # check if first kpi card have correct value
    dash_br.wait_for_text_to_equal(kpi_card_path(), "73902")


@image_assertion
def test_homepage(dash_br):
    graph_load_waiter(dash_br, graph_id=cnst.AREA_GRAPH_ID)


@image_assertion
def test_ag_grid_page(dash_br):
    accordion_select(dash_br, accordion_name=cnst.AG_GRID_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.TABLE_AG_GRID_PAGE,
    )
    # check if column 'country' is available
    dash_br.wait_for_element(f"div[id='{cnst.TABLE_AG_GRID_ID}'] div:nth-of-type(1) div[col-id='country']")


@image_assertion
def test_table_page(dash_br):
    accordion_select(dash_br, accordion_name=cnst.AG_GRID_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.TABLE_PAGE,
        graph_check=False,
    )
    # check if country Albania is available
    dash_br.wait_for_text_to_equal(
        f"div[id='{cnst.TABLE_ID}'] tr:nth-of-type(2) div[class='unfocused selectable dash-cell-value']", "Albania"
    )


@image_assertion
def test_table_interactions_page(dash_br):
    accordion_select(dash_br, accordion_name=cnst.AG_GRID_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.TABLE_INTERACTIONS_PAGE,
    )
    # click on Bosnia and Herzegovina country
    dash_br.multiple_click(
        f"div[id='{cnst.TABLE_INTERACTIONS_ID}'] tr:nth-of-type(5) div[class='unfocused selectable dash-cell-value']", 1
    )


@image_assertion
def test_tabs_parameters_page(dash_br):
    page_select(
        dash_br,
        page_name=cnst.PARAMETERS_PAGE,
        page_path=cnst.PARAMETERS_PAGE_PATH,
    )


@image_assertion
def test_nested_tabs_filters_page(dash_br):
    page_select(dash_br, page_path=cnst.FILTERS_PAGE_PATH, page_name=cnst.FILTERS_PAGE)


@image_assertion
def test_filters_inside_containers_page(dash_br):
    page_select(
        dash_br, page_path=cnst.FILTERS_INSIDE_CONTAINERS_PAGE_PATH, page_name=cnst.FILTERS_INSIDE_CONTAINERS_PAGE
    )


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
    dash_br_driver.multiple_click(nav_card_link_path(f"/{cnst.KPI_INDICATORS_PAGE}"), 1)
    # check if first kpi card have correct value
    dash_br_driver.wait_for_text_to_equal(kpi_card_path(), "73902")


@pytest.mark.parametrize(
    "dash_br_driver", [({"port": cnst.NAVBAR_PAGES_PORT})], ids=["navbar_pages"], indirect=["dash_br_driver"]
)
@image_assertion
def test_navbar_filters_page(dash_br_driver):
    dash_br_driver.multiple_click(nav_card_link_path(cnst.FILTERS_PAGE_PATH), 1)


@image_assertion
def test_container_variants_light_theme(dash_br):
    accordion_select(dash_br, accordion_name=cnst.CONTAINER_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.CONTAINER_VARIANTS_PAGE,
    )


@image_assertion
def test_container_variants_dark_theme(dash_br):
    style_background = cnst.STYLE_TRANSPARENT_FIREFOX if os.getenv("BROWSER") == "firefox" else cnst.STYLE_TRANSPARENT
    accordion_select(dash_br, accordion_name=cnst.CONTAINER_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.CONTAINER_VARIANTS_PAGE,
    )
    dash_br.multiple_click(theme_toggle_path(), 1)
    check_graph_color(dash_br, style_background=style_background, color=cnst.RGBA_TRANSPARENT)
    check_theme_color(dash_br, color=cnst.THEME_DARK)


@image_assertion
def test_flex_default_layout(dash_br):
    accordion_select(dash_br, accordion_name=cnst.LAYOUT_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.LAYOUT_FLEX_DEFAULT,
        graph_check=False,
    )


@image_assertion
def test_flex_layout_all_params(dash_br):
    accordion_select(dash_br, accordion_name=cnst.LAYOUT_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.LAYOUT_FLEX_ALL_PARAMS,
        graph_check=False,
    )


@image_assertion
def test_flex_layout_direction_and_graph(dash_br):
    accordion_select(dash_br, accordion_name=cnst.LAYOUT_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.LAYOUT_FLEX_DIRECTION_AND_GRAPH,
    )


@image_assertion
def test_flex_layout_gap_and_table(dash_br):
    accordion_select(dash_br, accordion_name=cnst.LAYOUT_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.LAYOUT_FLEX_GAP_AND_TABLE,
        graph_check=False,
    )

    # check if Total_bill 16.99 is available
    dash_br.wait_for_text_to_equal(
        "div[class='dash-table-container'] tr:nth-of-type(2) div[class='unfocused selectable dash-cell-value']", "16.99"
    )


@image_assertion
def test_flex_layout_wrap_and_ag_grid(dash_br):
    accordion_select(dash_br, accordion_name=cnst.LAYOUT_ACCORDION)
    page_select(dash_br, page_name=cnst.LAYOUT_FLEX_WRAP_AND_AG_GRID, graph_check=False)

    # check if column 'Total_bill' is available
    dash_br.wait_for_element("div[class='ag-theme-quartz ag-theme-vizro'] div:nth-of-type(1) div[col-id='total_bill']")


@image_assertion
def test_extra_parameter(dash_br):
    accordion_select(dash_br, accordion_name=cnst.LAYOUT_ACCORDION)
    page_select(dash_br, page_name=cnst.EXTRAS_PAGE)

    # open datepicker calendar and close it to scroll to the end of the page
    dash_br.multiple_click("button[class*='DatePickerInput']", 2)
    dash_br.wait_for_no_elements('div[data-calendar="true"]')


@image_assertion
def test_controls_tooltip_and_icon_light_theme(dash_br):
    accordion_select(dash_br, accordion_name=cnst.LAYOUT_ACCORDION)
    page_select(dash_br, page_name=cnst.EXTRAS_PAGE)

    # open datepicker calendar and close it to scroll to the end of the page
    dash_br.multiple_click("button[class*='DatePickerInput']", 2)
    dash_br.wait_for_no_elements('div[data-calendar="true"]')

    # hover over dropdown icon and wait for the tooltip appear
    hover_over_element_by_xpath_selenium(
        dash_br, f"//*[@class='material-symbols-outlined tooltip-icon'][text()='{cnst.DROPDOWN_TOOLTIP_ICON}']"
    )
    dash_br.wait_for_text_to_equal(".tooltip-inner p", cnst.DROPDOWN_TOOLTIP_TEXT)


@image_assertion
def test_controls_tooltip_and_icon_dark_theme(dash_br):
    accordion_select(dash_br, accordion_name=cnst.LAYOUT_ACCORDION)
    page_select(dash_br, page_name=cnst.EXTRAS_PAGE)

    # switch theme to dark
    dash_br.multiple_click(theme_toggle_path(), 1)

    # open datepicker calendar and close it to scroll to the end of the page
    dash_br.multiple_click("button[class*='DatePickerInput']", 2)
    dash_br.wait_for_no_elements('div[data-calendar="true"]')

    # hover over dropdown icon and wait for the tooltip appear
    hover_over_element_by_xpath_selenium(
        dash_br, f"//*[@class='material-symbols-outlined tooltip-icon'][text()='{cnst.CHECKLIST_TOOLTIP_ICON}']"
    )
    dash_br.wait_for_text_to_equal(".tooltip-inner p", cnst.CHECKLIST_TOOLTIP_TEXT)


@image_assertion
def test_button_styles(dash_br):
    accordion_select(dash_br, accordion_name=cnst.LAYOUT_ACCORDION)
    page_select(dash_br, page_name=cnst.BUTTONS_PAGE, graph_check=False)


@image_assertion
def test_collapsible_containers_grid(dash_br):
    accordion_select(dash_br, accordion_name=cnst.LAYOUT_ACCORDION)
    page_select(dash_br, page_name=cnst.COLLAPSIBLE_CONTAINERS_GRID)


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@image_assertion
def test_collapsible_containers_grid_switched(dash_br):
    accordion_select(dash_br, accordion_name=cnst.LAYOUT_ACCORDION)
    page_select(dash_br, page_name=cnst.COLLAPSIBLE_CONTAINERS_GRID)

    # close one container and open another
    click_element_by_xpath_selenium(dash_br, '//*[@class="material-symbols-outlined"][text()="keyboard_arrow_down"]')
    click_element_by_xpath_selenium(dash_br, '//*[@class="material-symbols-outlined"][text()="keyboard_arrow_up"]')

    # move mouse to different location of the screen to prevent flakiness because of tooltip.
    dash_br.click_at_coord_fractions(theme_toggle_path(), 0, 1)
    dash_br.wait_for_no_elements('span[aria-describedby*="tooltip"]')


@image_assertion
def test_collapsible_containers_flex(dash_br):
    accordion_select(dash_br, accordion_name=cnst.LAYOUT_ACCORDION)
    page_select(dash_br, page_name=cnst.COLLAPSIBLE_CONTAINERS_GRID)


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@image_assertion
def test_collapsible_containers_flex_switched(dash_br):
    accordion_select(dash_br, accordion_name=cnst.LAYOUT_ACCORDION)
    page_select(dash_br, page_name=cnst.COLLAPSIBLE_CONTAINERS_FLEX)

    # close one container and open another
    click_element_by_xpath_selenium(dash_br, '//*[@class="material-symbols-outlined"][text()="keyboard_arrow_down"]')
    click_element_by_xpath_selenium(dash_br, '//*[@class="material-symbols-outlined"][text()="keyboard_arrow_up"]')

    # move mouse to different location of the screen to prevent flakiness because of tooltip.
    dash_br.click_at_coord_fractions(theme_toggle_path(), 0, 1)
    dash_br.wait_for_no_elements('span[aria-describedby*="tooltip"]')


@pytest.mark.mobile_screenshots
@image_assertion
def test_homepage_mobile(dash_br):
    graph_load_waiter(dash_br, graph_id=cnst.AREA_GRAPH_ID)


@pytest.mark.mobile_screenshots
@pytest.mark.parametrize(
    "dash_br_driver", [({"path": cnst.FILTER_INTERACTIONS_PAGE})], ids=["mobile"], indirect=["dash_br_driver"]
)
@image_assertion
def test_filter_interactions_page(dash_br_driver):
    graph_load_waiter(dash_br_driver, graph_id=cnst.BOX_INTERACTIONS_ID)


@pytest.mark.mobile_screenshots
@pytest.mark.parametrize(
    "dash_br_driver", [({"path": cnst.FILTER_INTERACTIONS_PAGE})], ids=["mobile"], indirect=["dash_br_driver"]
)
@image_assertion
def test_filter_interactions_dark_theme_page(dash_br_driver):
    graph_load_waiter(dash_br_driver, graph_id=cnst.BOX_INTERACTIONS_ID)
    dash_br_driver.multiple_click(theme_toggle_path(), 1)
    check_graph_color(dash_br_driver, style_background=cnst.STYLE_TRANSPARENT, color=cnst.RGBA_TRANSPARENT)
    check_theme_color(dash_br_driver, color=cnst.THEME_DARK)
