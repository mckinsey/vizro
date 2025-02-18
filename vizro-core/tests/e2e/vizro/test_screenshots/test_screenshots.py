from e2e.asserts import assert_image_equal, make_screenshot_and_paths
from e2e.vizro import constants as cnst
from e2e.vizro.navigation import page_select
from e2e.vizro.waiters import graph_load_waiter


def image_assertion(func):
    def wrapper(dash_br, request):
        result = func(dash_br)
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
    page_select(
        dash_br,
        page_path=cnst.TABLE_AG_GRID_PAGE_PATH,
        page_name=cnst.TABLE_AG_GRID_PAGE,
        graph_id=cnst.BOX_AG_GRID_PAGE_ID,
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
