import e2e.vizro.constants as cnst
from e2e.vizro.checkers import (
    check_range_time_picker_value,
    check_table_ag_grid_rows_number,
    check_table_ag_grid_time_values_equal,
    check_table_ag_grid_time_values_in_range,
    check_time_picker_value,
)
from e2e.vizro.navigation import accordion_select, page_select, select_time_picker_range_value, select_time_picker_value


def test_timepicker_range_time_hh_mm_ss(dash_br):
    """Tests that range TimePicker as filter works correctly for a time column."""
    accordion_select(dash_br, accordion_name=cnst.DATEPICKER_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.TIMEPICKER_RANGE_PAGE,
        page_path=cnst.TIMEPICKER_RANGE_PAGE_PATH,
    )

    # set time range 10:43-10:44 on the native time_hh_mm_ss column (2 matching rows in seeded dff)
    select_time_picker_range_value(
        dash_br,
        elem_id=cnst.TIMEPICKER_TIME_HH_MM_SS_RANGE_ID,
        start_hour="10",
        start_minute="43",
        end_hour="10",
        end_minute="44",
    )

    # check that both range inputs display the selected times
    check_range_time_picker_value(
        dash_br,
        elem_id=cnst.TIMEPICKER_TIME_HH_MM_SS_RANGE_ID,
        start_hour="10",
        start_minute="43",
        end_hour="10",
        end_minute="44",
    )
    # check that the ag grid shows exactly the filtered rows
    check_table_ag_grid_rows_number(dash_br, table_id=cnst.TIMEPICKER_RANGE_AG_GRID_ID, expected_rows_num=2)
    # check that every visible cell in time_hh_mm_ss falls within the selected range
    check_table_ag_grid_time_values_in_range(
        dash_br,
        table_id=cnst.TIMEPICKER_RANGE_AG_GRID_ID,
        col_id="time_hh_mm_ss",
        start_time="10:43",
        end_time="10:44",
    )


def test_timepicker_range_datetime_utc_time(dash_br):
    """Tests that range TimePicker filters datetime column by time-of-day."""
    accordion_select(dash_br, accordion_name=cnst.DATEPICKER_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.TIMEPICKER_RANGE_PAGE,
        page_path=cnst.TIMEPICKER_RANGE_PAGE_PATH,
    )

    # filter datetime_utc by time-of-day only (ignores the calendar date component)
    select_time_picker_range_value(
        dash_br,
        elem_id=cnst.TIMEPICKER_DATETIME_UTC_TIME_RANGE_ID,
        start_hour="10",
        start_minute="43",
        end_hour="11",
        end_minute="00",
    )

    check_range_time_picker_value(
        dash_br,
        elem_id=cnst.TIMEPICKER_DATETIME_UTC_TIME_RANGE_ID,
        start_hour="10",
        start_minute="43",
        end_hour="11",
        end_minute="00",
    )
    check_table_ag_grid_rows_number(dash_br, table_id=cnst.TIMEPICKER_RANGE_AG_GRID_ID, expected_rows_num=2)
    # datetime_utc cells are ISO timestamps; checker extracts the time portion for comparison
    check_table_ag_grid_time_values_in_range(
        dash_br,
        table_id=cnst.TIMEPICKER_RANGE_AG_GRID_ID,
        col_id="datetime_utc",
        start_time="10:43",
        end_time="11:00",
    )


def test_timepicker_range_time_iso(dash_br):
    """Tests that range TimePicker as filter works correctly for a time_iso column."""
    accordion_select(dash_br, accordion_name=cnst.DATEPICKER_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.TIMEPICKER_RANGE_PAGE,
        page_path=cnst.TIMEPICKER_RANGE_PAGE_PATH,
    )

    # time_iso holds microsecond-precision times derived from datetime_utc
    select_time_picker_range_value(
        dash_br,
        elem_id=cnst.TIMEPICKER_TIME_ISO_RANGE_ID,
        start_hour="05",
        start_minute="54",
        end_hour="06",
        end_minute="00",
    )

    check_range_time_picker_value(
        dash_br,
        elem_id=cnst.TIMEPICKER_TIME_ISO_RANGE_ID,
        start_hour="05",
        start_minute="54",
        end_hour="06",
        end_minute="00",
    )
    check_table_ag_grid_rows_number(dash_br, table_id=cnst.TIMEPICKER_RANGE_AG_GRID_ID, expected_rows_num=3)
    check_table_ag_grid_time_values_in_range(
        dash_br,
        table_id=cnst.TIMEPICKER_RANGE_AG_GRID_ID,
        col_id="time_iso",
        start_time="05:54",
        end_time="06:00",
    )


def test_timepicker_single_time_hh_mm_ss(dash_br):
    """Tests that single TimePicker as filter works correctly for a time column."""
    accordion_select(dash_br, accordion_name=cnst.DATEPICKER_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.TIMEPICKER_SINGLE_PAGE,
        page_path=cnst.TIMEPICKER_SINGLE_PAGE_PATH,
    )

    # single-mode TimePicker matches rows where hour and minute equal the selection
    select_time_picker_value(
        dash_br,
        elem_id=cnst.TIMEPICKER_TIME_HH_MM_SS_SINGLE_ID,
        hour="10",
        minute="43",
    )

    check_time_picker_value(
        dash_br,
        elem_id=cnst.TIMEPICKER_TIME_HH_MM_SS_SINGLE_ID,
        expected_hour="10",
        expected_minute="43",
    )
    check_table_ag_grid_rows_number(dash_br, table_id=cnst.TIMEPICKER_SINGLE_AG_GRID_ID, expected_rows_num=2)
    check_table_ag_grid_time_values_equal(
        dash_br,
        table_id=cnst.TIMEPICKER_SINGLE_AG_GRID_ID,
        col_id="time_hh_mm_ss",
        time="10:43",
    )


def test_timepicker_single_datetime_utc_time(dash_br):
    """Tests that single TimePicker filters datetime column by time-of-day."""
    accordion_select(dash_br, accordion_name=cnst.DATEPICKER_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.TIMEPICKER_SINGLE_PAGE,
        page_path=cnst.TIMEPICKER_SINGLE_PAGE_PATH,
    )

    select_time_picker_value(
        dash_br,
        elem_id=cnst.TIMEPICKER_DATETIME_UTC_TIME_SINGLE_ID,
        hour="08",
        minute="28",
    )

    check_time_picker_value(
        dash_br,
        elem_id=cnst.TIMEPICKER_DATETIME_UTC_TIME_SINGLE_ID,
        expected_hour="08",
        expected_minute="28",
    )
    check_table_ag_grid_rows_number(dash_br, table_id=cnst.TIMEPICKER_SINGLE_AG_GRID_ID, expected_rows_num=3)
    check_table_ag_grid_time_values_equal(
        dash_br,
        table_id=cnst.TIMEPICKER_SINGLE_AG_GRID_ID,
        col_id="datetime_utc",
        time="08:28",
    )


def test_timepicker_single_time_iso(dash_br):
    """Tests that single TimePicker as filter works correctly for a time_iso column."""
    accordion_select(dash_br, accordion_name=cnst.DATEPICKER_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.TIMEPICKER_SINGLE_PAGE,
        page_path=cnst.TIMEPICKER_SINGLE_PAGE_PATH,
    )

    select_time_picker_value(
        dash_br,
        elem_id=cnst.TIMEPICKER_TIME_ISO_SINGLE_ID,
        hour="00",
        minute="19",
    )

    check_time_picker_value(
        dash_br,
        elem_id=cnst.TIMEPICKER_TIME_ISO_SINGLE_ID,
        expected_hour="00",
        expected_minute="19",
    )
    check_table_ag_grid_rows_number(dash_br, table_id=cnst.TIMEPICKER_SINGLE_AG_GRID_ID, expected_rows_num=3)
    check_table_ag_grid_time_values_equal(
        dash_br,
        table_id=cnst.TIMEPICKER_SINGLE_AG_GRID_ID,
        col_id="time_iso",
        time="00:19",
    )


def test_timepicker_parameter(dash_br):
    """Tests that single TimePicker as parameter updates the graph title."""
    accordion_select(dash_br, accordion_name=cnst.DATEPICKER_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.TIMEPICKER_PARAMETER_PAGE,
        page_path=cnst.TIMEPICKER_PARAMETER_PAGE_PATH,
    )

    # set time 10:43 via the parameter TimePicker
    select_time_picker_value(
        dash_br,
        elem_id=cnst.TIMEPICKER_PARAMETER_ID,
        hour="10",
        minute="43",
    )

    # parameter value is applied to scatter_chart.title
    dash_br.wait_for_text_to_equal(".gtitle", "10:43")
    check_time_picker_value(
        dash_br,
        elem_id=cnst.TIMEPICKER_PARAMETER_ID,
        expected_hour="10",
        expected_minute="43",
    )
