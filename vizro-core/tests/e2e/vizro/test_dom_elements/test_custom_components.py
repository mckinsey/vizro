import e2e.vizro.constants as cnst
from e2e.vizro.checkers import check_graph_is_loading
from e2e.vizro.navigation import page_select, select_dropdown_value


def test_dropdown(dash_br):
    page_select(
        dash_br,
        page_path=cnst.CUSTOM_COMPONENTS_PAGE_PATH,
        page_name=cnst.CUSTOM_COMPONENTS_PAGE,
        graph_id=cnst.SCATTER_CUSTOM_COMPONENTS_ID,
    )
    select_dropdown_value(dash_br, value=2, dropdown_id=cnst.CUSTOM_DROPDOWN_ID)
    check_graph_is_loading(dash_br, cnst.SCATTER_CUSTOM_COMPONENTS_ID)
