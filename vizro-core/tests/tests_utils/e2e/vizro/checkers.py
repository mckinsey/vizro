import os
import time
from collections import Counter
from datetime import datetime

import e2e.vizro.constants as cnst
from e2e.vizro.paths import (
    categorical_components_value_name_path,
    categorical_components_value_path,
    dropdown_id_path,
    graph_axis_value_path,
    select_all_path,
    table_ag_grid_cell_path_by_row,
)
from e2e.vizro.waiters import graph_load_waiter_selenium
from hamcrest import any_of, assert_that, contains_string, equal_to, greater_than_or_equal_to, less_than_or_equal_to
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.color import Color
from selenium.webdriver.support.wait import WebDriverWait


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


def check_graph_is_loading_selenium(driver, graph_id, timeout=cnst.SELENIUM_WAITERS_TIMEOUT):
    """Waiting for graph to start reloading for pure selenium."""
    WebDriverWait(driver, timeout).until(
        expected_conditions.presence_of_element_located(
            (By.CSS_SELECTOR, f"div[id='{graph_id}'][data-dash-is-loading='true']")
        )
    )
    graph_load_waiter_selenium(driver, graph_id, timeout)


def check_graph_is_empty(driver, graph_id):
    driver.wait_for_text_to_equal(
        graph_axis_value_path(
            graph_id=graph_id,
            axis="y",
            tick_index="1",
            value="−1",  # noqa: RUF001
        ),
        "−1",  # noqa: RUF001
    )


def check_graph_y_axis_value(driver, graph_id, tick_index, value):
    driver.wait_for_text_to_equal(
        graph_axis_value_path(
            graph_id=graph_id,
            axis="y",
            tick_index=tick_index,
            value=value,
        ),
        value,
    )


def check_graph_x_axis_value(driver, graph_id, tick_index, value):
    driver.wait_for_text_to_equal(
        graph_axis_value_path(
            graph_id=graph_id,
            axis="x",
            tick_index=tick_index,
            value=value,
        ),
        value,
    )


def check_slider_value(driver, elem_id, expected_max_value):
    driver.wait_for_element(f"div[id='{elem_id}'] span[aria-valuenow='{expected_max_value}']")


def check_range_slider_value(driver, elem_id, expected_min_value=None, expected_max_value=None):
    if expected_min_value:
        driver.wait_for_element(f"div[id='{elem_id}'] span[aria-valuenow='{expected_min_value}'][aria-label='Minimum']")
    else:
        driver.wait_for_element(f"div[id='{elem_id}'] span[aria-valuenow='{expected_max_value}'][aria-label='Maximum']")


def check_date_picker_value(driver, elem_id, expected_date_value):
    driver.wait_for_text_to_equal(f'button[id="{elem_id}"]', expected_date_value)


def check_range_date_picker_value(driver, elem_id, expected_min_date_value=None, expected_max_date_value=None):
    driver.wait_for_text_to_equal(
        f'button[id="{elem_id}"]',
        f"{expected_min_date_value} – {expected_max_date_value}",  # noqa: RUF001
    )


def check_time_picker_value(driver, elem_id, expected_hour, expected_minute):
    """Checks that a single dmc.TimePicker displays the expected hour and minute.

    Args:
        driver: dash_br fixture.
        elem_id: id of the TimePicker wrapper (without -start/-end suffix).
        expected_hour: two-digit hour string shown in the first input field.
        expected_minute: two-digit minute string shown in the second input field.
    """
    timeout = cnst.SELENIUM_WAITERS_TIMEOUT
    poll_interval = 0.2
    elapsed = 0
    while elapsed < timeout:
        fields = driver.find_elements(f"div[id='{elem_id}'] input.mantine-TimePicker-field")
        if (
            len(fields) >= 2
            and fields[0].get_attribute("value") == expected_hour
            and fields[1].get_attribute("value") == expected_minute
        ):
            return
        time.sleep(poll_interval)
        elapsed += poll_interval
    raise TimeoutError(
        f"TimePicker '{elem_id}' value did not become {expected_hour}:{expected_minute} within {timeout}s"
    )


def check_range_time_picker_value(driver, elem_id, start_hour, start_minute, end_hour, end_minute):
    """Checks that a range TimePicker displays the expected start and end times.

    Args:
        driver: dash_br fixture.
        elem_id: id of the range TimePicker (dcc.Store id, without -start/-end suffix).
        start_hour: two-digit hour string for the "From" input.
        start_minute: two-digit minute string for the "From" input.
        end_hour: two-digit hour string for the "To" input.
        end_minute: two-digit minute string for the "To" input.
    """
    check_time_picker_value(driver, f"{elem_id}-start", start_hour, start_minute)
    check_time_picker_value(driver, f"{elem_id}-end", end_hour, end_minute)


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


def check_graph_color_selenium(driver, style_background, color, timeout=cnst.SELENIUM_WAITERS_TIMEOUT):
    rgba = (
        WebDriverWait(driver, timeout)
        .until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, f"svg[style='{style_background}']")))
        .value_of_css_property("background-color")
    )
    graph_color = Color.from_string(rgba).rgba
    assert_that(
        graph_color,
        equal_to(color),
        reason=f"Graph color is '{graph_color}', but expected color is '{color}'",
    )


def check_selected_categorical_component(
    driver, component_id, options_value_status, select_all_status=False, checklist=False
):
    """Checks what selected and what is not for checklist and radio items.

    Args:
        driver: dash_br fixture
        component_id: id of checklist or radio items
        options_value_status: list of dicts with the next syntax
        select_all_status: value of Select All option, 'False' by default
        checklist: to have logic for 'Select All'
            [{
                "value": int, number of the value inside dom structure,
                "selected": bool, checks if value selected or not,
                "value_name": str, component value name,
            }]
    """
    if checklist:
        timeout = 2
        poll_interval = 0.1
        elapsed = 0
        select_all = driver.find_element(select_all_path(elem_id=component_id))
        while select_all.is_selected() != select_all_status and elapsed < timeout:
            time.sleep(poll_interval)
            elapsed += poll_interval
        assert_that(select_all.is_selected(), equal_to(select_all_status))
    values = driver.find_elements(f"div[id='{component_id}'] div[class^='form-check']")
    assert_that(len(values), equal_to(len(options_value_status)))
    for option in options_value_status:
        driver.wait_for_text_to_equal(
            categorical_components_value_name_path(elem_id=component_id, value=option["value"]), option["value_name"]
        )
        status = driver.find_element(categorical_components_value_path(elem_id=component_id, value=option["value"]))
        assert_that(status.is_selected(), equal_to(option["selected"]))


def check_selected_dropdown(
    driver, dropdown_id, expected_selected_options, expected_unselected_options=None, multi=True
):
    # if dropdown is closed, open it to avoid errors with values checking
    if driver.find_elements(f"{dropdown_id_path(dropdown_id)}[aria-expanded='false']"):
        driver.multiple_click(dropdown_id_path(dropdown_id), 1)
    if multi:
        selected_options = driver.find_elements(
            f"{dropdown_id_path(dropdown_id)} + div "
            "label[class='dash-options-list-option selected dash-dropdown-option'] "
            ".dash-options-list-option-text span"
        )
    else:
        selected_options = driver.find_elements(f"{dropdown_id_path(dropdown_id)} .dash-dropdown-value-item span")

    # creating list of selected options
    selected_options_list = ["".join(option.text.split()) for option in selected_options]
    # comparing selected options with expected
    assert_that(selected_options_list, equal_to(expected_selected_options))

    if expected_unselected_options:
        unselected_options = driver.find_elements(
            f"{dropdown_id_path(dropdown_id)} + div "
            f"label[class='dash-options-list-option dash-dropdown-option'] "
            f".dash-options-list-option-text span"
        )
        unselected_options_list = ["".join(option.text.split()) for option in unselected_options]
        assert_that(unselected_options_list, equal_to(expected_unselected_options))


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


def _parse_ag_grid_cell_time(text, col_id):
    """Parse a time-of-day from an AgGrid cell display string.

    datetime_utc cells contain full ISO timestamps; time columns use hh:mm:ss[.ffffff].
    """
    if col_id == "datetime_utc":
        cell_time = datetime.fromisoformat(text)
        return cell_time.hour, cell_time.minute, cell_time.second
    time_str = text.split(".")[0]
    hour, minute, second = (int(part) for part in time_str.split(":"))
    return hour, minute, second


def _time_to_seconds(hour, minute, second=0):
    """Convert hour, minute, and second to total seconds since midnight."""
    return hour * 3600 + minute * 60 + second


def _parse_time_hh_mm(time_str):
    """Parse an 'HH:MM' string into hour and minute integers."""
    hour, minute = (int(part) for part in time_str.split(":"))
    return hour, minute


def check_table_ag_grid_time_values_in_range(driver, table_id, col_id, start_time, end_time):
    """Checks that all visible AgGrid rows have time values within the given range (inclusive).

    The end minute is treated as inclusive up to :59 seconds (e.g. 10:44 means <= 10:44:59).

    Args:
        driver: dash_br fixture.
        table_id: id of the AgGrid component.
        col_id: column id to read from each row (e.g. "time_hh_mm_ss", "datetime_utc").
        start_time: range lower bound as "HH:MM".
        end_time: range upper bound as "HH:MM".
    """
    rows = driver.find_elements(f"div[id='{table_id}'] div[class='ag-center-cols-container'] div[row-index]")
    start_hour, start_minute = _parse_time_hh_mm(start_time)
    end_hour, end_minute = _parse_time_hh_mm(end_time)
    start_seconds = _time_to_seconds(start_hour, start_minute)
    end_seconds = _time_to_seconds(end_hour, end_minute, 59)
    for row in rows:
        row_index = row.get_attribute("row-index")
        cell_text = driver.find_element(
            table_ag_grid_cell_path_by_row(table_id, row_index=row_index, col_id=col_id)
        ).text
        hour, minute, second = _parse_ag_grid_cell_time(cell_text, col_id)
        cell_seconds = _time_to_seconds(hour, minute, second)
        assert_that(
            cell_seconds,
            greater_than_or_equal_to(start_seconds),
            reason=f"Row {row_index} value '{cell_text}' is before {start_time}",
        )
        assert_that(
            cell_seconds,
            less_than_or_equal_to(end_seconds),
            reason=f"Row {row_index} value '{cell_text}' is after {end_time}",
        )


def check_table_ag_grid_time_values_equal(driver, table_id, col_id, time):
    """Checks that all visible AgGrid rows match the given hour and minute (seconds may differ).

    Args:
        driver: dash_br fixture.
        table_id: id of the AgGrid component.
        col_id: column id to read from each row.
        time: expected time as "HH:MM".
    """
    rows = driver.find_elements(f"div[id='{table_id}'] div[class='ag-center-cols-container'] div[row-index]")
    expected_hour, expected_minute = _parse_time_hh_mm(time)
    for row in rows:
        row_index = row.get_attribute("row-index")
        cell_text = driver.find_element(
            table_ag_grid_cell_path_by_row(table_id, row_index=row_index, col_id=col_id)
        ).text
        cell_hour, cell_minute, _ = _parse_ag_grid_cell_time(cell_text, col_id)
        assert_that(
            (cell_hour, cell_minute),
            equal_to((expected_hour, expected_minute)),
            reason=f"Row {row_index} value '{cell_text}' does not match {time}",
        )


def check_http_requests_count(
    page, http_requests_paths, requests_number, sleep=cnst.HTTP_TIMEOUT_SHORT, url_path="_dash-update-component"
):
    page.wait_for_timeout(sleep)
    # http_requests_paths now contains "_dash-update-component" paths with query parameters such as "?endId=..."
    counts = Counter(path.split("?")[0] for path in http_requests_paths)
    assert_that(
        counts[url_path],
        equal_to(requests_number),
        reason=f"'{url_path}' requests should be equal to {requests_number}",
    )
