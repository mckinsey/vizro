import pytest
from e2e.vizro import constants as cnst
from e2e.vizro.checkers import check_graph_is_loading
from e2e.vizro.navigation import page_select, select_dropdown_value
from e2e.vizro.paths import categorical_components_value_path


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_interactions(dash_br):
    page_select(
        dash_br,
        page_path=cnst.FILTER_INTERACTIONS_PAGE_PATH,
        page_name=cnst.FILTER_INTERACTIONS_PAGE,
        graph_id=cnst.SCATTER_INTERACTIONS_ID,
    )

    # click on the 'setosa' data in scatter graph
    dash_br.click_at_coord_fractions(f"#{cnst.SCATTER_INTERACTIONS_ID} path:nth-of-type(20)", 0, 1)
    check_graph_is_loading(dash_br, cnst.BOX_INTERACTIONS_ID)

    # select 'setosa' in fropdown filter
    select_dropdown_value(dash_br, value=2, dropdown_id=cnst.DROPDOWN_INTER_FILTER)
    check_graph_is_loading(dash_br, cnst.BOX_INTERACTIONS_ID)

    # select 'red' title for the box graph
    dash_br.multiple_click(categorical_components_value_path(elem_id=cnst.RADIOITEM_INTER_PARAM, value=1), 1)
    check_graph_is_loading(dash_br, cnst.BOX_INTERACTIONS_ID)
    dash_br.wait_for_text_to_equal(".gtitle", "red")
