from e2e.vizro import constants as cnst
from e2e.vizro.checkers import (
    check_graph_is_loaded,
    check_selected_categorical_component,
    check_selected_dropdown,
    check_slider_value,
)
from e2e.vizro.navigation import clear_dropdown, page_select, select_dropdown_value
from e2e.vizro.paths import categorical_components_value_path, dropdown_arrow_path, select_all_path, slider_value_path


def test_sliders_state(dash_br):
    """Verify that sliders values stays the same after page reload."""
    page_select(
        dash_br,
        page_path=cnst.PARAMETERS_PAGE_PATH,
        page_name=cnst.PARAMETERS_PAGE,
    )

    # change slider value to '0.4'
    dash_br.multiple_click(slider_value_path(elem_id=cnst.SLIDER_PARAMETERS, value=3), 1)
    check_graph_is_loaded(dash_br, graph_id=cnst.BAR_GRAPH_ID)
    # change range slider max value to '7'
    dash_br.multiple_click(slider_value_path(elem_id=cnst.RANGE_SLIDER_PARAMETERS, value=4), 1)
    check_graph_is_loaded(dash_br, graph_id=cnst.HISTOGRAM_GRAPH_ID)

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
    select_dropdown_value(dash_br, dropdown_id=cnst.DROPDOWN_PARAMETERS_TWO, value="NONE")
    check_graph_is_loaded(dash_br, graph_id=cnst.BAR_GRAPH_ID)

    # check that specific bar has cerulean blue color
    dash_br.wait_for_element(
        f"div[id='{cnst.BAR_GRAPH_ID}'] g:nth-of-type(3) g:nth-of-type(45) path[style*='(57, 73, 171)'"
    )


def test_checklist_with_two_values(dash_br):
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
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.CHECKLIST_PARAM,
        checklist=True,
        options_value_status=[
            {"value": 1, "selected": True, "value_name": "country"},
            {"value": 2, "selected": False, "value_name": "continent"},
            {"value": 3, "selected": True, "value_name": "year"},
            {"value": 4, "selected": False, "value_name": "lifeExp"},
            {"value": 5, "selected": False, "value_name": "pop"},
            {"value": 6, "selected": False, "value_name": "gdpPercap"},
            {"value": 7, "selected": False, "value_name": "iso_alpha"},
            {"value": 8, "selected": False, "value_name": "iso_num"},
        ],
    )


def test_checklist_select_all_value(dash_br):
    """Checks parametrizing with multiple params by selecting columns for the table."""
    page_select(dash_br, page_path=cnst.PARAMETERS_MULTI_PAGE_PATH, page_name=cnst.PARAMETERS_MULTI_PAGE)
    # unselect 'Select All'
    dash_br.multiple_click(select_all_path(elem_id=cnst.CHECKLIST_PARAM), 1)
    # select 'Select All'
    dash_br.multiple_click(select_all_path(elem_id=cnst.CHECKLIST_PARAM), 1)
    # check if table column 'country' is available
    dash_br.wait_for_element(f"#{cnst.TABLE_CHECKLIST} th[data-dash-column='country']")
    # check if table column 'year' is available and no other column appears on the right
    dash_br.wait_for_element(
        f"#{cnst.TABLE_CHECKLIST} th[data-dash-column='iso_num'][class='dash-header column-7 cell--right-last ']"
    )
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.CHECKLIST_PARAM,
        checklist=True,
        select_all_status=True,
        options_value_status=[
            {"value": 1, "selected": True, "value_name": "country"},
            {"value": 2, "selected": True, "value_name": "continent"},
            {"value": 3, "selected": True, "value_name": "year"},
            {"value": 4, "selected": True, "value_name": "lifeExp"},
            {"value": 5, "selected": True, "value_name": "pop"},
            {"value": 6, "selected": True, "value_name": "gdpPercap"},
            {"value": 7, "selected": True, "value_name": "iso_alpha"},
            {"value": 8, "selected": True, "value_name": "iso_num"},
        ],
    )


def test_dropdown_with_two_values(dash_br):
    """Checks parametrizing with multiple params by selecting columns for the table."""
    page_select(dash_br, page_path=cnst.PARAMETERS_MULTI_PAGE_PATH, page_name=cnst.PARAMETERS_MULTI_PAGE)
    clear_dropdown(dash_br, cnst.DROPDOWN_PARAM_MULTI)
    # select 'pop' parameter
    select_dropdown_value(dash_br, dropdown_id=cnst.DROPDOWN_PARAM_MULTI, value="pop")
    # select 'gdpPercap' parameter
    select_dropdown_value(dash_br, dropdown_id=cnst.DROPDOWN_PARAM_MULTI, value="gdpPercap")
    # check if table column 'pop' is available
    dash_br.wait_for_element(f"#{cnst.TABLE_DROPDOWN} th[data-dash-column='pop']")
    # check if table column 'iso_num' is available and no other column appears on the right
    dash_br.wait_for_element(
        f"#{cnst.TABLE_DROPDOWN} th[data-dash-column='gdpPercap'][class='dash-header column-1 cell--right-last ']"
    )
    dash_br.multiple_click(dropdown_arrow_path(dropdown_id=cnst.DROPDOWN_PARAM_MULTI), 1)
    check_selected_dropdown(
        dash_br,
        dropdown_id=cnst.DROPDOWN_PARAM_MULTI,
        all_value=False,
        expected_selected_options=["pop", "gdpPercap"],
        expected_unselected_options=["SelectAll", "country", "continent", "year", "lifeExp", "iso_alpha", "iso_num"],
    )


def test_dropdown_select_all_value(dash_br):
    """Checks parametrizing with multiple params by selecting columns for the table."""
    page_select(dash_br, page_path=cnst.PARAMETERS_MULTI_PAGE_PATH, page_name=cnst.PARAMETERS_MULTI_PAGE)
    dash_br.multiple_click(dropdown_arrow_path(dropdown_id=cnst.DROPDOWN_PARAM_MULTI), 1)
    dash_br.multiple_click(f"#{cnst.DROPDOWN_PARAM_MULTI}_select_all", 1)
    dash_br.multiple_click(dropdown_arrow_path(dropdown_id=cnst.DROPDOWN_PARAM_MULTI), 1, delay=0.1)
    dash_br.multiple_click(f"#{cnst.DROPDOWN_PARAM_MULTI}_select_all", 1)
    # check if table column 'pop' is available
    dash_br.wait_for_element(f"#{cnst.TABLE_DROPDOWN} th[data-dash-column='pop']")
    # check if table column 'iso_num' is available and no other column appears on the right
    dash_br.wait_for_element(
        f"#{cnst.TABLE_DROPDOWN} th[data-dash-column='iso_num'][class='dash-header column-7 cell--right-last ']"
    )
    dash_br.multiple_click(dropdown_arrow_path(dropdown_id=cnst.DROPDOWN_PARAM_MULTI), 1)
    check_selected_dropdown(
        dash_br,
        dropdown_id=cnst.DROPDOWN_PARAM_MULTI,
        all_value=True,
        expected_selected_options=[
            "country",
            "continent",
            "year",
            "lifeExp",
            "pop",
            "gdpPercap",
            "iso_alpha",
            "iso_num",
        ],
        expected_unselected_options=[],
    )
