import e2e.vizro.constants as cnst
import pytest
from e2e.vizro.checkers import check_accordion_active
from e2e.vizro.paths import nav_card_link_path, page_title_path
from e2e.vizro.waiters import graph_load_waiter


def test_pages(dash_br, check_graph_is_loaded_thread):
    """Test of going from homepage to filters page and back using card link."""
    # open homepage and check title text
    dash_br.wait_for_text_to_equal(page_title_path(), cnst.HOME_PAGE)

    # open filters page using card link and check title text
    check_graph_is_loaded_thread(graph_id=cnst.SCATTER_GRAPH_ID)
    dash_br.multiple_click(nav_card_link_path(href=cnst.FILTERS_PAGE_PATH), 1)
    dash_br.wait_for_text_to_equal(page_title_path(), text=cnst.FILTERS_PAGE)

    # open homepage using card link and check title text
    check_graph_is_loaded_thread(graph_id=cnst.AREA_GRAPH_ID)
    dash_br.multiple_click(nav_card_link_path(href=cnst.HOME_PAGE_PATH), 1)
    dash_br.wait_for_text_to_equal(page_title_path(), cnst.HOME_PAGE)


def test_active_accordion(dash_br, check_graph_is_loaded_thread):
    """Test opening page from card link and checking appropriate accordion is opened."""
    check_graph_is_loaded_thread(graph_id=cnst.BAR_POP_DATE_ID)
    dash_br.multiple_click(nav_card_link_path(href=f"/{cnst.DATEPICKER_PAGE}"), 1)
    dash_br.wait_for_text_to_equal(page_title_path(), cnst.DATEPICKER_PAGE)
    check_accordion_active(dash_br, accordion_name=cnst.DATEPICKER_ACCORDION)


def test_404_page(dash_br, check_graph_is_loaded_thread):
    """Test opening page that doesn't exist."""
    dash_br.multiple_click(nav_card_link_path(href=cnst.PAGE_404_PATH), 1)
    dash_br.wait_for_text_to_equal("a[class='mt-4 btn btn-primary']", "Take me home")
    check_graph_is_loaded_thread(graph_id=cnst.AREA_GRAPH_ID)
    dash_br.multiple_click("a[class='mt-4 btn btn-primary']", 1)
    dash_br.wait_for_text_to_equal(page_title_path(), cnst.HOME_PAGE)


@pytest.mark.parametrize(
    "dash_br_driver",
    [{"path": "?unexpercted_param=parampampam"}],
    indirect=["dash_br_driver"],
)
def test_unexpected_query_parameters_page(dash_br_driver):
    """Test opening page with not existent parameter."""
    graph_load_waiter(dash_br_driver)
