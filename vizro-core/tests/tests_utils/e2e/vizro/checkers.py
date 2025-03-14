import os
import time

import e2e.vizro.constants as cnst
from e2e.vizro.paths import categorical_components_value_name_path, categorical_components_value_path, select_all_path
from e2e.vizro.waiters import graph_load_waiter
from hamcrest import any_of, assert_that, contains_string, equal_to
from selenium.webdriver.support.color import Color


def browser_console_warnings_checker(log_level, log_levels):
    """Whitelist for browser console errors and its assert."""
    assert_that(
        log_level["message"],
        any_of(
            contains_string(cnst.INVALID_PROP_ERROR),
            contains_string(cnst.REACT_NOT_RECOGNIZE_ERROR),
            contains_string(cnst.SCROLL_ZOOM_ERROR),
            contains_string(cnst.REACT_RENDERING_ERROR),
            contains_string(cnst.UNMOUNT_COMPONENTS_ERROR),
            contains_string(cnst.WILLMOUNT_RENAMED_WARNING),
            contains_string(cnst.WILLRECEIVEPROPS_RENAMED_WARNING),
            contains_string(cnst.READPIXELS_WARNING),
            contains_string(cnst.WEBGL_WARNING),
        ),
        reason=f"Error outoput: {log_levels}",
    )


def check_graph_is_loading(driver, graph_id):
    """Waiting for graph to start reloading."""
    driver.wait_for_element(f"div[id='{graph_id}'][data-dash-is-loading='true']")
    graph_load_waiter(driver, graph_id)


def check_slider_value(driver, elem_id, expected_end_value, expected_start_value=None):
    end_value = driver.find_element(f"input[id='{elem_id}_end_value']").get_attribute("value")
    assert_that(
        end_value,
        equal_to(expected_end_value),
        reason=f"Element number is '{end_value}', but expected number is '{expected_end_value}'",
    )
    if expected_start_value:
        start_value = driver.find_element(f"input[id='{elem_id}_start_value']").get_attribute("value")
        assert_that(
            start_value,
            equal_to(expected_start_value),
            reason=f"Element number is '{start_value}', but expected number is '{expected_start_value}'",
        )


def check_accordion_active(driver, accordion_name):
    driver.wait_for_text_to_equal("button[class='accordion-button']", accordion_name)


def check_theme_color(driver, color):
    driver.wait_for_element(f"html[data-bs-theme='{color}']")


def check_ag_grid_theme_color(driver, ag_grid_id, color):
    driver.wait_for_element(f"div[id='__input_{ag_grid_id}'][class='{color}']")


def check_graph_color(driver, style_background, color):
    rgba = driver.wait_for_element(f"svg[style='{style_background}']").value_of_css_property("background-color")
    graph_color = Color.from_string(rgba).rgba
    assert_that(
        graph_color,
        equal_to(color),
        reason=f"Graph color is '{graph_color}', but expected color is '{color}'",
    )


def check_selected_checklist(driver, checklist_id, select_all_status, options_value_status):
    # select_all = driver.find_element(select_all_path(elem_id=checklist_id))
    # assert_that(select_all.is_selected(), equal_to(select_all_status))
    for option in options_value_status:
        status = driver.find_element(categorical_components_value_path(elem_id=checklist_id, value=option["value"]))
        value_name = driver.find_element(
            categorical_components_value_name_path(elem_id=checklist_id, value=option["value"])
        )
        assert_that(status.is_selected(), equal_to(option["status"]))
        assert_that(value_name.text, equal_to(option["value_name"]))


def check_selected_dropdown(
    driver, dropdown_id, expected_selected_options, expected_unselected_options, all_value=False
):
    selected_options = driver.find_elements(f"div[id='{dropdown_id}'] span[class='Select-value-label']")
    selected_options_list = ["".join(option.text.split()) for option in selected_options]
    unselected_options = driver.find_elements(f"div[id='{dropdown_id}'] .VirtualizedSelectOption")
    unselected_options_list = ["".join(option.text.split()) for option in unselected_options]
    assert_that(selected_options_list, equal_to(expected_selected_options))
    assert_that(unselected_options_list, equal_to(expected_unselected_options))
    if all_value:
        status = driver.find_element(select_all_path(elem_id=dropdown_id))
        assert_that(status.is_selected(), equal_to(all_value))


def check_exported_file_exists(exported_file):
    time_to_wait = 15
    time_counter = 0
    while not os.path.exists(exported_file):
        time.sleep(0.1)
        time_counter += 0.1
        if time_counter > time_to_wait:
            raise FileNotFoundError(exported_file)


def check_table_rows_number(driver, table_id, expected_rows_num):
    actual_rows_num = driver.find_elements(f"div[id='{table_id}'] tbody tr")
    assert_that(
        len(actual_rows_num),
        equal_to(expected_rows_num),
        reason=f"Rows number is '{actual_rows_num}', but expected number is '{expected_rows_num}'",
    )


def check_table_ag_grid_rows_number(driver, table_id, expected_rows_num):
    actual_rows_num = driver.find_elements(
        f"div[id='{table_id}'] div[class='ag-center-cols-container'] div[role='row']"
    )
    assert_that(
        len(actual_rows_num),
        equal_to(expected_rows_num),
        reason=f"Rows number is '{actual_rows_num}', but expected number is '{expected_rows_num}'",
    )
