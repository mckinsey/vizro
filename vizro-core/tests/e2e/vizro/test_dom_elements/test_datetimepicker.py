import e2e.vizro.constants as cnst
import pytest
from e2e.vizro.checkers import (
    check_range_datetime_picker_value,
    check_single_datetime_picker_value,
    check_table_ag_grid_datetime_values_equal,
    check_table_ag_grid_datetime_values_in_range,
    check_table_ag_grid_rows_number,
)
from e2e.vizro.navigation import (
    accordion_select,
    page_select,
    select_range_datetime_picker_value,
    select_single_datetime_picker_value,
)


def test_datetimepicker_range_datetime_utc(dash_br):
    """Tests that range DateTimePicker as filter works correctly for a datetime_utc column."""
    accordion_select(dash_br, accordion_name=cnst.DATEPICKER_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.DATETIMEPICKER_RANGE_PAGE,
        page_path=cnst.DATETIMEPICKER_RANGE_PAGE_PATH,
        graph_check=False,
    )

    # set datetime range 2026-06-10T04:34-2026-06-11T20:18 on datetime_utc (2 matching rows in seeded dff;
    # end must extend past 2026-06-10T04:51 because filter compares full timestamps, not floored minutes)
    # also checking that value 2026-06-11T20:18:29.730804 is not included
    # because it is after the end of the range (2026-06-11T20:18:00)
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
    check_table_ag_grid_rows_number(dash_br, table_id=cnst.DATETIMEPICKER_RANGE_AG_GRID_ID, expected_rows_num=2)
    check_table_ag_grid_datetime_values_in_range(
        dash_br,
        table_id=cnst.DATETIMEPICKER_RANGE_AG_GRID_ID,
        col_id="datetime_utc",
        start_datetime="2026-06-10T04:34",
        end_datetime="2026-06-11T20:18",
    )


def test_datetimepicker_range_datetime_utc_three_rows(dash_br):
    """Tests that range DateTimePicker filters datetime_utc across a wider datetime window."""
    accordion_select(dash_br, accordion_name=cnst.DATEPICKER_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.DATETIMEPICKER_RANGE_PAGE,
        page_path=cnst.DATETIMEPICKER_RANGE_PAGE_PATH,
        graph_check=False,
    )

    # set datetime range 2026-10-14T02:56-2026-10-15T05:27 on datetime_utc (3 matching rows in seeded dff;
    # end must extend past 2026-10-14T21:55 because filter compares full timestamps, not floored minutes)
    # also checking that value 2026-10-15T05:27:26.381983 is not included
    # because it is after the end of the range (2026-10-15T05:27:00)
    select_range_datetime_picker_value(
        dash_br,
        elem_id=cnst.DATETIMEPICKER_DATETIME_UTC_RANGE_ID,
        start=("2026-10-14", "02", "56"),
        end=("2026-10-15", "05", "27"),
    )

    check_range_datetime_picker_value(
        dash_br,
        elem_id=cnst.DATETIMEPICKER_DATETIME_UTC_RANGE_ID,
        start=("Oct 14, 2026", "02", "56"),
        end=("Oct 15, 2026", "05", "27"),
    )
    check_table_ag_grid_rows_number(dash_br, table_id=cnst.DATETIMEPICKER_RANGE_AG_GRID_ID, expected_rows_num=3)
    check_table_ag_grid_datetime_values_in_range(
        dash_br,
        table_id=cnst.DATETIMEPICKER_RANGE_AG_GRID_ID,
        col_id="datetime_utc",
        start_datetime="2026-10-14T02:56",
        end_datetime="2026-10-15T05:27",
    )


@pytest.mark.parametrize(
    ("start", "end", "expected_start", "expected_end", "expected_rows", "start_datetime", "end_datetime"),
    [
        pytest.param(
            ("2026-06-10", None, None),
            ("2026-06-11", "20", "18"),
            ("Jun 10, 2026", None, None),
            ("Jun 11, 2026", "20", "18"),
            2,
            "2026-06-10T00:00",
            "2026-06-11T20:18",
            id="without_start_time",
        ),
        pytest.param(
            ("2026-06-10", "04", "34"),
            ("2026-06-11", None, None),
            ("Jun 10, 2026", "04", "34"),
            ("Jun 11, 2026", None, None),
            3,
            "2026-06-10T04:34",
            "2026-06-11T23:59",
            id="without_end_time",
        ),
        pytest.param(
            ("2026-06-10", None, None),
            ("2026-06-11", None, None),
            ("Jun 10, 2026", None, None),
            ("Jun 11, 2026", None, None),
            3,
            "2026-06-10T00:00",
            "2026-06-11T23:59",
            id="without_start_and_end_time",
        ),
    ],
)
def test_datetimepicker_range_date_only_time_filters_datetime_utc(  # noqa: PLR0917, PLR0913
    dash_br, start, end, expected_start, expected_end, expected_rows, start_datetime, end_datetime
):
    """Tests that cleared times widen the range to start/end of day while dates stay set."""
    accordion_select(dash_br, accordion_name=cnst.DATEPICKER_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.DATETIMEPICKER_RANGE_PAGE,
        page_path=cnst.DATETIMEPICKER_RANGE_PAGE_PATH,
        graph_check=False,
    )

    select_range_datetime_picker_value(
        dash_br,
        elem_id=cnst.DATETIMEPICKER_DATETIME_UTC_RANGE_ID,
        start=start,
        end=end,
    )

    check_range_datetime_picker_value(
        dash_br,
        elem_id=cnst.DATETIMEPICKER_DATETIME_UTC_RANGE_ID,
        start=expected_start,
        end=expected_end,
    )
    check_table_ag_grid_rows_number(
        dash_br, table_id=cnst.DATETIMEPICKER_RANGE_AG_GRID_ID, expected_rows_num=expected_rows
    )
    check_table_ag_grid_datetime_values_in_range(
        dash_br,
        table_id=cnst.DATETIMEPICKER_RANGE_AG_GRID_ID,
        col_id="datetime_utc",
        start_datetime=start_datetime,
        end_datetime=end_datetime,
    )


def test_datetimepicker_single_datetime_utc(dash_br):
    """Tests that single DateTimePicker as filter works correctly for a datetime_utc column."""
    accordion_select(dash_br, accordion_name=cnst.DATEPICKER_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.DATETIMEPICKER_SINGLE_PAGE,
        page_path=cnst.DATETIMEPICKER_SINGLE_PAGE_PATH,
        graph_check=False,
    )

    # single-mode DateTimePicker matches the exact datetime at minute precision (1 matching row in seeded dff)
    select_single_datetime_picker_value(
        dash_br,
        elem_id=cnst.DATETIMEPICKER_DATETIME_UTC_SINGLE_ID,
        iso_date="2026-03-14",
        hour="23",
        minute="11",
    )

    check_single_datetime_picker_value(
        dash_br,
        elem_id=cnst.DATETIMEPICKER_DATETIME_UTC_SINGLE_ID,
        expected_date_value="Mar 14, 2026",
        expected_hour="23",
        expected_minute="11",
    )
    check_table_ag_grid_rows_number(dash_br, table_id=cnst.DATETIMEPICKER_SINGLE_AG_GRID_ID, expected_rows_num=1)
    check_table_ag_grid_datetime_values_equal(
        dash_br,
        table_id=cnst.DATETIMEPICKER_SINGLE_AG_GRID_ID,
        col_id="datetime_utc",
        datetime_str="2026-03-14T23:11",
    )


def test_datetimepicker_parameter(dash_br):
    """Tests that single DateTimePicker as parameter updates the graph title."""
    accordion_select(dash_br, accordion_name=cnst.DATEPICKER_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.DATETIMEPICKER_PARAMETER_PAGE,
        page_path=cnst.DATETIMEPICKER_PARAMETER_PAGE_PATH,
    )

    select_single_datetime_picker_value(
        dash_br,
        elem_id=cnst.DATETIMEPICKER_PARAMETER_ID,
        iso_date="2026-01-15",
        hour="10",
        minute="43",
    )

    dash_br.wait_for_text_to_equal(".gtitle", "2026-01-15T10:43")
    check_single_datetime_picker_value(
        dash_br,
        elem_id=cnst.DATETIMEPICKER_PARAMETER_ID,
        expected_date_value="Jan 15, 2026",
        expected_hour="10",
        expected_minute="43",
    )
