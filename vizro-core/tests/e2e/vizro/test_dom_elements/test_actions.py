from e2e.asserts import assert_files_equal
from e2e.vizro import constants as cnst
from e2e.vizro.checkers import (
    check_exported_file_exists,
    check_selected_categorical_component,
    check_selected_dropdown,
)
from e2e.vizro.navigation import (
    accordion_select,
    hover_over_element_by_css_selector_selenium,
    modifier_click,
    page_select,
)
from e2e.vizro.paths import (
    button_id_path,
    categorical_components_value_path,
    dropdown_arrow_path,
    graph_axis_value_path,
    kpi_card_path,
    page_title_path,
    scatter_point_path,
    select_all_path,
    table_ag_grid_cell_path_by_row,
    table_ag_grid_checkbox_path_by_row,
)
from hamcrest import assert_that, equal_to
from selenium.webdriver import Keys


def test_export_data_no_controls(dash_br):
    """Test exporting unfiltered data."""
    page_select(
        dash_br,
        page_path=cnst.EXPORT_PAGE_PATH,
        page_name=cnst.EXPORT_PAGE,
    )

    # download files and compare it with base ones
    dash_br.multiple_click(button_id_path(btn_id=cnst.EXPORT_PAGE_BUTTON), 1)
    check_exported_file_exists(f"{dash_br.download_path}/{cnst.UNFILTERED_CSV}")
    check_exported_file_exists(f"{dash_br.download_path}/{cnst.UNFILTERED_XLSX}")
    assert_files_equal(cnst.UNFILTERED_BASE_CSV, f"{dash_br.download_path}/{cnst.UNFILTERED_CSV}")


def test_export_filtered_data(dash_br):
    """Test exporting filtered data. It is prefiltered in dashboard config."""
    page_select(
        dash_br,
        page_path=cnst.FILTERS_PAGE_PATH,
        page_name=cnst.FILTERS_PAGE,
    )

    # download files and compare it with base ones
    dash_br.multiple_click(button_id_path(btn_id=cnst.FILTERS_PAGE_EXPORT_DATA_BUTTON), 1)
    check_exported_file_exists(f"{dash_br.download_path}/{cnst.FILTERED_CSV}")
    check_exported_file_exists(f"{dash_br.download_path}/{cnst.FILTERED_XLSX}")
    assert_files_equal(cnst.FILTERED_BASE_CSV, f"{dash_br.download_path}/{cnst.FILTERED_CSV}")


def test_scatter_click_data_custom_action(dash_br):
    """Test custom action for changing data in card by interacting with graph."""
    page_select(
        dash_br,
        page_name=cnst.FILTER_INTERACTIONS_PAGE,
    )

    # click on the dot in the scatter graph and check card text values
    dash_br.click_at_coord_fractions(f"#{cnst.SCATTER_INTERACTIONS_ID} path:nth-of-type(20)", 0, 0)
    dash_br.wait_for_text_to_equal(f"#{cnst.CARD_INTERACTIONS_ID} p", "Scatter chart clicked data:")
    dash_br.wait_for_text_to_equal(f"#{cnst.CARD_INTERACTIONS_ID} h3", 'Species: "setosa"')


def test_actions_progress_indicator(dash_br):
    """Test that progress indicator appears during action run."""
    page_select(
        dash_br,
        page_name=cnst.FILTER_INTERACTIONS_PAGE,
    )

    # click on the dot in the scatter graph
    dash_br.click_at_coord_fractions(f"#{cnst.SCATTER_INTERACTIONS_ID} path:nth-of-type(20)", 0, 0)

    # check that that progress indicator appears
    dash_br.wait_for_text_to_equal("span[class='material-symbols-outlined progress-indicator']", "progress_activity")


def test_set_control_cross_filter_graph(dash_br):
    """Test cross filter between two graphs."""
    accordion_select(dash_br, accordion_name=cnst.ACTIONS_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.SET_CONTROL_GRAPH_CROSS_FILTER_PAGE,
    )

    # click on the 'versicolor' data in scatter graph and check result for box graph
    dash_br.click_at_coord_fractions(
        scatter_point_path(cnst.SCATTER_SET_CONTROL_CROSS_FILTER_ID, point_number=20), 0, 0
    )

    # Check y axis max value is '1.8'
    dash_br.wait_for_text_to_equal(
        graph_axis_value_path(graph_id=cnst.BOX_SET_CONTROL_CROSS_FILTER_ID, axis_value_number="5", axis_value="1.8"),
        "1.8",
    )

    # open dropdown and check values
    dash_br.multiple_click(dropdown_arrow_path(dropdown_id=cnst.DROPDOWN_SET_CONTROL_CROSS_FILTER), 1)
    check_selected_dropdown(
        dash_br,
        dropdown_id=cnst.DROPDOWN_SET_CONTROL_CROSS_FILTER,
        all_value=False,
        expected_selected_options=["versicolor"],
        expected_unselected_options=["SelectAll", "setosa", "virginica"],
    )


def test_set_control_cross_filter_ag_grid(dash_br):
    """Test cross filter between ag_grid and line graph."""
    accordion_select(dash_br, accordion_name=cnst.ACTIONS_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.SET_CONTROL_TABLE_AG_GRID_CROSS_FILTER_PAGE,
    )

    # check if column 'country' is available
    dash_br.wait_for_element(
        table_ag_grid_cell_path_by_row(cnst.SET_CONTROL_TABLE_AG_GRID_CROSS_FILTER_ID, row_index=0, col_id="country")
    )

    # click on Albania country
    dash_br.multiple_click(
        table_ag_grid_cell_path_by_row(cnst.SET_CONTROL_TABLE_AG_GRID_CROSS_FILTER_ID, row_index=1, col_id="country"), 1
    )

    # Check y axis max value is '50k'
    dash_br.wait_for_text_to_equal(
        graph_axis_value_path(
            graph_id=cnst.SET_CONTROL_LINE_AG_GRID_CROSS_FILTER_ID, axis_value_number="6", axis_value="50k"
        ),
        "50k",
    )


def test_set_control_filter_kpi_card(dash_br):
    """Test filter by clicking kpi_card."""
    page_select(dash_br, page_name=cnst.KPI_INDICATORS_PAGE)

    # click kpi_card_reference figure sets the dropdown value to "C"
    dash_br.multiple_click(f"#{cnst.CLICKABLE_KPI_CARD_REFERENCE_ID}", 1, delay=0.1)

    # check dropdown filter value
    dash_br.multiple_click(dropdown_arrow_path(dropdown_id=cnst.DROPDOWN_FILTER_KPI_PAGE), 1)
    check_selected_dropdown(
        dash_br,
        dropdown_id=cnst.DROPDOWN_FILTER_KPI_PAGE,
        all_value=False,
        expected_selected_options=["C"],
        expected_unselected_options=["A", "B", "C"],
    )

    # check kpi_card values
    values = dash_br.find_elements(kpi_card_path())
    values_text = [value.text for value in values]
    assert_that(
        actual_or_assertion=values_text,
        matcher=equal_to(
            [
                "34",
                "34.0",
                "34.0",
                "53",
                "34",
                "34.0",
                "$34.00",
                "34€",
                "34.0",
                "34",
                "53",
            ]
        ),
    )

    # click kpi_card figure sets the dropdown value to "B"
    dash_br.multiple_click(f"#{cnst.CLICKABLE_KPI_CARD_ID}", 1, delay=0.1)

    # check dropdown filter value
    dash_br.multiple_click(dropdown_arrow_path(dropdown_id=cnst.DROPDOWN_FILTER_KPI_PAGE), 1)
    check_selected_dropdown(
        dash_br,
        dropdown_id=cnst.DROPDOWN_FILTER_KPI_PAGE,
        all_value=False,
        expected_selected_options=["B"],
        expected_unselected_options=["A", "B", "C"],
    )

    # check kpi_card values
    values = dash_br.find_elements(kpi_card_path())
    values_text = [value.text for value in values]
    assert_that(
        actual_or_assertion=values_text,
        matcher=equal_to(
            [
                "6434",
                "6434.0",
                "6434.0",
                "6553",
                "6434",
                "6434.0",
                "$6434.00",
                "6434€",
                "6434.0",
                "6434",
                "6553",
            ]
        ),
    )


def test_set_control_filter_button(dash_br):
    """Test filter by clicking button."""
    page_select(dash_br, page_name=cnst.FILTERS_PAGE, page_path=cnst.FILTERS_PAGE_PATH)

    # click filter button sets the radioitems value to "versicolor"
    dash_br.multiple_click(button_id_path(btn_id=cnst.FILTERS_PAGE_SET_CONTROL_FILTER_BUTTON), 1, delay=0.1)

    # check radio button filter value
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.RADIO_ITEMS_FILTER_FILTERS_PAGE,
        options_value_status=[
            {"value": 1, "selected": False, "value_name": "setosa"},
            {"value": 2, "selected": True, "value_name": "versicolor"},
            {"value": 3, "selected": False, "value_name": "virginica"},
        ],
    )

    # check y axis for box graph has max value is '1.8'
    dash_br.wait_for_text_to_equal(
        graph_axis_value_path(graph_id=cnst.BOX_GRAPH_ID, axis_value_number="5", axis_value="1.8"),
        "1.8",
    )


def test_set_control_filter_card(dash_br):
    """Test filter by clicking card."""
    accordion_select(dash_br, accordion_name=cnst.ACTIONS_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.SET_CONTROL_CARD_GRAPH_CROSS_FILTER_PAGE,
    )

    # click filter card sets the radioitems value to "Oceania"
    dash_br.multiple_click(f"#{cnst.SET_CONTROL_CARD_GRAPH_CROSS_FILTER_CARD_ID}", 1, delay=0.1)

    # check radio button filter value
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.SET_CONTROL_CARD_GRAPH_CROSS_FILTER_CONTOL_ID,
        options_value_status=[
            {"value": 1, "selected": False, "value_name": "Africa"},
            {"value": 2, "selected": False, "value_name": "Americas"},
            {"value": 3, "selected": False, "value_name": "Asia"},
            {"value": 4, "selected": False, "value_name": "Europe"},
            {"value": 5, "selected": True, "value_name": "Oceania"},
        ],
    )

    # check that graph data changed to "Oceania"
    dash_br.wait_for_text_to_equal("text[class='legendtext'][data-unformatted='Oceania']", "Oceania")


def test_drill_through_filter_graph(dash_br):
    accordion_select(dash_br, accordion_name=cnst.ACTIONS_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.SET_CONTROL_DRILL_THROUGH_FILTER_GRAPH_SOURCE,
    )

    # click on the 'versicolor' data in scatter graph
    dash_br.click_at_coord_fractions(
        scatter_point_path(cnst.SCATTER_DRILL_THROUGH_FILTER_GRAPH_SOURCE_ID, point_number=20), 0, 0
    )

    # check that new page is opened
    dash_br.wait_for_text_to_equal(page_title_path(), cnst.SET_CONTROL_DRILL_THROUGH_FILTER_GRAPH_TARGET)

    # check that appropriate filter selected on the new page
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.CHECKLIST_DRILL_THROUGH_FILTER_GRAPH_ID,
        options_value_status=[
            {"value": 1, "selected": False, "value_name": "setosa"},
            {"value": 2, "selected": True, "value_name": "versicolor"},
            {"value": 3, "selected": False, "value_name": "virginica"},
        ],
    )

    # Check y axis max value is '7'
    dash_br.wait_for_text_to_equal(
        graph_axis_value_path(
            graph_id=cnst.SCATTER_DRILL_THROUGH_FILTER_GRAPH_TARGET_ID, axis_value_number="5", axis_value="7"
        ),
        "7",
    )


def test_drill_through_parameter_graph(dash_br):
    accordion_select(dash_br, accordion_name=cnst.ACTIONS_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.SET_CONTROL_DRILL_THROUGH_PARAMETER_GRAPH_SOURCE,
    )

    # click on the 'versicolor' data in scatter graph
    dash_br.click_at_coord_fractions(
        scatter_point_path(cnst.SCATTER_DRILL_THROUGH_PARAMETER_GRAPH_SOURCE_ID, point_number=20), 0, 0
    )

    # check that new page is opened
    dash_br.wait_for_text_to_equal(page_title_path(), cnst.SET_CONTROL_DRILL_THROUGH_PARAMETER_GRAPH_TARGET)

    # check that appropriate parameter selected on the new page
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.RADIOITEMS_DRILL_THROUGH_PARAMETER_GRAPH_ID,
        checklist=False,
        options_value_status=[
            {"value": 1, "selected": False, "value_name": "setosa"},
            {"value": 2, "selected": True, "value_name": "versicolor"},
            {"value": 3, "selected": False, "value_name": "virginica"},
        ],
    )

    # check that graph title changed to 'versicolor'
    dash_br.wait_for_text_to_equal(".gtitle", "versicolor")


def test_drill_through_filter_ag_grid(dash_br):
    accordion_select(dash_br, accordion_name=cnst.ACTIONS_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.SET_CONTROL_DRILL_THROUGH_FILTER_AG_GRID_SOURCE,
    )

    # check if column 'Sepal_length' is available
    dash_br.wait_for_element(
        table_ag_grid_cell_path_by_row(cnst.AG_GRID_DRILL_THROUGH_FILTER_AG_GRID_ID, row_index=0, col_id="sepal_length")
    )

    # click on the 'versicolor' data in ag_grid
    dash_br.multiple_click(
        table_ag_grid_cell_path_by_row(cnst.AG_GRID_DRILL_THROUGH_FILTER_AG_GRID_ID, row_index=1, col_id="species"), 1
    )

    # check that new page is opened
    dash_br.wait_for_text_to_equal(page_title_path(), cnst.SET_CONTROL_DRILL_THROUGH_FILTER_AG_GRID_TARGET)

    # check that appropriate filter selected on the new page
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.RADIOITEMS_DRILL_THROUGH_FILTER_AG_GRID_ID,
        checklist=False,
        options_value_status=[
            {"value": 1, "selected": False, "value_name": "setosa"},
            {"value": 2, "selected": True, "value_name": "versicolor"},
            {"value": 3, "selected": False, "value_name": "virginica"},
        ],
    )

    # Check y axis max value is '7'
    dash_br.wait_for_text_to_equal(
        graph_axis_value_path(
            graph_id=cnst.SCATTER_SECOND_DRILL_THROUGH_FILTER_AG_GRID_TARGET_ID, axis_value_number="5", axis_value="7"
        ),
        "7",
    )


def test_drill_down_graph(dash_br):
    accordion_select(dash_br, accordion_name=cnst.ACTIONS_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.SET_CONTROL_DRILL_DOWN_GRAPH_PAGE,
    )

    # click on the 'versicolor' data in scatter graph
    dash_br.click_at_coord_fractions(scatter_point_path(cnst.SCATTER_DRILL_DOWN_GRAPH_ID, point_number=20), 0, 0)

    # Check y axis max value is '7'
    dash_br.wait_for_text_to_equal(
        graph_axis_value_path(graph_id=cnst.SCATTER_DRILL_DOWN_GRAPH_ID, axis_value_number="5", axis_value="7"),
        "7",
    )

    # check that graph title changed to 'versicolor'
    dash_br.wait_for_text_to_equal(".gtitle", "Graph shows `['versicolor']` species.")


def test_action_properties_shortcut_title_description_header_footer(dash_br):
    accordion_select(dash_br, accordion_name=cnst.ACTIONS_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.ACTION_MODEL_FIELD_SHORTCUT_PAGE,
    )

    # click button which is changing title, description, header and footer for the graph and ag_grid
    dash_br.multiple_click(button_id_path(btn_id=cnst.ACTION_MODEL_FIELD_BUTTON_ID), 1)

    # check that title for the graph and ag_grid were changed
    dash_br.wait_for_text_to_equal(
        f"#{cnst.ACTION_MODEL_FIELD_SHORTCUT_GRAPH_ID}_title", cnst.ACTION_MODEL_FIELD_BUTTON_CLICKED_FIGURE_TEXT
    )
    dash_br.wait_for_text_to_equal(
        f"#{cnst.ACTION_MODEL_FIELD_SHORTCUT_AG_GRID_ID}_title", cnst.ACTION_MODEL_FIELD_BUTTON_CLICKED_FIGURE_TEXT
    )

    # check that header for the graph and ag_grid were changed
    dash_br.wait_for_text_to_equal(
        f"#{cnst.ACTION_MODEL_FIELD_SHORTCUT_GRAPH_ID}_header p", cnst.ACTION_MODEL_FIELD_BUTTON_CLICKED_FIGURE_TEXT
    )
    dash_br.wait_for_text_to_equal(
        f"#{cnst.ACTION_MODEL_FIELD_SHORTCUT_AG_GRID_ID}_header p", cnst.ACTION_MODEL_FIELD_BUTTON_CLICKED_FIGURE_TEXT
    )

    # check that footer for the graph and ag_grid were changed
    dash_br.wait_for_text_to_equal(
        f"#{cnst.ACTION_MODEL_FIELD_SHORTCUT_GRAPH_ID}_footer p", cnst.ACTION_MODEL_FIELD_BUTTON_CLICKED_FIGURE_TEXT
    )
    dash_br.wait_for_text_to_equal(
        f"#{cnst.ACTION_MODEL_FIELD_SHORTCUT_AG_GRID_ID}_footer p", cnst.ACTION_MODEL_FIELD_BUTTON_CLICKED_FIGURE_TEXT
    )

    # check that description for the graph and ag_grid were changed
    # hover over info icon and wait for the tooltip appear for graph
    hover_over_element_by_css_selector_selenium(dash_br, f"#{cnst.ACTION_MODEL_FIELD_SHORTCUT_GRAPH_ID}_title + span")
    dash_br.wait_for_text_to_equal(".tooltip-inner p", cnst.ACTION_MODEL_FIELD_BUTTON_CLICKED_FIGURE_TEXT)

    # hover over info icon and wait for the tooltip appear for ag_grid
    hover_over_element_by_css_selector_selenium(dash_br, f"#{cnst.ACTION_MODEL_FIELD_SHORTCUT_AG_GRID_ID}_title + span")
    dash_br.wait_for_text_to_equal(".tooltip-inner p", cnst.ACTION_MODEL_FIELD_BUTTON_CLICKED_FIGURE_TEXT)


def test_ag_grid_underlying_id_shortcuts(dash_br):
    accordion_select(dash_br, accordion_name=cnst.ACTIONS_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.ACTION_AG_GRID_UNDERLYING_ID_SHORTCUT_PAGE,
    )

    # check if column 'Sepal_length' is available in ag-grid
    dash_br.wait_for_element(
        table_ag_grid_cell_path_by_row(
            cnst.ACTION_AG_GRID_UNDERLYING_ID_SHORTCUT_AG_GRID_ID, row_index=0, col_id="sepal_length"
        )
    )

    # click on 'Sepal_length = 4.9' ag-grid cell
    dash_br.multiple_click(
        table_ag_grid_cell_path_by_row(
            cnst.ACTION_AG_GRID_UNDERLYING_ID_SHORTCUT_AG_GRID_ID, row_index=1, col_id="sepal_length"
        ),
        1,
    )

    # check value in Card
    dash_br.wait_for_text_to_equal(
        f"#{cnst.ACTION_AG_GRID_UNDERLYING_ID_SHORTCUT_CARD_ID} a",
        "{'sepal_length': 4.9, 'sepal_width': 3, 'petal_length': 1.4, 'petal_width': 0.2, "
        "'species': 'setosa', 'species_id': 1, 'date_column': '2024-01-02', 'number_column': 1, 'is_setosa': True}",
    )


def test_default_property_controls(dash_br):
    accordion_select(dash_br, accordion_name=cnst.ACTIONS_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.ACTION_CONTROL_SHORTCUT_PAGE,
    )

    # choose 'petal_length' for filter
    dash_br.multiple_click(
        categorical_components_value_path(elem_id=cnst.ACTION_CONTROL_SHORTCUT_FILTER_ID, value=2), 1, delay=0.1
    )

    # check that 'petal_length' was chosen for parameter
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.ACTION_CONTROL_SHORTCUT_PARAMETER_ID,
        options_value_status=[
            {"value": 1, "selected": False, "value_name": "sepal_length"},
            {"value": 2, "selected": True, "value_name": "petal_length"},
        ],
    )

    # check that graph 'x' axis changed to 'petal_length'
    dash_br.wait_for_element('text[class="xtitle"][data-unformatted="petal_length"]')


def test_set_control_clickmode_event_select(dash_br):
    """Test cross filter between two graphs with multi select."""
    accordion_select(dash_br, accordion_name=cnst.ACTIONS_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.SET_CONTROL_MULTI_SELECT_PAGE,
    )

    # select virginica - this causes both: checklist and radioitems to be set
    dash_br.click_at_coord_fractions(scatter_point_path(cnst.SCATTER_SET_CONTROL_EVENT_SELECT, point_number=21), 0, 0)

    # select versicolor with SHIFT key - this causes only checklist to be set and radioitems
    # stays unchanged as multiple values are selected and radioItems is single-select control
    modifier_click(
        dash_br, selector=scatter_point_path(cnst.SCATTER_SET_CONTROL_EVENT_SELECT, point_number=22), key=Keys.SHIFT
    )

    # Check filters target graph is correct - y axis max value is '2.4'
    dash_br.wait_for_text_to_equal(
        graph_axis_value_path(
            graph_id=cnst.BOX_SET_CONTROL_TARGET_MULTI_SELECT, axis_value_number="6", axis_value="2.4"
        ),
        "2.4",
    )

    # check selected values in checklist and radioitems
    check_selected_categorical_component(
        dash_br,
        checklist=True,
        component_id=cnst.CHECKLIST_SET_CONTROL_MULTI_SELECT_FILTER,
        options_value_status=[
            {"value": 1, "selected": False, "value_name": "setosa"},
            {"value": 2, "selected": True, "value_name": "versicolor"},
            {"value": 3, "selected": True, "value_name": "virginica"},
        ],
    )
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.RADIOITEMS_SET_CONTROL_MULTI_SELECT_FILTER,
        options_value_status=[
            {"value": 1, "selected": False, "value_name": "setosa"},
            {"value": 2, "selected": False, "value_name": "versicolor"},
            {"value": 3, "selected": True, "value_name": "virginica"},
        ],
    )

    # unselect all values - this causes target control values to reset
    dash_br.click_at_coord_fractions(scatter_point_path(cnst.SCATTER_SET_CONTROL_EVENT_SELECT, point_number=21), 0, 0)
    dash_br.click_at_coord_fractions(scatter_point_path(cnst.SCATTER_SET_CONTROL_EVENT_SELECT, point_number=21), 0, 0)

    # check all values are selected for checklist and setosa is selected for radioitems
    check_selected_categorical_component(
        dash_br,
        checklist=True,
        select_all_status=True,
        component_id=cnst.CHECKLIST_SET_CONTROL_MULTI_SELECT_FILTER,
        options_value_status=[
            {"value": 1, "selected": True, "value_name": "setosa"},
            {"value": 2, "selected": True, "value_name": "versicolor"},
            {"value": 3, "selected": True, "value_name": "virginica"},
        ],
    )
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.RADIOITEMS_SET_CONTROL_MULTI_SELECT_FILTER,
        options_value_status=[
            {"value": 1, "selected": True, "value_name": "setosa"},
            {"value": 2, "selected": False, "value_name": "versicolor"},
            {"value": 3, "selected": False, "value_name": "virginica"},
        ],
    )


def test_set_control_clickmode_event(dash_br):
    """Test cross filter between two graphs without multi select."""
    accordion_select(dash_br, accordion_name=cnst.ACTIONS_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.SET_CONTROL_MULTI_SELECT_PAGE,
    )

    # select virginica - this causes both: checklist and radioitems to be set
    dash_br.click_at_coord_fractions(scatter_point_path(cnst.SCATTER_SET_CONTROL_EVENT, point_number=21), 0, 0)

    # Check target graph is correct - y axis max value is '2.4'
    dash_br.wait_for_text_to_equal(
        graph_axis_value_path(
            graph_id=cnst.BOX_SET_CONTROL_TARGET_MULTI_SELECT, axis_value_number="6", axis_value="2.4"
        ),
        "2.4",
    )

    # check selected values in checklist and radioitems
    check_selected_categorical_component(
        dash_br,
        checklist=True,
        component_id=cnst.CHECKLIST_SET_CONTROL_MULTI_SELECT_FILTER,
        options_value_status=[
            {"value": 1, "selected": False, "value_name": "setosa"},
            {"value": 2, "selected": False, "value_name": "versicolor"},
            {"value": 3, "selected": True, "value_name": "virginica"},
        ],
    )
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.RADIOITEMS_SET_CONTROL_MULTI_SELECT_FILTER,
        options_value_status=[
            {"value": 1, "selected": False, "value_name": "setosa"},
            {"value": 2, "selected": False, "value_name": "versicolor"},
            {"value": 3, "selected": True, "value_name": "virginica"},
        ],
    )

    # select versicolor with SHIFT key - this causes that only versicolor is selected as source graph
    # has clickmode="event"
    modifier_click(
        dash_br, selector=scatter_point_path(cnst.SCATTER_SET_CONTROL_EVENT, point_number=22), key=Keys.SHIFT
    )

    # check that only versicolor is selected in checklist and radioitems
    check_selected_categorical_component(
        dash_br,
        checklist=True,
        component_id=cnst.CHECKLIST_SET_CONTROL_MULTI_SELECT_FILTER,
        options_value_status=[
            {"value": 1, "selected": False, "value_name": "setosa"},
            {"value": 2, "selected": True, "value_name": "versicolor"},
            {"value": 3, "selected": False, "value_name": "virginica"},
        ],
    )
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.RADIOITEMS_SET_CONTROL_MULTI_SELECT_FILTER,
        options_value_status=[
            {"value": 1, "selected": False, "value_name": "setosa"},
            {"value": 2, "selected": True, "value_name": "versicolor"},
            {"value": 3, "selected": False, "value_name": "virginica"},
        ],
    )


def test_set_control_clickmode_aggrid_checkbox_click(dash_br):
    """Test cross filter between AgGrid and graph with checkbox multi select."""
    accordion_select(dash_br, accordion_name=cnst.ACTIONS_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.SET_CONTROL_MULTI_SELECT_PAGE,
    )

    # select virginica and versicolor in ag_grid with checkbox click
    dash_br.multiple_click(table_ag_grid_checkbox_path_by_row(cnst.TABLE_SET_CONTROL_MULTI_SELECT, row_index=2), 1)
    dash_br.multiple_click(table_ag_grid_checkbox_path_by_row(cnst.TABLE_SET_CONTROL_MULTI_SELECT, row_index=1), 1)

    # check selected values in checklist and radioitems
    check_selected_categorical_component(
        dash_br,
        checklist=True,
        component_id=cnst.CHECKLIST_SET_CONTROL_MULTI_SELECT_FILTER,
        options_value_status=[
            {"value": 1, "selected": False, "value_name": "setosa"},
            {"value": 2, "selected": True, "value_name": "versicolor"},
            {"value": 3, "selected": True, "value_name": "virginica"},
        ],
    )
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.RADIOITEMS_SET_CONTROL_MULTI_SELECT_FILTER,
        options_value_status=[
            {"value": 1, "selected": False, "value_name": "setosa"},
            {"value": 2, "selected": False, "value_name": "versicolor"},
            {"value": 3, "selected": True, "value_name": "virginica"},
        ],
    )

    # unselect virginica in ag_grid with checkbox click
    dash_br.multiple_click(table_ag_grid_checkbox_path_by_row(cnst.TABLE_SET_CONTROL_MULTI_SELECT, row_index=2), 1)

    # check selected values in checklist and radioitems
    check_selected_categorical_component(
        dash_br,
        checklist=True,
        component_id=cnst.CHECKLIST_SET_CONTROL_MULTI_SELECT_FILTER,
        options_value_status=[
            {"value": 1, "selected": False, "value_name": "setosa"},
            {"value": 2, "selected": True, "value_name": "versicolor"},
            {"value": 3, "selected": False, "value_name": "virginica"},
        ],
    )
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.RADIOITEMS_SET_CONTROL_MULTI_SELECT_FILTER,
        options_value_status=[
            {"value": 1, "selected": False, "value_name": "setosa"},
            {"value": 2, "selected": True, "value_name": "versicolor"},
            {"value": 3, "selected": False, "value_name": "virginica"},
        ],
    )

    # unselect all rows in ag_grid with checkbox click
    dash_br.multiple_click(table_ag_grid_checkbox_path_by_row(cnst.TABLE_SET_CONTROL_MULTI_SELECT, row_index=1), 1)

    # check all values are selected for checklist and setosa is selected for radioitems
    check_selected_categorical_component(
        dash_br,
        checklist=True,
        select_all_status=True,
        component_id=cnst.CHECKLIST_SET_CONTROL_MULTI_SELECT_FILTER,
        options_value_status=[
            {"value": 1, "selected": True, "value_name": "setosa"},
            {"value": 2, "selected": True, "value_name": "versicolor"},
            {"value": 3, "selected": True, "value_name": "virginica"},
        ],
    )
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.RADIOITEMS_SET_CONTROL_MULTI_SELECT_FILTER,
        options_value_status=[
            {"value": 1, "selected": True, "value_name": "setosa"},
            {"value": 2, "selected": False, "value_name": "versicolor"},
            {"value": 3, "selected": False, "value_name": "virginica"},
        ],
    )


def test_set_control_clickmode_aggrid_command_and_shift_click(dash_br):
    """Test cross filter between AgGrid and graph with command and shift multi select."""
    accordion_select(dash_br, accordion_name=cnst.ACTIONS_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.SET_CONTROL_MULTI_SELECT_PAGE,
    )

    # select virginica by clicking on cell
    dash_br.multiple_click(
        table_ag_grid_cell_path_by_row(cnst.TABLE_SET_CONTROL_MULTI_SELECT, row_index=2, col_id="sepal_length"), 1
    )
    # select versicolor with SHIFT key
    modifier_click(
        dash_br,
        selector=table_ag_grid_cell_path_by_row(
            cnst.TABLE_SET_CONTROL_MULTI_SELECT, row_index=1, col_id="sepal_length"
        ),
        key=Keys.SHIFT,
    )

    # check selected values in checklist and radioitems
    check_selected_categorical_component(
        dash_br,
        checklist=True,
        component_id=cnst.CHECKLIST_SET_CONTROL_MULTI_SELECT_FILTER,
        options_value_status=[
            {"value": 1, "selected": False, "value_name": "setosa"},
            {"value": 2, "selected": True, "value_name": "versicolor"},
            {"value": 3, "selected": True, "value_name": "virginica"},
        ],
    )
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.RADIOITEMS_SET_CONTROL_MULTI_SELECT_FILTER,
        options_value_status=[
            {"value": 1, "selected": False, "value_name": "setosa"},
            {"value": 2, "selected": False, "value_name": "versicolor"},
            {"value": 3, "selected": True, "value_name": "virginica"},
        ],
    )

    # unselect virginica with COMMAND key
    modifier_click(
        dash_br,
        selector=table_ag_grid_cell_path_by_row(
            cnst.TABLE_SET_CONTROL_MULTI_SELECT, row_index=2, col_id="sepal_length"
        ),
        key=Keys.COMMAND,
    )

    # check selected values in checklist and radioitems
    check_selected_categorical_component(
        dash_br,
        checklist=True,
        component_id=cnst.CHECKLIST_SET_CONTROL_MULTI_SELECT_FILTER,
        options_value_status=[
            {"value": 1, "selected": False, "value_name": "setosa"},
            {"value": 2, "selected": True, "value_name": "versicolor"},
            {"value": 3, "selected": False, "value_name": "virginica"},
        ],
    )
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.RADIOITEMS_SET_CONTROL_MULTI_SELECT_FILTER,
        options_value_status=[
            {"value": 1, "selected": False, "value_name": "setosa"},
            {"value": 2, "selected": True, "value_name": "versicolor"},
            {"value": 3, "selected": False, "value_name": "virginica"},
        ],
    )

    # unselect versicolor with COMMAND key
    modifier_click(
        dash_br,
        selector=table_ag_grid_cell_path_by_row(
            cnst.TABLE_SET_CONTROL_MULTI_SELECT, row_index=1, col_id="sepal_length"
        ),
        key=Keys.COMMAND,
    )

    # check all values are selected for checklist and setosa is selected for radioitems
    check_selected_categorical_component(
        dash_br,
        checklist=True,
        select_all_status=True,
        component_id=cnst.CHECKLIST_SET_CONTROL_MULTI_SELECT_FILTER,
        options_value_status=[
            {"value": 1, "selected": True, "value_name": "setosa"},
            {"value": 2, "selected": True, "value_name": "versicolor"},
            {"value": 3, "selected": True, "value_name": "virginica"},
        ],
    )
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.RADIOITEMS_SET_CONTROL_MULTI_SELECT_FILTER,
        options_value_status=[
            {"value": 1, "selected": True, "value_name": "setosa"},
            {"value": 2, "selected": False, "value_name": "versicolor"},
            {"value": 3, "selected": False, "value_name": "virginica"},
        ],
    )


def test_set_control_button_card_variants(dash_br):
    """Test set_control action from button and card with different variants."""
    accordion_select(dash_br, accordion_name=cnst.ACTIONS_ACCORDION)
    page_select(dash_br, page_name=cnst.SET_CONTROL_BUTTON_CARD)

    # set_control card single value
    # Click the card to set virginica value to filters
    dash_br.multiple_click(f"#{cnst.SET_CONTROL_CARD_SINGLE_VALUE}", 1)

    # Check checklist and radioitems values
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.CHECKLIST_SET_CONTROL_BUTTON_CARD,
        checklist=True,
        options_value_status=[
            {"value": 1, "selected": False, "value_name": "setosa"},
            {"value": 2, "selected": False, "value_name": "versicolor"},
            {"value": 3, "selected": True, "value_name": "virginica"},
        ],
    )

    check_selected_categorical_component(
        dash_br,
        component_id=cnst.RADIOITEMS_SET_CONTROL_BUTTON_CARD,
        options_value_status=[
            {"value": 1, "selected": False, "value_name": "setosa"},
            {"value": 2, "selected": False, "value_name": "versicolor"},
            {"value": 3, "selected": True, "value_name": "virginica"},
        ],
    )

    # set_control card multi value
    # Click the card to set versicolor and virginica value to filters
    dash_br.multiple_click(f"#{cnst.SET_CONTROL_CARD_MULTI_VALUE}", 1)

    # Check checklist and radioitems values
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.CHECKLIST_SET_CONTROL_BUTTON_CARD,
        checklist=True,
        options_value_status=[
            {"value": 1, "selected": False, "value_name": "setosa"},
            {"value": 2, "selected": True, "value_name": "versicolor"},
            {"value": 3, "selected": True, "value_name": "virginica"},
        ],
    )

    check_selected_categorical_component(
        dash_br,
        component_id=cnst.RADIOITEMS_SET_CONTROL_BUTTON_CARD,
        options_value_status=[
            {"value": 1, "selected": False, "value_name": "setosa"},
            {"value": 2, "selected": False, "value_name": "versicolor"},
            {"value": 3, "selected": True, "value_name": "virginica"},
        ],
    )

    # set_control button empty list
    # Click the button to set [] value to filters
    dash_br.multiple_click(button_id_path(btn_id=cnst.SET_CONTROL_BUTTON_EMPTY_LIST), 1)

    # Check checklist and radioitems values
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.CHECKLIST_SET_CONTROL_BUTTON_CARD,
        checklist=True,
        options_value_status=[
            {"value": 1, "selected": False, "value_name": "setosa"},
            {"value": 2, "selected": False, "value_name": "versicolor"},
            {"value": 3, "selected": False, "value_name": "virginica"},
        ],
    )

    check_selected_categorical_component(
        dash_br,
        component_id=cnst.RADIOITEMS_SET_CONTROL_BUTTON_CARD,
        options_value_status=[
            {"value": 1, "selected": False, "value_name": "setosa"},
            {"value": 2, "selected": False, "value_name": "versicolor"},
            {"value": 3, "selected": True, "value_name": "virginica"},
        ],
    )

    # set_control button none
    # Click the button to set none value to filters (reset filters)
    dash_br.multiple_click(button_id_path(btn_id=cnst.SET_CONTROL_BUTTON_NONE), 1)

    # Check checklist and radioitems values
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.CHECKLIST_SET_CONTROL_BUTTON_CARD,
        select_all_status=True,
        checklist=True,
        options_value_status=[
            {"value": 1, "selected": True, "value_name": "setosa"},
            {"value": 2, "selected": True, "value_name": "versicolor"},
            {"value": 3, "selected": True, "value_name": "virginica"},
        ],
    )

    check_selected_categorical_component(
        dash_br,
        component_id=cnst.RADIOITEMS_SET_CONTROL_BUTTON_CARD,
        options_value_status=[
            {"value": 1, "selected": True, "value_name": "setosa"},
            {"value": 2, "selected": False, "value_name": "versicolor"},
            {"value": 3, "selected": False, "value_name": "virginica"},
        ],
    )


def test_filtered_graph_does_not_trigger_set_control(dash_br):
    """Test filtered graph does not trigger the set_control again."""
    accordion_select(dash_br, accordion_name=cnst.ACTIONS_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.FILTERED_GRAPH_AGGRID_TRIGGER_SET_CONTROL_PAGE,
    )

    # select versicolor in scatter graph
    dash_br.click_at_coord_fractions(
        scatter_point_path(cnst.FILTERED_SCATTER_TRIGGER_SET_CONTROL_ID, point_number=21), 0, 0
    )

    # unselect all in checklist that filters a set_control source graph
    dash_br.multiple_click(select_all_path(elem_id=cnst.CHECKLIST_FT_GRAPH_SET_CONTROL), 1, delay=0.5)

    # check selected value in checklist for targeted aggrid did not change
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.CHECKLIST_FILTERED_GRAPH_TARGET_AGGRID_SET_CONTROL,
        checklist=True,
        options_value_status=[
            {"value": 1, "selected": False, "value_name": "setosa"},
            {"value": 2, "selected": True, "value_name": "versicolor"},
            {"value": 3, "selected": False, "value_name": "virginica"},
        ],
    )


def test_filtered_aggrid_does_not_trigger_set_control(dash_br):
    """Test filtered ag_grid does not trigger the set_control again."""
    accordion_select(dash_br, accordion_name=cnst.ACTIONS_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.FILTERED_GRAPH_AGGRID_TRIGGER_SET_CONTROL_PAGE,
    )

    # navigate to AgGrid tab
    dash_br.multiple_click("a[role='tab'][class='nav-link']", 1)

    # select virginica by clicking on cell
    dash_br.multiple_click(
        table_ag_grid_cell_path_by_row(cnst.FILTERED_AGGRID_TRIGGER_SET_CONTROL_ID, row_index=2, col_id="sepal_length"),
        1,
        delay=0.5,
    )

    # unselect all in checklist that filters a set_control source ag_grid
    dash_br.multiple_click(select_all_path(elem_id=cnst.CHECKLIST_FT_AGGRID_SET_CONTROL), 1)

    # check selected value in checklist for targeted aggrid did not change
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.CHECKLIST_FILTERED_GRAPH_TARGET_AGGRID_SET_CONTROL,
        checklist=True,
        options_value_status=[
            {"value": 1, "selected": False, "value_name": "setosa"},
            {"value": 2, "selected": False, "value_name": "versicolor"},
            {"value": 3, "selected": True, "value_name": "virginica"},
        ],
    )


def test_self_filtered_graph(dash_br):
    """Test self filter graph by selecting data in the same graph."""
    accordion_select(dash_br, accordion_name=cnst.ACTIONS_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.SELF_FILTER_SET_CONTROL_PAGE,
    )

    # select virginica in scatter graph
    dash_br.click_at_coord_fractions(scatter_point_path(cnst.SCATTER_SET_CONTROL_SELF_FILTER, point_number=21), 0, 0)

    # Check y axis max value is '2.4'
    dash_br.wait_for_text_to_equal(
        graph_axis_value_path(graph_id=cnst.SCATTER_SET_CONTROL_SELF_FILTER, axis_value_number="6", axis_value="2.4"),
        "2.4",
    )

    # check selected value in checklist
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.CHECKLIST_SET_CONTROL_SELF_FILTER,
        checklist=True,
        options_value_status=[
            {"value": 1, "selected": False, "value_name": "setosa"},
            {"value": 2, "selected": False, "value_name": "versicolor"},
            {"value": 3, "selected": True, "value_name": "virginica"},
        ],
    )

    # select virginica in scatter graph
    dash_br.click_at_coord_fractions(
        scatter_point_path(cnst.SCATTER_SET_CONTROL_SELF_FILTER, point_number=21, trace_index=1), 0, 0
    )
    dash_br.click_at_coord_fractions(
        scatter_point_path(cnst.SCATTER_SET_CONTROL_SELF_FILTER, point_number=21, trace_index=1), 0, 0
    )
    # TODO: find out why three clicks are needed to unselect the point
    dash_br.click_at_coord_fractions(
        scatter_point_path(cnst.SCATTER_SET_CONTROL_SELF_FILTER, point_number=21, trace_index=1), 0, 0
    )

    # check that all values are selected in checklist
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.CHECKLIST_SET_CONTROL_SELF_FILTER,
        checklist=True,
        select_all_status=True,
        options_value_status=[
            {"value": 1, "selected": True, "value_name": "setosa"},
            {"value": 2, "selected": True, "value_name": "versicolor"},
            {"value": 3, "selected": True, "value_name": "virginica"},
        ],
    )
