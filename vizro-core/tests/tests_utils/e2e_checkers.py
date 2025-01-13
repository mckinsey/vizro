import e2e_constants as cnst
from e2e_helpers import graph_load_waiter, webdriver_waiter
from e2e_paths import accordion_path
from hamcrest import any_of, assert_that, contains_string, equal_to
from selenium.webdriver.common.by import By
from selenium.webdriver.support.color import Color


def check_text(driver, xpath, text):
    webdriver_waiter(driver, xpath)
    elem = driver.find_element(By.XPATH, xpath)
    assert_that(
        elem.text,
        equal_to(text),
        reason=f"Element text is '{elem.text}', but expected text is '{text}'",
    )


def browser_console_warnings_checker(log_level, log_levels):
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
    webdriver_waiter(driver, f'//*[@id="{graph_id}"][@data-dash-is-loading="true"]')
    graph_load_waiter(driver, graph_id)


def check_range_slider_value(driver, left_num, right_num, elem_id=None):
    def _check_func(num, index):
        xpath = f'//*[@id="{elem_id}"]/..//*[@class="dash-input slider-text-input-field"][{index}]'
        value = driver.find_element(
            By.XPATH,
            xpath,
        ).get_attribute("value")
        assert_that(
            value,
            equal_to(num),
            reason=f"Element number is '{value}', but expected number is '{num}'",
        )

    _check_func(num=left_num, index=1)
    _check_func(num=right_num, index=2)


def check_slider_value(driver, num, elem_id):
    xpath = f'//*[@id="{elem_id}"]/..//*[@class="dash-input slider-text-input-field"]'
    value = driver.find_element(
        By.XPATH,
        xpath,
    ).get_attribute("value")
    assert_that(
        value,
        equal_to(num),
        reason=f"Element number is '{value}', but expected number is '{num}'",
    )


def check_accordion(driver, accordion_name):
    webdriver_waiter(driver, accordion_path(accordion_name))
    webdriver_waiter(driver, f'//*{accordion_path(accordion_name)}[@aria-expanded="true"]')


def check_theme_color(driver, color):
    webdriver_waiter(driver, f'//*[@data-bs-theme="{color}"]')


def check_ag_grid_theme_color(driver, ag_grid_id, color):
    webdriver_waiter(driver, f'//*[@id="__input_{ag_grid_id}"][@class="{color}"]')


def check_graph_color(driver, xpath, style_background, color):
    webdriver_waiter(driver, f'{xpath}[@style="{style_background}"]')
    rgb = webdriver_waiter(driver, xpath).value_of_css_property("background-color")
    graph_color = Color.from_string(rgb).hex
    assert_that(
        graph_color,
        equal_to(color),
        reason=f"Graph color is '{graph_color}', but expected color is '{color}'",
    )
