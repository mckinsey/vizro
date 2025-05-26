import pytest
from e2e.asserts import assert_files_equal
from e2e.vizro import constants as cnst
from e2e.vizro.checkers import (
    check_exported_file_exists,
    check_graph_color,
    check_graph_color_selenium,
    check_graph_is_loading,
    check_graph_is_loading_selenium,
    check_theme_color,
)
from e2e.vizro.navigation import page_select, page_select_selenium
from e2e.vizro.paths import button_path, categorical_components_value_path, slider_value_path, theme_toggle_path
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


@pytest.mark.flaky(reruns=5)
def test_parameters_title(chrome_driver, dash_br):
    """Tests that graph title is changing by parameter independently for every user."""
    # select parameters page for the first user
    page_select_selenium(
        chrome_driver,
        page_path=cnst.PARAMETERS_PAGE_PATH,
        page_name=cnst.PARAMETERS_PAGE,
    )

    # select parameters page for the second user
    page_select(
        dash_br,
        page_path=cnst.PARAMETERS_PAGE_PATH,
        page_name=cnst.PARAMETERS_PAGE,
    )

    # set bar graph title for the first user as 'red'
    WebDriverWait(chrome_driver, cnst.SELENIUM_WAITERS_TIMEOUT).until(
        expected_conditions.element_to_be_clickable(
            (By.CSS_SELECTOR, categorical_components_value_path(elem_id=cnst.RADIO_ITEMS_PARAMETERS_ONE, value=1))
        )
    ).click()
    check_graph_is_loading_selenium(chrome_driver, graph_id=cnst.BAR_GRAPH_ID)
    WebDriverWait(chrome_driver, cnst.SELENIUM_WAITERS_TIMEOUT).until(
        expected_conditions.text_to_be_present_in_element((By.CSS_SELECTOR, ".gtitle"), "red")
    )

    # change slider value from the second user and check that bar graph title is default ('blue')
    dash_br.multiple_click(slider_value_path(elem_id=cnst.SLIDER_PARAMETERS, value=3), 1)
    check_graph_is_loading(dash_br, graph_id=cnst.BAR_GRAPH_ID)
    dash_br.wait_for_text_to_equal(".gtitle", "blue")


def test_theme_color(chrome_driver, dash_br):
    """Tests that theme color is changing independently for every user."""
    # select parameters page for the first user
    page_select_selenium(
        chrome_driver,
        page_path=cnst.PARAMETERS_PAGE_PATH,
        page_name=cnst.PARAMETERS_PAGE,
    )

    # select parameters page for the second user
    page_select(
        dash_br,
        page_path=cnst.PARAMETERS_PAGE_PATH,
        page_name=cnst.PARAMETERS_PAGE,
    )

    # change theme to dark for the first user
    WebDriverWait(chrome_driver, cnst.SELENIUM_WAITERS_TIMEOUT).until(
        expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, theme_toggle_path()))
    ).click()
    check_graph_color_selenium(chrome_driver, style_background=cnst.STYLE_TRANSPARENT, color=cnst.RGBA_TRANSPARENT)
    WebDriverWait(chrome_driver, cnst.SELENIUM_WAITERS_TIMEOUT).until(
        expected_conditions.presence_of_element_located((By.CSS_SELECTOR, f"html[data-bs-theme='{cnst.THEME_DARK}']"))
    )

    # change slider value for the second user and check that theme is default ('light')
    dash_br.multiple_click(slider_value_path(elem_id=cnst.SLIDER_PARAMETERS, value=3), 1)
    check_graph_is_loading(dash_br, graph_id=cnst.BAR_GRAPH_ID)
    check_graph_color(dash_br, style_background=cnst.STYLE_TRANSPARENT, color=cnst.RGBA_TRANSPARENT)
    check_theme_color(dash_br, color=cnst.THEME_LIGHT)


def test_export_action(chrome_driver, dash_br):
    """Tests that export action is giving different results according to what every user filters."""
    # select filters page for the first user
    page_select_selenium(
        chrome_driver,
        page_path=cnst.FILTERS_PAGE_PATH,
        page_name=cnst.FILTERS_PAGE,
    )

    # select filters page for the second user
    page_select(
        dash_br,
        page_path=cnst.FILTERS_PAGE_PATH,
        page_name=cnst.FILTERS_PAGE,
    )

    # change slider values for scatter graph for the first user
    WebDriverWait(chrome_driver, cnst.SELENIUM_WAITERS_TIMEOUT).until(
        expected_conditions.element_to_be_clickable(
            (By.CSS_SELECTOR, slider_value_path(elem_id=cnst.SLIDER_FILTER_FILTERS_PAGE, value=3))
        )
    ).click()
    check_graph_is_loading_selenium(chrome_driver, graph_id=cnst.SCATTER_GRAPH_ID)

    # export scatter data for the second user without changing anything and check if data is correct
    dash_br.multiple_click(button_path(), 1)
    check_exported_file_exists(f"{dash_br.download_path}/{cnst.FILTERED_CSV}")
    check_exported_file_exists(f"{dash_br.download_path}/{cnst.FILTERED_XLSX}")
    assert_files_equal(cnst.FILTERED_BASE_CSV, f"{dash_br.download_path}/{cnst.FILTERED_CSV}")
