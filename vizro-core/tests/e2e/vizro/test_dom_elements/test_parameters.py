from e2e.vizro import constants as cnst
from e2e.vizro.checkers import check_graph_is_loading, check_slider_value
from e2e.vizro.navigation import page_select, select_dropdown_value
from e2e.vizro.paths import slider_value_path


def test_sliders_state(dash_br):
    """Verify that sliders values stays the same after page reload."""
    page_select(
        dash_br,
        page_path=cnst.PARAMETERS_PAGE_PATH,
        page_name=cnst.PARAMETERS_PAGE,
    )

    # change slider value to '0.4'
    dash_br.multiple_click(slider_value_path(elem_id=cnst.SLIDER_PARAMETERS, value=3), 1)
    check_graph_is_loading(dash_br, graph_id=cnst.BAR_GRAPH_ID)
    # change range slider max value to '7'
    dash_br.multiple_click(slider_value_path(elem_id=cnst.RANGE_SLIDER_PARAMETERS, value=4), 1)
    check_graph_is_loading(dash_br, graph_id=cnst.HISTOGRAM_GRAPH_ID)

    # refresh the page
    page_select(dash_br, page_path=cnst.FILTERS_PAGE_PATH, page_name=cnst.FILTERS_PAGE)
    page_select(
        dash_br,
        page_path=cnst.PARAMETERS_PAGE_PATH,
        page_name=cnst.PARAMETERS_PAGE,
    )

    # check that slider value still '0.4'
    check_slider_value(dash_br, expected_end_value="0.4", elem_id=cnst.SLIDER_PARAMETERS)
    # check that range slider max value still '7'
    check_slider_value(dash_br, elem_id=cnst.RANGE_SLIDER_PARAMETERS, expected_start_value="4", expected_end_value="7")


def test_none_parameter(dash_br):
    """Test if one of the parameter values is NONE."""
    page_select(
        dash_br,
        page_path=cnst.PARAMETERS_PAGE_PATH,
        page_name=cnst.PARAMETERS_PAGE,
    )

    # check that specific bar has blue color
    dash_br.wait_for_element(
        f"div[id='{cnst.BAR_GRAPH_ID}'] g:nth-of-type(3) g:nth-of-type(45) path[style*='(0, 0, 255)'"
    )

    # choose NONE parameter
    select_dropdown_value(dash_br, value=1, dropdown_id=cnst.DROPDOWN_PARAMETERS_TWO)
    check_graph_is_loading(dash_br, graph_id=cnst.BAR_GRAPH_ID)

    # check that specific bar has cerulean blue color
    dash_br.wait_for_element(
        f"div[id='{cnst.BAR_GRAPH_ID}'] g:nth-of-type(3) g:nth-of-type(45) path[style*='(57, 73, 171)'"
    )
