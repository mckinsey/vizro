import pytest
from e2e.vizro import constants as cnst
from e2e.vizro.checkers import check_graph_is_loading
from e2e.vizro.navigation import page_select


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_interactions(dash_br):
    page_select(
        dash_br,
        page_path=cnst.FILTER_INTERACTIONS_PAGE_PATH,
        page_name=cnst.FILTER_INTERACTIONS_PAGE,
        graph_id=cnst.SCATTER_INTERACTIONS_ID,
    )
    dash_br.click_at_coord_fractions(f"#{cnst.SCATTER_INTERACTIONS_ID} path:nth-of-type(20)", 0, 1)
    check_graph_is_loading(dash_br, cnst.BOX_DYNAMIC_FILTERS_ID)

    # box_xpath = graph_interaction_path(
    #     cnst.BOX_INTER_GRAPH_ID, "trace boxes", "path", 9
    # )
    # check_elem_color(dash_br_driver, box_xpath, cnst.RGBA_ORANGE, "fill")
    #
    # webdriver_waiter(dash_br_driver, graph_xaxis_tick_path(cnst.BOX_INTER_GRAPH_ID))
    # webdriver_click_waiter(dash_br_driver, dropdown_clear_path(dropdown_path()))
    # webdriver_click_waiter(dash_br_driver, dropdown_arrow_path(dropdown_path()))
    # webdriver_click_waiter(dash_br_driver, dropdown_value_path(dropdown_path(), 3))
    # check_graph_is_loading(dash_br_driver, cnst.BOX_INTER_GRAPH_ID)
    # webdriver_waiter(dash_br_driver, graph_xaxis_tick_path(cnst.BOX_INTER_GRAPH_ID))
    #
    # webdriver_waiter(dash_br_driver, graph_xaxis_tick_path(cnst.BOX_INTER_GRAPH_ID))
    # webdriver_waiter(dash_br_driver, radio_items_path("title"))
    # webdriver_click_waiter(
    #     dash_br_driver, radio_items_value_path(radio_items_path("title"), 1)
    # )
    # check_graph_is_loading(dash_br_driver, cnst.BOX_INTER_GRAPH_ID)
    # webdriver_waiter(dash_br_driver, graph_xaxis_tick_path(cnst.BOX_INTER_GRAPH_ID))
    # time.sleep(1)
    # check_text(dash_br_driver, graph_titles_path(cnst.BOX_INTER_GRAPH_ID), "red")
