from functools import wraps
from pathlib import Path

import pytest
import yaml
from e2e.asserts import assert_image_not_equal, assert_pixelmatch
from e2e.vizro import constants as cnst
from e2e.vizro.checkers import (
    check_graph_is_empty,
    check_graph_is_loaded,
    check_selected_categorical_component,
    check_selected_dropdown,
    check_slider_value,
)
from e2e.vizro.navigation import (
    accordion_select,
    clear_dropdown,
    page_select,
    select_dropdown_value,
    select_slider_handler,
)
from e2e.vizro.paths import (
    actions_progress_indicator_path,
    categorical_components_value_path,
    dropdown_arrow_path,
    graph_axis_value_path,
    slider_value_path,
)
from e2e.vizro.waiters import callbacks_finish_waiter


def dynamic_filters_data_config_manipulation(key, set_value=None):
    with open(cnst.DYNAMIC_FILTERS_DATA_CONFIG, "r+") as file:
        data = yaml.safe_load(file)
        data[key] = set_value

        file.seek(0)
        yaml.dump(data, file, default_flow_style=False)
        file.truncate()


def rewrite_dynamic_filters_data_config(func):
    """Rewriting dynamic_filters_data.yml."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        data = {
            "date_max": "2024-03-10",
            "date_min": "2024-03-05",
            "max": 7,
            "min": 6,
            "setosa": 5,
            "versicolor": 10,
            "virginica": 15,
        }
        with open(cnst.DYNAMIC_FILTERS_DATA_CONFIG, "w") as file:
            yaml.dump(data, file)
        func(*args, **kwargs)

    return wrapper


@pytest.mark.order(1)
def test_dropdown_values_not_disappear(dash_br):
    """Check for dynamic data specific scenario.

    This test checks the problem when dashboard is started with one scope of options
    for dropdown in database and during its usage database updated with new options, which will disappear
    from dropdown after reloading the page.
    This test should be run as the first in module because of specific database configuration.
    """
    # Select page and wait until it's loaded
    accordion_select(dash_br, accordion_name=cnst.DYNAMIC_DATA_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_CATEGORICAL_PAGE,
    )
    # Open dropdown menu
    dash_br.multiple_click(dropdown_arrow_path(dropdown_id=cnst.DROPDOWN_MULTI_DYNAMIC_FILTER_ID), 1, delay=0.1)
    # Check that all values are selected
    check_selected_dropdown(
        dash_br,
        dropdown_id=cnst.DROPDOWN_MULTI_DYNAMIC_FILTER_ID,
        all_value=True,
        expected_selected_options=["setosa"],
        expected_unselected_options=[],
    )
    # Add "versicolor" and "virginica" from the dynamic data
    dynamic_filters_data_config_manipulation(key="versicolor", set_value=10)
    dynamic_filters_data_config_manipulation(key="virginica", set_value=15)
    dash_br.driver.refresh()
    # Open dropdown menu
    dash_br.multiple_click(dropdown_arrow_path(dropdown_id=cnst.DROPDOWN_MULTI_DYNAMIC_FILTER_ID), 1, delay=0.1)
    # Check that all values are present and only "setosa" selected
    check_selected_dropdown(
        dash_br,
        dropdown_id=cnst.DROPDOWN_MULTI_DYNAMIC_FILTER_ID,
        all_value=False,
        expected_selected_options=["setosa"],
        expected_unselected_options=["SelectAll", "versicolor", "virginica"],
    )
    # Choose "versicolor" and "virginica"
    select_dropdown_value(dash_br, dropdown_id=cnst.DROPDOWN_MULTI_DYNAMIC_FILTER_ID, value="versicolor")
    select_dropdown_value(dash_br, dropdown_id=cnst.DROPDOWN_MULTI_DYNAMIC_FILTER_ID, value="virginica")
    # Open dropdown menu
    dash_br.multiple_click(dropdown_arrow_path(dropdown_id=cnst.DROPDOWN_MULTI_DYNAMIC_FILTER_ID), 1, delay=0.1)
    # Check that all values are selected
    check_selected_dropdown(
        dash_br,
        dropdown_id=cnst.DROPDOWN_MULTI_DYNAMIC_FILTER_ID,
        all_value=True,
        expected_selected_options=["setosa", "versicolor", "virginica"],
        expected_unselected_options=[],
    )
    dash_br.driver.refresh()
    # Open dropdown menu
    dash_br.multiple_click(dropdown_arrow_path(dropdown_id=cnst.DROPDOWN_MULTI_DYNAMIC_FILTER_ID), 1, delay=0.1)
    # Check that all values are still selected
    check_selected_dropdown(
        dash_br,
        dropdown_id=cnst.DROPDOWN_MULTI_DYNAMIC_FILTER_ID,
        all_value=True,
        expected_selected_options=["setosa", "versicolor", "virginica"],
        expected_unselected_options=[],
    )


@pytest.mark.parametrize(
    "cache, slider_id",
    [
        ("cached", cnst.SLIDER_DYNAMIC_DATA_CACHED_ID),
        ("cached_not", cnst.SLIDER_DYNAMIC_DATA_ID),
    ],
)
def test_data_dynamic_parametrization(dash_br, cache, slider_id):
    """This test checks parametrized data loading and how it is working with and without cache."""
    first_screen = f"{cache}_screen_first_test_data_dynamic_parametrization.png"
    second_screen = f"{cache}_screen_second_test_data_dynamic_parametrization.png"
    third_screen = f"{cache}_screen_third_test_data_dynamic_parametrization.png"
    accordion_select(dash_br, accordion_name=cnst.DYNAMIC_DATA_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_DATA_PAGE,
    )

    # move slider to value '20'
    select_slider_handler(dash_br, elem_id=slider_id, value=2)
    callbacks_finish_waiter(dash_br)
    # wait till actions will be finished ad no progress indicator will be visible on the screenshots
    dash_br.wait_for_no_elements(actions_progress_indicator_path())
    dash_br.driver.save_screenshot(first_screen)

    # move slider to value '60'
    select_slider_handler(dash_br, elem_id=slider_id, value=6)
    callbacks_finish_waiter(dash_br)
    # wait till actions will be finished ad no progress indicator will be visible on the screenshots
    dash_br.wait_for_no_elements(actions_progress_indicator_path())
    dash_br.driver.save_screenshot(second_screen)

    # move slider to value '20'
    select_slider_handler(dash_br, elem_id=slider_id, value=2)
    callbacks_finish_waiter(dash_br)
    # wait till actions will be finished ad no progress indicator will be visible on the screenshots
    dash_br.wait_for_no_elements(actions_progress_indicator_path())
    dash_br.driver.save_screenshot(third_screen)

    # first and second screens should be different
    assert_image_not_equal(first_screen, second_screen)
    if cache == "cached":
        # first and third screens should be the same
        assert_pixelmatch(first_screen, third_screen)
    if cache == "not_cached":
        # first and third screens should be different
        assert_image_not_equal(first_screen, third_screen)
    for file in Path(".").glob("*test_data_dynamic_parametrization*"):
        file.unlink()


@rewrite_dynamic_filters_data_config
def test_dropdown_filter_multi(dash_br):
    """Initial selected value is 'ALL'."""
    # Select page and wait until it's loaded
    accordion_select(dash_br, accordion_name=cnst.DYNAMIC_DATA_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_CATEGORICAL_PAGE,
    )

    # Choose "versicolor" value and check that graph is reloaded
    clear_dropdown(dash_br, cnst.DROPDOWN_MULTI_DYNAMIC_FILTER_ID)
    select_dropdown_value(dash_br, dropdown_id=cnst.DROPDOWN_MULTI_DYNAMIC_FILTER_ID, value="versicolor")
    check_graph_is_loaded(dash_br, graph_id=cnst.BOX_DYNAMIC_FILTERS_ID)

    # Remove "setosa" and "versicolor" from the dynamic data and simulate refreshing the page
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_NUMERICAL_PAGE,
    )
    dynamic_filters_data_config_manipulation(key="setosa", set_value=0)
    dynamic_filters_data_config_manipulation(key="versicolor", set_value=0)
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_CATEGORICAL_PAGE,
    )

    # open dropdown and check selected and unselected values
    dash_br.multiple_click(dropdown_arrow_path(dropdown_id=cnst.DROPDOWN_MULTI_DYNAMIC_FILTER_ID), 1)
    check_selected_dropdown(
        dash_br,
        dropdown_id=cnst.DROPDOWN_MULTI_DYNAMIC_FILTER_ID,
        expected_selected_options=["versicolor"],
        expected_unselected_options=["SelectAll", "virginica"],
    )


@rewrite_dynamic_filters_data_config
def test_dropdown_filter_select_all_value(dash_br):
    """Initial selected value is 'setosa'."""
    # Select page and wait until it's loaded
    accordion_select(dash_br, accordion_name=cnst.DYNAMIC_DATA_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_CATEGORICAL_PAGE,
    )
    # TODO: delete this code block after fixing https://github.com/McK-Internal/vizro-internal/issues/1356
    # -------- START: code block --------
    dynamic_filters_data_config_manipulation(key="versicolor", set_value=15)
    dynamic_filters_data_config_manipulation(key="virginica", set_value=10)
    dash_br.driver.refresh()
    dash_br.multiple_click(dropdown_arrow_path(dropdown_id=cnst.DROPDOWN_MULTI_DYNAMIC_FILTER_ID), 1, delay=0.1)
    select_dropdown_value(dash_br, dropdown_id=cnst.DROPDOWN_MULTI_DYNAMIC_FILTER_ID, value="versicolor")
    select_dropdown_value(dash_br, dropdown_id=cnst.DROPDOWN_MULTI_DYNAMIC_FILTER_ID, value="virginica")
    # -------- END: code block --------
    # Open dropdown menu
    dash_br.multiple_click(dropdown_arrow_path(dropdown_id=cnst.DROPDOWN_MULTI_DYNAMIC_FILTER_ID), 1, delay=0.1)
    # Check that all values are selected
    check_selected_dropdown(
        dash_br,
        dropdown_id=cnst.DROPDOWN_MULTI_DYNAMIC_FILTER_ID,
        all_value=True,
        expected_selected_options=["setosa", "versicolor", "virginica"],
        expected_unselected_options=[],
    )
    # delete last options 'versicolor' and 'virginica'
    dash_br.clear_input(f"div[id='{cnst.DROPDOWN_MULTI_DYNAMIC_FILTER_ID}']")
    dash_br.clear_input(f"div[id='{cnst.DROPDOWN_MULTI_DYNAMIC_FILTER_ID}']")
    # Remove "versicolor" and "virginica" from the dynamic data
    dynamic_filters_data_config_manipulation(key="versicolor", set_value=0)
    dynamic_filters_data_config_manipulation(key="virginica", set_value=0)
    # Simulate refreshing the page
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_NUMERICAL_PAGE,
    )
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_CATEGORICAL_PAGE,
    )
    dash_br.multiple_click(dropdown_arrow_path(dropdown_id=cnst.DROPDOWN_MULTI_DYNAMIC_FILTER_ID), 1, delay=0.1)
    # Check that only "setosa" selected and listed
    check_selected_dropdown(
        dash_br,
        dropdown_id=cnst.DROPDOWN_MULTI_DYNAMIC_FILTER_ID,
        all_value=True,
        expected_selected_options=["setosa"],
        expected_unselected_options=[],
    )
    # Add "versicolor" to the dynamic data and simulate refreshing the page
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_NUMERICAL_PAGE,
    )
    dynamic_filters_data_config_manipulation(key="versicolor", set_value=10)
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_CATEGORICAL_PAGE,
    )
    dash_br.multiple_click(dropdown_arrow_path(dropdown_id=cnst.DROPDOWN_MULTI_DYNAMIC_FILTER_ID), 1, delay=0.1)
    # Check that "setosa" is selected and "versicolor" just listed
    check_selected_dropdown(
        dash_br,
        dropdown_id=cnst.DROPDOWN_MULTI_DYNAMIC_FILTER_ID,
        all_value=False,
        expected_selected_options=["setosa"],
        expected_unselected_options=["SelectAll", "versicolor"],
    )
    # Choose "versicolor"
    select_dropdown_value(dash_br, dropdown_id=cnst.DROPDOWN_MULTI_DYNAMIC_FILTER_ID, value="versicolor")
    dash_br.multiple_click(dropdown_arrow_path(dropdown_id=cnst.DROPDOWN_MULTI_DYNAMIC_FILTER_ID), 1, delay=0.1)
    # Check that only "setosa" and "versicolor" selected and listed
    check_selected_dropdown(
        dash_br,
        dropdown_id=cnst.DROPDOWN_MULTI_DYNAMIC_FILTER_ID,
        all_value=True,
        expected_selected_options=["setosa", "versicolor"],
        expected_unselected_options=[],
    )
    # Remove "versicolor" from the dynamic data and simulate refreshing the page
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_NUMERICAL_PAGE,
    )
    dynamic_filters_data_config_manipulation(key="versicolor", set_value=0)
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_CATEGORICAL_PAGE,
    )
    dash_br.multiple_click(dropdown_arrow_path(dropdown_id=cnst.DROPDOWN_MULTI_DYNAMIC_FILTER_ID), 1, delay=0.1)
    # Check that only "setosa" and "versicolor" selected and listed
    check_selected_dropdown(
        dash_br,
        dropdown_id=cnst.DROPDOWN_MULTI_DYNAMIC_FILTER_ID,
        all_value=True,
        expected_selected_options=["setosa", "versicolor"],
        expected_unselected_options=[],
    )
    # delete last option 'versicolor'
    dash_br.clear_input(f"div[id='{cnst.DROPDOWN_MULTI_DYNAMIC_FILTER_ID}']")
    # Check that "setosa" is selected and "versicolor" just listed
    check_selected_dropdown(
        dash_br,
        dropdown_id=cnst.DROPDOWN_MULTI_DYNAMIC_FILTER_ID,
        all_value=False,
        expected_selected_options=["setosa"],
        expected_unselected_options=["SelectAll", "versicolor"],
    )
    # Simulate refreshing the page
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_NUMERICAL_PAGE,
    )
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_CATEGORICAL_PAGE,
    )
    dash_br.multiple_click(dropdown_arrow_path(dropdown_id=cnst.DROPDOWN_MULTI_DYNAMIC_FILTER_ID), 1, delay=0.1)
    # Check that only "setosa" selected and listed
    check_selected_dropdown(
        dash_br,
        dropdown_id=cnst.DROPDOWN_MULTI_DYNAMIC_FILTER_ID,
        all_value=True,
        expected_selected_options=["setosa"],
        expected_unselected_options=[],
    )


@rewrite_dynamic_filters_data_config
def test_dropdown_filter(dash_br):
    """Initial selected value is 'setosa'."""
    # Select page and wait until it's loaded
    accordion_select(dash_br, accordion_name=cnst.DYNAMIC_DATA_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_CATEGORICAL_PAGE,
    )

    # Choose "versicolor" value and check that graph is reloaded
    select_dropdown_value(dash_br, dropdown_id=cnst.DROPDOWN_DYNAMIC_FILTER_ID, value="versicolor")
    check_graph_is_loaded(dash_br, graph_id=cnst.BOX_DYNAMIC_FILTERS_ID)

    # Remove "setosa" and "versicolor" from the dynamic data and simulate refreshing the page
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_NUMERICAL_PAGE,
    )
    dynamic_filters_data_config_manipulation(key="setosa", set_value=0)
    dynamic_filters_data_config_manipulation(key="versicolor", set_value=0)
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_CATEGORICAL_PAGE,
    )

    # open dropdown and check selected and unselected values
    dash_br.multiple_click(dropdown_arrow_path(dropdown_id=cnst.DROPDOWN_DYNAMIC_FILTER_ID), 1)
    check_selected_dropdown(
        dash_br,
        dropdown_id=cnst.DROPDOWN_DYNAMIC_FILTER_ID,
        expected_selected_options=["versicolor"],
        expected_unselected_options=["versicolor", "virginica"],
    )


@rewrite_dynamic_filters_data_config
def test_checklist_filter_select_all_value(dash_br):
    """Initial selected value is 'setosa'."""
    # Load the page
    accordion_select(dash_br, accordion_name=cnst.DYNAMIC_DATA_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_CATEGORICAL_PAGE,
    )
    # TODO: delete this code block after fixing https://github.com/McK-Internal/vizro-internal/issues/1356
    # -------- START: code block --------
    dynamic_filters_data_config_manipulation(key="versicolor", set_value=15)
    dynamic_filters_data_config_manipulation(key="virginica", set_value=10)
    dash_br.driver.refresh()
    dash_br.multiple_click(categorical_components_value_path(elem_id=cnst.CHECKLIST_DYNAMIC_FILTER_ID, value=2), 1)
    dash_br.multiple_click(
        categorical_components_value_path(elem_id=cnst.CHECKLIST_DYNAMIC_FILTER_ID, value=3), 1, delay=0.1
    )
    # -------- END: code block --------
    # Check that "setosa", "versicolor" and "virginica" is the listed options
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.CHECKLIST_DYNAMIC_FILTER_ID,
        checklist=True,
        select_all_status=True,
        options_value_status=[
            {"value": 1, "selected": True, "value_name": "setosa"},
            {"value": 2, "selected": True, "value_name": "versicolor"},
            {"value": 3, "selected": True, "value_name": "virginica"},
        ],
    )
    # Unselect "versicolor" and "virginica"
    dash_br.multiple_click(categorical_components_value_path(elem_id=cnst.CHECKLIST_DYNAMIC_FILTER_ID, value=2), 1)
    dash_br.multiple_click(categorical_components_value_path(elem_id=cnst.CHECKLIST_DYNAMIC_FILTER_ID, value=3), 1)
    # Remove "versicolor" and "virginica" from the dynamic data
    dynamic_filters_data_config_manipulation(key="versicolor", set_value=0)
    dynamic_filters_data_config_manipulation(key="virginica", set_value=0)
    # Simulate refreshing the page
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_NUMERICAL_PAGE,
    )
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_CATEGORICAL_PAGE,
    )
    # Check that "setosa" is the only listed options
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.CHECKLIST_DYNAMIC_FILTER_ID,
        checklist=True,
        select_all_status=True,
        options_value_status=[
            {"value": 1, "selected": True, "value_name": "setosa"},
        ],
    )
    # Add "versicolor" to the dynamic data
    dynamic_filters_data_config_manipulation(key="versicolor", set_value=10)
    # Simulate refreshing the page
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_NUMERICAL_PAGE,
    )
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_CATEGORICAL_PAGE,
    )
    # Check that "setosa" is the only selected option
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.CHECKLIST_DYNAMIC_FILTER_ID,
        checklist=True,
        select_all_status=False,
        options_value_status=[
            {"value": 1, "selected": True, "value_name": "setosa"},
            {"value": 2, "selected": False, "value_name": "versicolor"},
        ],
    )
    # Select "versicolor"
    dash_br.multiple_click(
        categorical_components_value_path(elem_id=cnst.CHECKLIST_DYNAMIC_FILTER_ID, value=2), 1, delay=0.1
    )
    # Check that "setosa" and "versicolor" selected
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.CHECKLIST_DYNAMIC_FILTER_ID,
        checklist=True,
        select_all_status=True,
        options_value_status=[
            {"value": 1, "selected": True, "value_name": "setosa"},
            {"value": 2, "selected": True, "value_name": "versicolor"},
        ],
    )
    # Delete "versicolor" from the dynamic data
    dynamic_filters_data_config_manipulation(key="versicolor", set_value=0)
    # Simulate refreshing the page
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_NUMERICAL_PAGE,
    )
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_CATEGORICAL_PAGE,
    )
    # Check that "setosa" and "versicolor" selected
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.CHECKLIST_DYNAMIC_FILTER_ID,
        checklist=True,
        select_all_status=True,
        options_value_status=[
            {"value": 1, "selected": True, "value_name": "setosa"},
            {"value": 2, "selected": True, "value_name": "versicolor"},
        ],
    )
    # Unselect "versicolor"
    dash_br.multiple_click(
        categorical_components_value_path(elem_id=cnst.CHECKLIST_DYNAMIC_FILTER_ID, value=2), 1, delay=0.1
    )
    # Check that only "setosa" selected
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.CHECKLIST_DYNAMIC_FILTER_ID,
        checklist=True,
        select_all_status=False,
        options_value_status=[
            {"value": 1, "selected": True, "value_name": "setosa"},
            {"value": 2, "selected": False, "value_name": "versicolor"},
        ],
    )
    # Simulate refreshing the page
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_NUMERICAL_PAGE,
    )
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_CATEGORICAL_PAGE,
    )
    # Check that "setosa" selected and the only option
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.CHECKLIST_DYNAMIC_FILTER_ID,
        checklist=True,
        select_all_status=True,
        options_value_status=[
            {"value": 1, "selected": True, "value_name": "setosa"},
        ],
    )


@rewrite_dynamic_filters_data_config
def test_checklist_filter(dash_br):
    """Initial selected value is 'ALL'."""
    accordion_select(dash_br, accordion_name=cnst.DYNAMIC_DATA_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_CATEGORICAL_PAGE,
    )

    # Choose "versicolor" value and check that graph is reloaded
    dash_br.multiple_click(categorical_components_value_path(elem_id=cnst.CHECKLIST_DYNAMIC_FILTER_ID, value=1), 1)
    # TODO: change value to 3 after fixing https://github.com/McK-Internal/vizro-internal/issues/1356
    dash_br.multiple_click(categorical_components_value_path(elem_id=cnst.CHECKLIST_DYNAMIC_FILTER_ID, value=2), 1)
    check_graph_is_loaded(dash_br, cnst.BOX_DYNAMIC_FILTERS_ID)

    # Remove "setosa" and "versicolor" from the dynamic data and simulate refreshing the page
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_NUMERICAL_PAGE,
    )
    dynamic_filters_data_config_manipulation(key="setosa", set_value=0)
    dynamic_filters_data_config_manipulation(key="versicolor", set_value=0)
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_CATEGORICAL_PAGE,
    )

    # Check that "versicolor" and "virginica" is the only listed options
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.CHECKLIST_DYNAMIC_FILTER_ID,
        checklist=True,
        options_value_status=[
            {"value": 1, "selected": True, "value_name": "versicolor"},
            {"value": 2, "selected": False, "value_name": "virginica"},
        ],
    )


@rewrite_dynamic_filters_data_config
def test_radio_items_filter(dash_br):
    """Initial selected value is 'setosa'."""
    accordion_select(dash_br, accordion_name=cnst.DYNAMIC_DATA_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_CATEGORICAL_PAGE,
    )

    # Choose "versicolor" value and check that graph is reloaded
    dash_br.multiple_click(categorical_components_value_path(elem_id=cnst.RADIOITEMS_DYNAMIC_FILTER_ID, value=2), 1)
    check_graph_is_loaded(dash_br, cnst.BOX_DYNAMIC_FILTERS_ID)

    # Remove "setosa" and "versicolor" from the dynamic data and simulate refreshing the page
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_NUMERICAL_PAGE,
    )
    dynamic_filters_data_config_manipulation(key="setosa", set_value=0)
    dynamic_filters_data_config_manipulation(key="versicolor", set_value=0)
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_CATEGORICAL_PAGE,
    )

    # Check that "versicolor" and "virginica" is the only listed options
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.RADIOITEMS_DYNAMIC_FILTER_ID,
        options_value_status=[
            {"value": 1, "selected": True, "value_name": "versicolor"},
            {"value": 2, "selected": False, "value_name": "virginica"},
        ],
    )


@rewrite_dynamic_filters_data_config
def test_numerical_filters(dash_br):
    """Initial selected value for slider is 6. Initial selected values for range_slider are 6 and 7."""
    accordion_select(dash_br, accordion_name=cnst.DYNAMIC_DATA_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_NUMERICAL_PAGE,
    )

    # Set "min" option to "5" for the dynamic data and simulate refreshing the page
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_CATEGORICAL_PAGE,
    )
    dynamic_filters_data_config_manipulation(key="min", set_value=5)
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_NUMERICAL_PAGE,
    )

    # Check slider value
    check_slider_value(dash_br, expected_end_value="6", elem_id=cnst.SLIDER_DYNAMIC_FILTER_ID)
    # Check range slider values
    check_slider_value(
        dash_br, elem_id=cnst.RANGE_SLIDER_DYNAMIC_FILTER_ID, expected_start_value="6", expected_end_value="7"
    )

    # Change "min" slider and range slider values to "5"
    dash_br.multiple_click(slider_value_path(elem_id=cnst.SLIDER_DYNAMIC_FILTER_ID, value=1), 1)
    check_graph_is_loaded(dash_br, graph_id=cnst.BAR_DYNAMIC_FILTER_ID)
    dash_br.multiple_click(slider_value_path(elem_id=cnst.RANGE_SLIDER_DYNAMIC_FILTER_ID, value=1), 1)
    check_graph_is_loaded(dash_br, graph_id=cnst.BAR_DYNAMIC_FILTER_ID)

    # Check slider value
    check_slider_value(dash_br, expected_end_value="5", elem_id=cnst.SLIDER_DYNAMIC_FILTER_ID)
    # Check range slider values
    check_slider_value(
        dash_br, elem_id=cnst.RANGE_SLIDER_DYNAMIC_FILTER_ID, expected_start_value="5", expected_end_value="7"
    )

    # Set "min" option to "6" for the dynamic data and simulate refreshing the page
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_CATEGORICAL_PAGE,
    )
    dynamic_filters_data_config_manipulation(key="min", set_value=6)
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_NUMERICAL_PAGE,
    )

    # Check slider value
    check_slider_value(dash_br, expected_end_value="5", elem_id=cnst.SLIDER_DYNAMIC_FILTER_ID)
    # Check range slider values
    check_slider_value(
        dash_br, elem_id=cnst.RANGE_SLIDER_DYNAMIC_FILTER_ID, expected_start_value="5", expected_end_value="7"
    )


@rewrite_dynamic_filters_data_config
def test_datepicker_range_filters(dash_br):
    """Initial selected values are 5 March 2024 and 10 March 2024."""
    accordion_select(dash_br, accordion_name=cnst.DYNAMIC_DATA_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_DATEPICKER_PAGE,
    )

    # Check y axis min value is '0'
    dash_br.wait_for_text_to_equal(
        graph_axis_value_path(graph_id=cnst.BAR_DYNAMIC_DATEPICKER_FILTER_ID, axis_value_number="1", axis_value="0"),
        "0",
    )

    # Check y axis max value is '6'
    dash_br.wait_for_text_to_equal(
        graph_axis_value_path(graph_id=cnst.BAR_DYNAMIC_DATEPICKER_FILTER_ID, axis_value_number="4", axis_value="6"),
        "6",
    )

    # check current date values
    dash_br.wait_for_text_to_equal(f'button[id="{cnst.DATEPICKER_DYNAMIC_RANGE_ID}"]', "Mar 5, 2024 – Mar 10, 2024")  # noqa: RUF001

    # Set "date_max" option to "2024-03-09" for the dynamic data and simulate refreshing the page
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_CATEGORICAL_PAGE,
    )
    dynamic_filters_data_config_manipulation(key="date_max", set_value="2024-03-09")
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_DATEPICKER_PAGE,
    )
    dash_br.wait_for_text_to_equal(f'button[id="{cnst.DATEPICKER_DYNAMIC_RANGE_ID}"]', "Mar 5, 2024 – Mar 10, 2024")  # noqa: RUF001

    # Check y axis max value is '5'
    dash_br.wait_for_text_to_equal(
        graph_axis_value_path(graph_id=cnst.BAR_DYNAMIC_DATEPICKER_FILTER_ID, axis_value_number="6", axis_value="5"),
        "5",
    )

    # open datepicker calendar and choose dates from 6 to 10 March 2024
    dash_br.multiple_click(f'button[id="{cnst.DATEPICKER_DYNAMIC_RANGE_ID}"]', 1)
    dash_br.wait_for_element('div[data-calendar="true"]')
    dash_br.multiple_click('button[aria-label="6 March 2024"]', 1)
    dash_br.multiple_click('button[aria-label="10 March 2024"]', 1)
    check_graph_is_loaded(dash_br, cnst.BAR_DYNAMIC_DATEPICKER_FILTER_ID)

    # Check y axis max value is '4'
    dash_br.wait_for_text_to_equal(
        graph_axis_value_path(graph_id=cnst.BAR_DYNAMIC_DATEPICKER_FILTER_ID, axis_value_number="5", axis_value="4"),
        "4",
    )

    # Set "date_min" option to "2024-03-06" for the dynamic data and simulate refreshing the page
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_CATEGORICAL_PAGE,
    )
    dynamic_filters_data_config_manipulation(key="date_min", set_value="2024-03-06")
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_DATEPICKER_PAGE,
    )
    dash_br.wait_for_text_to_equal(f'button[id="{cnst.DATEPICKER_DYNAMIC_RANGE_ID}"]', "Mar 6, 2024 – Mar 10, 2024")  # noqa: RUF001

    # open the calendar and check if '5 March' is disabled
    dash_br.multiple_click(f'button[id="{cnst.DATEPICKER_DYNAMIC_RANGE_ID}"]', 1)
    dash_br.wait_for_element('div[data-calendar="true"]')
    dash_br.wait_for_element('button[aria-label="5 March 2024"][data-disabled="true"]')


@rewrite_dynamic_filters_data_config
def test_datepicker_single_filters(dash_br):
    """Initial selected value is 5 March 2024."""
    accordion_select(dash_br, accordion_name=cnst.DYNAMIC_DATA_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_DATEPICKER_PAGE,
    )

    # check current date value
    dash_br.wait_for_text_to_equal(f'button[id="{cnst.DATEPICKER_DYNAMIC_SINGLE_ID}"]', "Mar 5, 2024")

    # Check y axis min value is '0'
    dash_br.wait_for_text_to_equal(
        graph_axis_value_path(
            graph_id=cnst.BAR_DYNAMIC_DATEPICKER_SINGLE_FILTER_ID, axis_value_number="1", axis_value="0"
        ),
        "0",
    )

    # Check y axis max value is '1'
    dash_br.wait_for_text_to_equal(
        graph_axis_value_path(
            graph_id=cnst.BAR_DYNAMIC_DATEPICKER_SINGLE_FILTER_ID, axis_value_number="6", axis_value="1"
        ),
        "1",
    )

    # Set "date_min" option to "2024-03-06" for the dynamic data and simulate refreshing the page
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_CATEGORICAL_PAGE,
    )
    dynamic_filters_data_config_manipulation(key="date_min", set_value="2024-03-06")
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_DATEPICKER_PAGE,
    )
    dash_br.wait_for_text_to_equal(f'button[id="{cnst.DATEPICKER_DYNAMIC_SINGLE_ID}"]', "Mar 5, 2024")

    # Check y axis min value is '-1' (empty chart)
    check_graph_is_empty(dash_br, graph_id=cnst.BAR_DYNAMIC_DATEPICKER_SINGLE_FILTER_ID)

    # Check y axis max value is '4'
    dash_br.wait_for_text_to_equal(
        graph_axis_value_path(
            graph_id=cnst.BAR_DYNAMIC_DATEPICKER_SINGLE_FILTER_ID, axis_value_number="6", axis_value="4"
        ),
        "4",
    )

    # open datepicker calendar and choose 6 March 2024
    dash_br.multiple_click(f'button[id="{cnst.DATEPICKER_DYNAMIC_SINGLE_ID}"]', 1)
    dash_br.wait_for_element('div[data-calendar="true"]')
    dash_br.multiple_click('button[aria-label="6 March 2024"]', 1)
    dash_br.wait_for_text_to_equal(f'button[id="{cnst.DATEPICKER_DYNAMIC_SINGLE_ID}"]', "Mar 6, 2024")

    # Check y axis max value is '1'
    dash_br.wait_for_text_to_equal(
        graph_axis_value_path(
            graph_id=cnst.BAR_DYNAMIC_DATEPICKER_SINGLE_FILTER_ID, axis_value_number="6", axis_value="1"
        ),
        "1",
    )

    # simulate refreshing the page
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_CATEGORICAL_PAGE,
    )
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_FILTERS_DATEPICKER_PAGE,
    )
    dash_br.wait_for_text_to_equal(f'button[id="{cnst.DATEPICKER_DYNAMIC_SINGLE_ID}"]', "Mar 6, 2024")

    # open the calendar and check if '5 March' is disabled
    dash_br.multiple_click(f'button[id="{cnst.DATEPICKER_DYNAMIC_SINGLE_ID}"]', 1)
    dash_br.wait_for_element('div[data-calendar="true"]')
    dash_br.wait_for_element('button[aria-label="5 March 2024"][data-disabled="true"]')


def test_dynamic_data_parameter_refresh_dynamic_filters(dash_br):
    """Test automatic refreshing of the dynamic filters and their targets when the data_frame parameter is changed.

    Page configuration includes dynamic data scatter chart which controls by slider parameter and static data scatter
    which has 'virginica' data only.
    """
    accordion_select(dash_br, accordion_name=cnst.DYNAMIC_DATA_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.DYNAMIC_DATA_DF_PARAMETER_PAGE,
    )

    # select 'virginica' value and check scatter graph point color
    dash_br.multiple_click(categorical_components_value_path(elem_id=cnst.RADIOITEMS_FILTER_DF_PARAMETER, value=3), 1)
    dash_br.wait_for_element(f"div[id='{cnst.SCATTER_DF_PARAMETER}'] path[style*='rgb(57, 73, 171)']:nth-of-type(1)")
    dash_br.wait_for_element(f"div[id='{cnst.SCATTER_DF_STATIC}'] path[style*='rgb(57, 73, 171)']:nth-of-type(1)")

    # select '10' points for slider which is showing only 'setosa' data and check that scatter graph
    # with dynamic data is empty and that scatter graph with static data is the same
    select_slider_handler(dash_br, elem_id=cnst.SLIDER_DF_PARAMETER, value=2)
    check_graph_is_loaded(dash_br, graph_id=cnst.SCATTER_DF_STATIC)
    check_graph_is_empty(dash_br, graph_id=cnst.SCATTER_DF_PARAMETER)
    dash_br.wait_for_element(f"div[id='{cnst.SCATTER_DF_STATIC}'] path[style*='rgb(57, 73, 171)']:nth-of-type(1)")

    # Check that "setosa" and "virginica" is the only listed options
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.RADIOITEMS_FILTER_DF_PARAMETER,
        options_value_status=[
            {"value": 1, "selected": False, "value_name": "setosa"},
            {"value": 2, "selected": True, "value_name": "virginica"},
        ],
    )

    # simulate refreshing the page to check if filters and graphs stays the same
    page_select(dash_br, page_name=cnst.DYNAMIC_FILTERS_CATEGORICAL_PAGE)
    page_select(dash_br, page_name=cnst.DYNAMIC_DATA_DF_PARAMETER_PAGE)

    # check that dynamic data graph is empty and static data graph stays the same
    check_graph_is_empty(dash_br, graph_id=cnst.SCATTER_DF_PARAMETER)
    dash_br.wait_for_element(f"div[id='{cnst.SCATTER_DF_STATIC}'] path[style*='rgb(57, 73, 171)']:nth-of-type(1)")

    # Check that "setosa" and "virginica" is the only listed options
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.RADIOITEMS_FILTER_DF_PARAMETER,
        options_value_status=[
            {"value": 1, "selected": False, "value_name": "setosa"},
            {"value": 2, "selected": True, "value_name": "virginica"},
        ],
    )

    # select 'setosa' value and check dynamic scatter graph point color and that static scatter graph is empty
    dash_br.multiple_click(categorical_components_value_path(elem_id=cnst.RADIOITEMS_FILTER_DF_PARAMETER, value=1), 1)
    dash_br.wait_for_element(f"div[id='{cnst.SCATTER_DF_PARAMETER}'] path[style*='rgb(0, 180, 255)']:nth-of-type(1)")
    check_graph_is_empty(dash_br, graph_id=cnst.SCATTER_DF_STATIC)

    # Check that "setosa" and "virginica" is the only listed options
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.RADIOITEMS_FILTER_DF_PARAMETER,
        options_value_status=[
            {"value": 1, "selected": True, "value_name": "setosa"},
            {"value": 2, "selected": False, "value_name": "virginica"},
        ],
    )
