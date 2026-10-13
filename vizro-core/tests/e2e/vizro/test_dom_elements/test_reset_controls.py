import e2e.vizro.constants as cnst
from e2e.vizro.checkers import (
    check_cascader_trigger_value,
    check_empty_time_picker_value,
    check_range_date_picker_value,
    check_range_datetime_picker_value,
    check_range_slider_value,
    check_range_time_picker_value,
    check_selected_categorical_component,
    check_selected_dropdown,
    check_slider_value,
    check_table_ag_grid_column_values,
    check_table_ag_grid_rows_number,
)
from e2e.vizro.navigation import (
    accordion_select,
    clear_dropdown,
    hover_over_element_by_xpath_selenium,
    page_select,
    select_cascader_path,
    select_dropdown_select_all,
    select_dropdown_value,
    select_range_datetime_picker_value,
    select_range_time_picker_value,
    select_slider_value,
)
from e2e.vizro.paths import (
    categorical_components_value_path,
    dropdown_id_path,
    switch_path_using_filter_control_id,
)
from hamcrest import assert_that, equal_to


def test_reset_controls_tooltip(dash_br):
    page_select(
        dash_br, page_path=cnst.FILTERS_INSIDE_CONTAINERS_PAGE_PATH, page_name=cnst.FILTERS_INSIDE_CONTAINERS_PAGE
    )
    # hover over reset controls icon and wait for the tooltip appear
    hover_over_element_by_xpath_selenium(dash_br.driver, "//*[contains(@id, 'reset-button')]")
    dash_br.wait_for_text_to_equal(".tooltip-inner", "Reset all page controls")


def test_reset_controls_header(dash_br):
    page_select(
        dash_br, page_path=cnst.FILTERS_INSIDE_CONTAINERS_PAGE_PATH, page_name=cnst.FILTERS_INSIDE_CONTAINERS_PAGE
    )
    # change all controls on the page
    # dropdown change from ["setosa", "versicolor", "virginical"] to ["setosa"]
    clear_dropdown(dash_br, cnst.DROPDOWN_INSIDE_CONTAINERS)
    select_dropdown_value(dash_br, dropdown_id=cnst.DROPDOWN_INSIDE_CONTAINERS, value="setosa")
    # checklist change from ["SelectAll", "setosa", "versicolor", "virginical"] to ["setosa", "virginica"]
    dash_br.multiple_click(categorical_components_value_path(elem_id=cnst.CHECK_LIST_INSIDE_CONTAINERS, value=2), 1)
    # radioitems change from "setosa" to "versicolor"
    dash_br.multiple_click(categorical_components_value_path(elem_id=cnst.RADIO_ITEMS_INSIDE_CONTAINERS, value=2), 1)
    # slider change from "0.1" to "1.1"
    select_slider_value(dash_br, elem_id=cnst.SLIDER_INSIDE_CONTAINERS, max_value="1.1")
    # range_slider change from "4.3 - 7.9" to "4.3 - 7"
    select_slider_value(dash_br, elem_id=cnst.RANGE_SLIDER_INSIDE_CONTAINERS, max_value="7.3")
    # date_picker change from "2024/01/01 - 2024/05/29" to "2024/01/10 - 2024/01/26"
    dash_br.multiple_click(f'button[id="{cnst.RANGE_DATEPICKER_INSIDE_CONTAINERS}"]', 1)
    dash_br.wait_for_element('div[data-calendar="true"]')
    dash_br.multiple_click('button[aria-label="10 January 2024"]', 1)
    dash_br.multiple_click('button[aria-label="26 January 2024"]', 1)
    # switch change from "On" to "Off"
    dash_br.multiple_click(switch_path_using_filter_control_id(filter_control_id=cnst.SWITCH_INSIDE_CONTAINERS), 1)

    # click reset controls icon
    dash_br.multiple_click("button[id$='reset-button']", 1, delay=0.1)

    # check all controls were reset
    # dropdown
    check_selected_dropdown(
        dash_br,
        dropdown_id=cnst.DROPDOWN_INSIDE_CONTAINERS,
        expected_selected_options=["setosa", "versicolor", "virginica"],
        expected_unselected_options=[],
    )
    # close dropdown to avoid errors with checking other controls
    dash_br.multiple_click(dropdown_id_path(dropdown_id=cnst.DROPDOWN_INSIDE_CONTAINERS), 1)
    # checklist
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.CHECK_LIST_INSIDE_CONTAINERS,
        select_all_status=True,
        checklist=True,
        options_value_status=[
            {"value": 1, "selected": True, "value_name": "setosa"},
            {"value": 2, "selected": True, "value_name": "versicolor"},
            {"value": 3, "selected": True, "value_name": "virginica"},
        ],
    )
    # radioitems
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.RADIO_ITEMS_INSIDE_CONTAINERS,
        options_value_status=[
            {"value": 1, "selected": True, "value_name": "setosa"},
            {"value": 2, "selected": False, "value_name": "versicolor"},
            {"value": 3, "selected": False, "value_name": "virginica"},
        ],
    )
    # slider
    check_slider_value(dash_br, expected_max_value="0.1", elem_id=cnst.SLIDER_INSIDE_CONTAINERS)
    # range_slider
    check_range_slider_value(
        dash_br, elem_id=cnst.RANGE_SLIDER_INSIDE_CONTAINERS, expected_min_value="4.3", expected_max_value="7.9"
    )
    # date_picker
    check_range_date_picker_value(
        dash_br,
        elem_id=cnst.RANGE_DATEPICKER_INSIDE_CONTAINERS,
        expected_min_date_value="2024/01/01",
        expected_max_date_value="2024/05/29",
    )
    # switch
    status = dash_br.find_element(categorical_components_value_path(elem_id=cnst.SWITCH_INSIDE_CONTAINERS, value=1))
    assert_that(status.is_selected(), equal_to(True))


def test_reset_controls_page(dash_br):
    accordion_select(dash_br, accordion_name=cnst.AG_GRID_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.TABLE_AG_GRID_INTERACTIONS_PAGE,
    )
    # change all controls on the page
    # dropdown change from "2007" to "Select All"
    select_dropdown_select_all(dash_br, dropdown_id=cnst.DROPDOWN_AG_GRID_INTERACTIONS_ID)
    # close dropdown to avoid errors with checking other controls
    dash_br.multiple_click(dropdown_id_path(dropdown_id=cnst.DROPDOWN_AG_GRID_INTERACTIONS_ID), 1)
    # radioitems change from "Europe" to "Africa"
    dash_br.multiple_click(
        categorical_components_value_path(elem_id=cnst.RADIOITEMS_AG_GRID_INTERACTIONS_ID, value=2), 1
    )

    # click reset controls button
    dash_br.multiple_click("button[id$='reset-button']", 1, delay=0.1)

    # check all controls were reset
    # dropdown
    check_selected_dropdown(
        dash_br,
        dropdown_id=cnst.DROPDOWN_AG_GRID_INTERACTIONS_ID,
        expected_selected_options=["2007"],
        expected_unselected_options=[
            "1952",
            "1957",
            "1962",
            "1967",
            "1972",
            "1977",
            "1982",
            "1987",
            "1992",
            "1997",
            "2002",
        ],
    )
    # close dropdown to avoid errors with checking other controls
    dash_br.multiple_click(dropdown_id_path(dropdown_id=cnst.DROPDOWN_AG_GRID_INTERACTIONS_ID), 1)
    # radioitems
    check_selected_categorical_component(
        dash_br,
        component_id=cnst.RADIOITEMS_AG_GRID_INTERACTIONS_ID,
        options_value_status=[
            {"value": 1, "selected": True, "value_name": "Europe"},
            {"value": 2, "selected": False, "value_name": "Africa"},
            {"value": 3, "selected": False, "value_name": "Americas"},
        ],
    )


def test_reset_controls_timepicker(dash_br):
    accordion_select(dash_br, accordion_name=cnst.DATEPICKER_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.TIMEPICKER_RANGE_PAGE,
        page_path=cnst.TIMEPICKER_RANGE_PAGE_PATH,
        graph_check=False,
    )

    select_range_time_picker_value(
        dash_br,
        elem_id=cnst.TIMEPICKER_TIME_HH_MM_SS_RANGE_ID,
        start_hour="10",
        start_minute="43",
        end_hour="10",
        end_minute="44",
    )
    check_range_time_picker_value(
        dash_br,
        elem_id=cnst.TIMEPICKER_TIME_HH_MM_SS_RANGE_ID,
        start_hour="10",
        start_minute="43",
        end_hour="10",
        end_minute="44",
    )

    dash_br.multiple_click("button[id$='reset-button']", 1, delay=0.1)

    check_empty_time_picker_value(dash_br, f"{cnst.TIMEPICKER_TIME_HH_MM_SS_RANGE_ID}-start")
    check_empty_time_picker_value(dash_br, f"{cnst.TIMEPICKER_TIME_HH_MM_SS_RANGE_ID}-end")


def test_reset_controls_datetimepicker(dash_br):
    accordion_select(dash_br, accordion_name=cnst.DATEPICKER_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.DATETIMEPICKER_RANGE_PAGE,
        page_path=cnst.DATETIMEPICKER_RANGE_PAGE_PATH,
        graph_check=False,
    )

    # dynamic DateTimePicker defaults to the column min/max date range
    default_range = (("Jan 3, 2026", None, None), ("Dec 29, 2026", None, None))
    check_range_datetime_picker_value(
        dash_br,
        elem_id=cnst.DATETIMEPICKER_DATETIME_UTC_RANGE_ID,
        start=default_range[0],
        end=default_range[1],
    )

    select_range_datetime_picker_value(
        dash_br,
        elem_id=cnst.DATETIMEPICKER_DATETIME_UTC_RANGE_ID,
        start=("2026-06-10", "04", "34"),
        end=("2026-06-11", "20", "18"),
    )
    check_range_datetime_picker_value(
        dash_br,
        elem_id=cnst.DATETIMEPICKER_DATETIME_UTC_RANGE_ID,
        start=("Jun 10, 2026", "04", "34"),
        end=("Jun 11, 2026", "20", "18"),
    )

    dash_br.multiple_click("button[id$='reset-button']", 1, delay=0.1)

    check_range_datetime_picker_value(
        dash_br,
        elem_id=cnst.DATETIMEPICKER_DATETIME_UTC_RANGE_ID,
        start=default_range[0],
        end=default_range[1],
    )


def test_reset_controls_cascader(dash_br):
    accordion_select(dash_br, accordion_name=cnst.CASCADER_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.CASCADER_LEAF_PAGE,
        page_path=cnst.CASCADER_LEAF_PAGE_PATH,
        graph_check=False,
    )

    select_cascader_path(
        dash_br,
        cnst.CASCADER_LEAF_ID,
        ["Asia", "South", "China"],
        multi=False,
    )
    check_cascader_trigger_value(dash_br, cnst.CASCADER_LEAF_ID, "China")

    dash_br.multiple_click("button[id$='reset-button']", 1, delay=0.1)

    check_cascader_trigger_value(dash_br, cnst.CASCADER_LEAF_ID, "United States")
    check_table_ag_grid_rows_number(dash_br, table_id=cnst.CASCADER_LEAF_AG_GRID_ID, expected_rows_num=1)
    check_table_ag_grid_column_values(
        dash_br, table_id=cnst.CASCADER_LEAF_AG_GRID_ID, col_id="country", expected_values=["United States"]
    )
