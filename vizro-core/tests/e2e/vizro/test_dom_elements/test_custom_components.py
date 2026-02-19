import e2e.vizro.constants as cnst
from e2e.vizro.checkers import (
    check_graph_x_axis_value,
    check_graph_y_axis_value,
    check_selected_dropdown,
    check_slider_value,
)
from e2e.vizro.navigation import page_select, select_dropdown_value, select_slider_value


def test_custom_dropdown(dash_br):
    """Testing setting up and filter of the custom dropdown."""
    page_select(
        dash_br,
        page_name=cnst.CUSTOM_COMPONENTS_PAGE,
    )
    # choose 'versicolor' value
    select_dropdown_value(dash_br, dropdown_id=cnst.CUSTOM_DROPDOWN_ID, value="versicolor")
    check_graph_y_axis_value(
        dash_br, graph_id=cnst.SCATTER_CUSTOM_COMPONENTS_ID, axis_value_number="5", axis_value="1.8"
    )
    check_selected_dropdown(
        dash_br,
        dropdown_id=cnst.CUSTOM_DROPDOWN_ID,
        expected_selected_options=["versicolor"],
        multi=False,
    )


def test_custom_range_slider(dash_br):
    """Testing setting up and filter of the custom range slider."""
    page_select(
        dash_br,
        page_name=cnst.CUSTOM_COMPONENTS_PAGE,
    )
    select_slider_value(dash_br, elem_id=cnst.CUSTOM_RANGE_SLIDER_ID, value="5.3")
    check_graph_x_axis_value(dash_br, graph_id=cnst.SCATTER_CUSTOM_COMPONENTS_ID, axis_value_number="1", axis_value="5")
    check_slider_value(dash_br, elem_id=cnst.CUSTOM_RANGE_SLIDER_ID, expected_start_value="5", expected_end_value="7.9")
