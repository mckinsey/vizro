import e2e.vizro.constants as cnst
from e2e.vizro.checkers import check_graph_is_loading, check_selected_dropdown, check_slider_value
from e2e.vizro.navigation import page_select, select_dropdown_value
from e2e.vizro.paths import slider_value_path


def test_custom_dropdown(dash_br):
    """Testing setting up and filter of the custom dropdown."""
    page_select(
        dash_br,
        page_name=cnst.CUSTOM_COMPONENTS_PAGE,
    )
    # choose 'versicolor' value
    select_dropdown_value(dash_br, value=2, dropdown_id=cnst.CUSTOM_DROPDOWN_ID)
    check_graph_is_loading(dash_br, cnst.SCATTER_CUSTOM_COMPONENTS_ID)
    check_selected_dropdown(
        dash_br,
        dropdown_id=cnst.CUSTOM_DROPDOWN_ID,
        expected_selected_options=["versicolor"],
    )


def test_custom_range_slider(dash_br):
    """Testing setting up and filter of the custom range slider."""
    page_select(
        dash_br,
        page_name=cnst.CUSTOM_COMPONENTS_PAGE,
    )
    dash_br.multiple_click(slider_value_path(elem_id=cnst.CUSTOM_RANGE_SLIDER_ID, value=4), 1)
    check_graph_is_loading(dash_br, graph_id=cnst.SCATTER_CUSTOM_COMPONENTS_ID)
    check_slider_value(dash_br, elem_id=cnst.CUSTOM_RANGE_SLIDER_ID, expected_start_value="4", expected_end_value="7")
