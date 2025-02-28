import e2e.vizro.constants as cnst
from e2e.vizro.checkers import check_selected_checklist, check_selected_dropdown
from e2e.vizro.navigation import page_select
from e2e.vizro.paths import categorical_components_value_path, dropdown_arrow_path, select_all_path


def test_checklist_select_all_value(dash_br):
    """Checks parametrizing with multiple params by selecting columns for the table."""
    page_select(dash_br, page_path=cnst.PARAMETERS_MULTI_PAGE_PATH, page_name=cnst.PARAMETERS_MULTI_PAGE)
    # unselect 'Select All'
    dash_br.multiple_click(select_all_path(elem_id=cnst.CHECKLIST_PARAM), 1)
    # select 'country' parameter
    dash_br.multiple_click(categorical_components_value_path(elem_id=cnst.CHECKLIST_PARAM, value=1), 1)
    # select 'year' parameter
    dash_br.multiple_click(categorical_components_value_path(elem_id=cnst.CHECKLIST_PARAM, value=3), 1)
    # check if table column 'country' is available
    dash_br.wait_for_element(f"#{cnst.TABLE_CHECKLIST} th[data-dash-column='country']")
    # check if table column 'year' is available and no other column appears on the right
    dash_br.wait_for_element(
        f"#{cnst.TABLE_CHECKLIST} th[data-dash-column='year'][class='dash-header column-1 cell--right-last ']"
    )
    check_selected_checklist(
        dash_br,
        checklist_id=cnst.CHECKLIST_PARAM,
        select_all_status=False,
        options_value_status=[
            {"value": 1, "status": True},
            {"value": 2, "status": False},
            {"value": 3, "status": True},
            {"value": 4, "status": False},
            {"value": 5, "status": False},
            {"value": 6, "status": False},
            {"value": 7, "status": False},
            {"value": 8, "status": False},
        ],
    )


def test_dropdown_select_all_value(dash_br):
    """Checks parametrizing with multiple params by selecting columns for the table."""
    page_select(dash_br, page_path=cnst.PARAMETERS_MULTI_PAGE_PATH, page_name=cnst.PARAMETERS_MULTI_PAGE)
    dash_br.multiple_click(dropdown_arrow_path(), 1)
    # unselect 'Select All'
    dash_br.multiple_click(select_all_path(elem_id=cnst.DROPDOWN_PARAM_MULTI), 1)
    dash_br.multiple_click(dropdown_arrow_path(), 1)
    # select 'pop' parameter
    dash_br.select_dcc_dropdown(f"#{cnst.DROPDOWN_PARAM_MULTI}", "pop")
    # select 'gdpPercap' parameter
    dash_br.select_dcc_dropdown(f"#{cnst.DROPDOWN_PARAM_MULTI}", "gdpPercap")
    # check if table column 'pop' is available
    dash_br.wait_for_element(f"#{cnst.TABLE_DROPDOWN} th[data-dash-column='pop']")
    # check if table column 'gdpPercap' is available and no other column appears on the right
    dash_br.wait_for_element(
        f"#{cnst.TABLE_DROPDOWN} th[data-dash-column='gdpPercap'][class='dash-header column-1 cell--right-last ']"
    )
    dash_br.multiple_click(dropdown_arrow_path(), 1)
    check_selected_dropdown(
        dash_br,
        dropdown_id=cnst.DROPDOWN_PARAM_MULTI,
        all_value=False,
        expected_selected_options=["pop", "gdpPercap"],
        expected_unselected_options=["country", "continent", "year", "lifeExp", "iso_alpha", "iso_num"],
    )
