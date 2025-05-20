import pytest
from e2e.vizro import constants as cnst
from e2e.vizro.navigation import (
    accordion_select,
    hover_over_element_by_xpath_selenium,
    page_select,
)


@pytest.mark.parametrize(
    "dash_br_driver, icon, tooltip_text",
    [
        ({"port": cnst.DEFAULT_PORT}, cnst.DROPDOWN_TOOLTIP_ICON, cnst.DROPDOWN_TOOLTIP_TEXT),
        ({"port": cnst.DEFAULT_PORT}, cnst.RADIOITEMS_TOOLTIP_ICON, cnst.RADIOITEMS_TOOLTIP_TEXT),
        ({"port": cnst.DEFAULT_PORT}, cnst.CHECKLIST_TOOLTIP_ICON, cnst.CHECKLIST_TOOLTIP_TEXT),
        ({"port": cnst.DEFAULT_PORT}, cnst.SLIDER_TOOLTIP_ICON, cnst.SLIDER_TOOLTIP_TEXT),
        ({"port": cnst.DEFAULT_PORT}, cnst.RANGESLIDER_TOOLTIP_ICON, cnst.RANGESLIDER_TOOLTIP_TEXT),
        ({"port": cnst.DEFAULT_PORT}, cnst.DATEPICKER_TOOLTIP_ICON, cnst.DATEPICKER_TOOLTIP_TEXT),
    ],
    ids=["Dropdown", "RadioItems", "Checklist", "Slider", "RangeSlider", "Datepicker"],
    indirect=["dash_br_driver"],
)
def test_controls_tooltip_and_icon(dash_br_driver, icon, tooltip_text):
    accordion_select(dash_br_driver, accordion_name=cnst.LAYOUT_ACCORDION)
    page_select(dash_br_driver, page_name=cnst.EXTRAS_PAGE)

    # open datepicker calendar and close it to scroll to the end of the page
    dash_br_driver.multiple_click("button[class*='DatePickerInput']", 2)
    dash_br_driver.wait_for_no_elements('div[data-calendar="true"]')

    # hover over dropdown icon and wait for the tooltip appear
    hover_over_element_by_xpath_selenium(
        dash_br_driver, f"//*[@class='material-symbols-outlined tooltip-icon'][text()='{icon}']"
    )
    dash_br_driver.wait_for_text_to_equal(".tooltip-inner p", tooltip_text)


@pytest.mark.parametrize(
    "dash_br_driver, icon, tooltip_text",
    [
        ({"port": cnst.DEFAULT_PORT}, cnst.PAGE_TOOLTIP_ICON, cnst.PAGE_TOOLTIP_TEXT),
        ({"port": cnst.DEFAULT_PORT}, cnst.CONTAINER_TOOLTIP_ICON, cnst.CONTAINER_TOOLTIP_TEXT),
        ({"port": cnst.DEFAULT_PORT}, cnst.GRAPH_TOOLTIP_ICON, cnst.GRAPH_TOOLTIP_TEXT),
    ],
    ids=["Page", "Container", "Graph"],
    indirect=["dash_br_driver"],
)
def test_components_tooltip_and_icon(dash_br_driver, icon, tooltip_text):
    accordion_select(dash_br_driver, accordion_name=cnst.LAYOUT_ACCORDION)
    page_select(dash_br_driver, page_name=cnst.EXTRAS_PAGE)

    # hover over dropdown icon and wait for the tooltip appear
    hover_over_element_by_xpath_selenium(
        dash_br_driver, f"//*[@class='material-symbols-outlined tooltip-icon'][text()='{icon}']"
    )
    dash_br_driver.wait_for_text_to_equal(".tooltip-inner p", tooltip_text)


@pytest.mark.parametrize(
    "dash_br_driver, accordion_name, page_name, icon, tooltip_text",
    [
        (
            {"port": cnst.DEFAULT_PORT},
            cnst.AG_GRID_ACCORDION,
            cnst.TABLE_PAGE,
            cnst.TABLE_TOOLTIP_ICON,
            cnst.TABLE_TOOLTIP_TEXT,
        ),
        (
            {"port": cnst.DEFAULT_PORT},
            cnst.AG_GRID_ACCORDION,
            cnst.TABLE_AG_GRID_PAGE,
            cnst.AG_GRID_TOOLTIP_ICON,
            cnst.AG_GRID_TOOLTIP_TEXT,
        ),
    ],
    ids=[
        "Table",
        "AgGrid",
    ],
    indirect=["dash_br_driver"],
)
def test_components_tooltip_and_icon_tables(dash_br_driver, accordion_name, page_name, icon, tooltip_text):
    accordion_select(dash_br_driver, accordion_name=accordion_name)
    page_select(dash_br_driver, page_name=page_name, graph_check=False)

    # hover over dropdown icon and wait for the tooltip appear
    hover_over_element_by_xpath_selenium(
        dash_br_driver, f"//*[@class='material-symbols-outlined tooltip-icon'][text()='{icon}']"
    )
    dash_br_driver.wait_for_text_to_equal(".tooltip-inner p", tooltip_text)


@pytest.mark.parametrize(
    "dash_br_driver",
    [
        ({"port": cnst.YAML_PORT}),
    ],
    indirect=["dash_br_driver"],
)
def test_dashboard_tooltip_and_icon(dash_br_driver):
    # hover over dropdown icon and wait for the tooltip appear
    hover_over_element_by_xpath_selenium(
        dash_br_driver, "//*[@class='material-symbols-outlined tooltip-icon'][text()='info']"
    )
    dash_br_driver.wait_for_text_to_equal(".tooltip-inner p", "dashboard tooltip")
