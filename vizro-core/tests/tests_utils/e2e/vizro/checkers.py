import e2e.vizro.constants as cnst
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
