import pytest
from e2e.asserts import assert_files_equal
from e2e.vizro import constants as cnst
from e2e.vizro.checkers import (
    check_exported_file_exists,
    check_selected_categorical_component,
    check_selected_dropdown,
)
from e2e.vizro.navigation import accordion_select, page_select
from e2e.vizro.paths import (
    button_id_path,
    dropdown_arrow_path,
    graph_axis_value_path,
    page_title_path,
)


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


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_scatter_click_data_custom_action(dash_br):
    """Test custom action for changing data in card by interacting with graph."""
    page_select(
        dash_br,
        page_name=cnst.FILTER_INTERACTIONS_PAGE,
    )

    # click on the dot in the scatter graph and check card text values
    dash_br.click_at_coord_fractions(f"#{cnst.SCATTER_INTERACTIONS_ID} path:nth-of-type(20)", 0, 1)
    dash_br.wait_for_text_to_equal(f"#{cnst.CARD_INTERACTIONS_ID} p", "Scatter chart clicked data:")
    dash_br.wait_for_text_to_equal(f"#{cnst.CARD_INTERACTIONS_ID} h3", 'Species: "setosa"')


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_actions_progress_indicator(dash_br):
    """Test that progress indicator appears during action run."""
    page_select(
        dash_br,
        page_name=cnst.FILTER_INTERACTIONS_PAGE,
    )

    # click on the dot in the scatter graph
    dash_br.click_at_coord_fractions(f"#{cnst.SCATTER_INTERACTIONS_ID} path:nth-of-type(20)", 0, 1)
    # check that that progress indicator appears
    dash_br.wait_for_text_to_equal("span[class='material-symbols-outlined progress-indicator']", "progress_activity")


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_set_control_filter_interactions_graph(dash_br):
    """Test filter interactions between two graphs."""
    accordion_select(dash_br, accordion_name=cnst.ACTIONS_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.SET_CONTROL_GRAPH_INTERACTIONS_PAGE,
    )

    # click on the 'versicolor' data in scatter graph and check result for box graph
    dash_br.click_at_coord_fractions(
        "#scatter_set_control_inter g[class^='trace']:nth-of-type(2) path:nth-of-type(20)", 0, 1
    )
    # Check y axis max value is '1.8'
    dash_br.wait_for_text_to_equal(
        graph_axis_value_path(graph_id=cnst.BOX_SET_CONTROL_INTERACTIONS_ID, axis_value_number="5", axis_value="1.8"),
        "1.8",
    )

    # open dropdown and check values
    dash_br.multiple_click(dropdown_arrow_path(dropdown_id=cnst.DROPDOWN_SET_CONTROL_INTER_FILTER), 1)
    check_selected_dropdown(
        dash_br,
        dropdown_id=cnst.DROPDOWN_SET_CONTROL_INTER_FILTER,
        all_value=False,
        expected_selected_options=["versicolor"],
        expected_unselected_options=["SelectAll", "setosa", "virginica"],
    )


def test_set_control_filter_interactions_ag_grid(dash_br):
    """Test filter interaction between ag_grid and line graph."""
    accordion_select(dash_br, accordion_name=cnst.ACTIONS_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.SET_CONTROL_TABLE_AG_GRID_INTERACTIONS_PAGE,
    )

    # check if column 'country' is available
    dash_br.wait_for_element(
        f"div[id='{cnst.SET_CONTROL_TABLE_AG_GRID_INTERACTIONS_ID}'] div:nth-of-type(1) div[col-id='country']"
    )

    # click on Albania country
    dash_br.multiple_click(
        f"div[id='{cnst.SET_CONTROL_TABLE_AG_GRID_INTERACTIONS_ID}'] div[class='ag-center-cols-container'] "
        f"div:nth-of-type(2) div[col-id='country']",
        1,
    )
    # Check y axis max value is '50k'
    dash_br.wait_for_text_to_equal(
        graph_axis_value_path(
            graph_id=cnst.SET_CONTROL_LINE_AG_GRID_INTERACTIONS_ID, axis_value_number="6", axis_value="50k"
        ),
        "50k",
    )


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_filter_drill_through(dash_br):
    accordion_select(dash_br, accordion_name=cnst.ACTIONS_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.SET_CONTROL_FILTER_DRILL_THROUGH_SOURCE,
    )
    # click on the 'versicolor' data in scatter graph
    dash_br.click_at_coord_fractions(
        f"#{cnst.SCATTER_FILTER_DRILL_THROUGH_SOURCE_ID} g[class^='trace']:nth-of-type(2) path:nth-of-type(20)", 0, 1
    )
    # check that new page is opened
    dash_br.wait_for_text_to_equal(page_title_path(), cnst.SET_CONTROL_FILTER_DRILL_THROUGH_TARGET)
    # check that appropriate filter selected on the new page
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.CHECKLIST_FILTER_DRILL_THROUGH_ID,
        select_all_status=False,
        options_value_status=[
            {"value": 1, "selected": False, "value_name": "setosa"},
            {"value": 2, "selected": True, "value_name": "versicolor"},
            {"value": 3, "selected": False, "value_name": "virginica"},
        ],
    )
    # Check y axis max value is '7'
    dash_br.wait_for_text_to_equal(
        graph_axis_value_path(
            graph_id=cnst.SCATTER_FILTER_DRILL_THROUGH_TARGET_ID, axis_value_number="5", axis_value="7"
        ),
        "7",
    )


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_parameter_drill_through(dash_br):
    accordion_select(dash_br, accordion_name=cnst.ACTIONS_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.SET_CONTROL_PARAMETER_DRILL_THROUGH_SOURCE,
    )
    # click on the 'versicolor' data in scatter graph
    dash_br.click_at_coord_fractions(
        f"#{cnst.SCATTER_PARAMETER_DRILL_THROUGH_SOURCE_ID} g[class^='trace']:nth-of-type(2) path:nth-of-type(20)", 0, 1
    )
    # check that new page is opened
    dash_br.wait_for_text_to_equal(page_title_path(), cnst.SET_CONTROL_PARAMETER_DRILL_THROUGH_TARGET)
    # check that appropriate parameter selected on the new page
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.RADIOITEMS_PARAMETER_DRILL_THROUGH_ID,
        checklist=False,
        options_value_status=[
            {"value": 1, "selected": False, "value_name": "setosa"},
            {"value": 2, "selected": True, "value_name": "versicolor"},
            {"value": 3, "selected": False, "value_name": "virginica"},
        ],
    )
    # check that graph title changed to 'versicolor'
    dash_br.wait_for_text_to_equal(".gtitle", "versicolor")


def test_ag_grid_filter_drill_through(dash_br):
    accordion_select(dash_br, accordion_name=cnst.ACTIONS_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.SET_CONTROL_FILTER_DRILL_THROUGH_AG_GRID_SOURCE,
    )
    # check if column 'Sepal_length' is available
    dash_br.wait_for_element(f"div[id='{cnst.AG_GRID_DRILL_THROUGH_ID}'] div:nth-of-type(1) div[col-id='sepal_length']")

    # click on the 'versicolor' data in ag_grid
    dash_br.multiple_click(
        f"div[id='{cnst.AG_GRID_DRILL_THROUGH_ID}'] div[class='ag-center-cols-container'] "
        f"div:nth-of-type(2) div[col-id='species']",
        1,
    )
    # check that new page is opened
    dash_br.wait_for_text_to_equal(page_title_path(), cnst.SET_CONTROL_FILTER_DRILL_THROUGH_AG_GRID_TARGET)
    # check that appropriate filter selected on the new page
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.RADIOITEMS_FILTER_DRILL_THROUGH_ID,
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
            graph_id=cnst.SCATTER_SECOND_FILTER_DRILL_THROUGH_TARGET_ID, axis_value_number="5", axis_value="7"
        ),
        "7",
    )


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_drill_down(dash_br):
    accordion_select(dash_br, accordion_name=cnst.ACTIONS_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.SET_CONTROL_DRILL_DOWN,
    )
    # click on the 'versicolor' data in scatter graph
    dash_br.click_at_coord_fractions(
        f"#{cnst.SCATTER_DRILL_DOWN_ID} g[class^='trace']:nth-of-type(2) path:nth-of-type(20)", 0, 1
    )
    # Check y axis max value is '7'
    dash_br.wait_for_text_to_equal(
        graph_axis_value_path(graph_id=cnst.SCATTER_DRILL_DOWN_ID, axis_value_number="5", axis_value="7"),
        "7",
    )
    # check that graph title changed to 'versicolor'
    dash_br.wait_for_text_to_equal(".gtitle", "Graph shows `versicolor` species.")
