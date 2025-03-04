import pytest
from e2e.asserts import assert_image_equal, make_screenshot_and_paths
from e2e.vizro import constants as cnst
from e2e.vizro.checkers import check_graph_color, check_theme_color
from e2e.vizro.navigation import accordion_select, page_select
from e2e.vizro.paths import kpi_card_path, nav_card_link_path, theme_toggle_path
from e2e.vizro.waiters import callbacks_finish_waiter, graph_load_waiter


def image_assertion(func):
    """Wait until all callbacks are finished and compare screenshots."""

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
    # check if first kpi card have correct value
    dash_br.wait_for_text_to_equal(kpi_card_path(), "73902")


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
    # check if column 'country' is available
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
    # check if country Albania is available
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
        graph_id=cnst.LINE_INTERACTIONS_ID,
    )
    # click on Bosnia and Herzegovina country
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
    # check if first kpi card have correct value
    dash_br_driver.wait_for_text_to_equal(kpi_card_path(), "73902")


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
