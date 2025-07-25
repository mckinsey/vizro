import e2e.vizro.constants as cnst
from e2e.vizro.checkers import check_graph_is_loaded
from e2e.vizro.navigation import clear_dropdown, page_select, select_dropdown_value
from e2e.vizro.paths import categorical_components_value_path


def test_filter_and_parameter(dash_br):
    """Testing filter and parameter on the same page."""
    page_select(
        dash_br,
        page_name=cnst.FILTER_AND_PARAM_PAGE,
    )

    # check that title of the graph is 'blue'
    dash_br.wait_for_text_to_equal(".gtitle", "blue")

    # select 'red' value in the radio item parameter selector and the title of the graph
    dash_br.multiple_click(categorical_components_value_path(elem_id=cnst.RADIO_ITEMS_FILTER_AND_PARAM, value=1), 1)
    check_graph_is_loaded(dash_br, graph_id=cnst.BOX_FILTER_AND_PARAM_ID)
    dash_br.wait_for_text_to_equal(".gtitle", "red")

    # select 'setosa' in dropdown filter selector
    clear_dropdown(dash_br, cnst.DROPDOWN_FILTER_AND_PARAM)
    select_dropdown_value(dash_br, dropdown_id=cnst.DROPDOWN_FILTER_AND_PARAM, value="setosa")
    check_graph_is_loaded(dash_br, graph_id=cnst.BOX_FILTER_AND_PARAM_ID)
