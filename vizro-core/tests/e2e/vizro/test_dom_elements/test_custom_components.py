import e2e.vizro.constants as cnst
from e2e.vizro.checkers import check_graph_is_loading, check_slider_value
from e2e.vizro.navigation import page_select, select_dropdown_value
from e2e.vizro.paths import slider_value_path


def test_dropdown(dash_br):
    page_select(
        dash_br,
        page_path=cnst.CUSTOM_COMPONENTS_PAGE_PATH,
        page_name=cnst.CUSTOM_COMPONENTS_PAGE,
        graph_id=cnst.SCATTER_CUSTOM_COMPONENTS_ID,
    )
    select_dropdown_value(dash_br, value=2, dropdown_id=cnst.CUSTOM_DROPDOWN_ID, multi=False)
    check_graph_is_loading(dash_br, cnst.SCATTER_CUSTOM_COMPONENTS_ID)


def test_range_slider(dash_br):
    page_select(
        dash_br,
        page_path=cnst.CUSTOM_COMPONENTS_PAGE_PATH,
        page_name=cnst.CUSTOM_COMPONENTS_PAGE,
        graph_id=cnst.SCATTER_CUSTOM_COMPONENTS_ID,
    )
    dash_br.multiple_click(slider_value_path(elem_id=cnst.CUSTOM_RANGE_SLIDER_ID, value=4), 1)
    check_graph_is_loading(dash_br, graph_id=cnst.SCATTER_CUSTOM_COMPONENTS_ID)
    check_slider_value(dash_br, elem_id=cnst.CUSTOM_RANGE_SLIDER_ID, expected_start_value="4", expected_end_value="7")
    # check tooltip for the start value
    dash_br.wait_for_text_to_equal(
        f"div[id='{cnst.CUSTOM_RANGE_SLIDER_ID}'] div:nth-of-type(7) .rc-slider-tooltip-inner", "4"
    )
    # check tooltip for the end value
    dash_br.wait_for_text_to_equal(
        f"div[id='{cnst.CUSTOM_RANGE_SLIDER_ID}'] div:nth-of-type(8) .rc-slider-tooltip-inner", "7"
    )
