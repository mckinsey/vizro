import e2e.vizro.constants as cnst
from e2e.vizro.checkers import check_table_rows_number
from e2e.vizro.navigation import accordion_select, page_select
from e2e.vizro.paths import graph_axis_value_path, table_cell_value_path


def test_single_date(dash_br):
    """Tests that single datepicker as filter works correctly."""
    accordion_select(dash_br, accordion_name=cnst.DATEPICKER_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.DATEPICKER_PAGE,
    )

    # open datepicker calendar and choose date 17 May 2016
    dash_br.multiple_click(f'button[id="{cnst.DATEPICKER_SINGLE_ID}"]', 1)
    dash_br.wait_for_element('div[data-calendar="true"]')
    dash_br.multiple_click('button[aria-label="17 May 2016"]', 1)
    dash_br.wait_for_text_to_equal(f'button[id="{cnst.DATEPICKER_SINGLE_ID}"]', "May 17, 2016")

    # check bar graph has bar with light blue color
    dash_br.wait_for_element(f"div[id='{cnst.BAR_POP_DATE_ID}'] path[style*='rgb(13, 142, 209)']:nth-of-type(1)")

    # check that date in the row is correct
    # we're using 'row_number=2' because the first row is a header
    dash_br.wait_for_text_to_equal(
        table_cell_value_path(table_id=cnst.TABLE_POP_DATE_ID, row_number=2, column_number=1), "2016-05-17T00:00:00"
    )

    # check that we have only 1 row in the table
    # we're using 'expected_rows_num=2' because the first row is a header
    check_table_rows_number(dash_br, table_id=cnst.TABLE_POP_DATE_ID, expected_rows_num=2)


def test_date_range(dash_br):
    """Tests that range datepicker as filter works correctly."""
    accordion_select(dash_br, accordion_name=cnst.DATEPICKER_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.DATEPICKER_PAGE,
    )

    # open datepicker calendar and choose dates from 17 to 18 May 2016
    dash_br.multiple_click(f'button[id="{cnst.DATEPICKER_RANGE_ID}"]', 1)
    dash_br.wait_for_element('div[data-calendar="true"]')
    dash_br.multiple_click('button[aria-label="17 May 2016"]', 1)
    dash_br.multiple_click('button[aria-label="18 May 2016"]', 1)

    # Check x axis max value is '12:00'
    dash_br.wait_for_text_to_equal(
        graph_axis_value_path(graph_id=cnst.BAR_POP_RANGE_ID, axis_value_number="5", axis_value="12:00"),
        "12:00",
    )

    dash_br.wait_for_text_to_equal(f'button[id="{cnst.DATEPICKER_RANGE_ID}"]', "May 17, 2016 – May 18, 2016")  # noqa: RUF001

    # check that dates in the rows are within the chosen range
    # we're starting from 'row_number=2' because the first row is a header
    dash_br.wait_for_text_to_equal(
        table_cell_value_path(table_id=cnst.TABLE_POP_RANGE_ID, row_number=2, column_number=1), "2016-05-17T00:00:00"
    )
    dash_br.wait_for_text_to_equal(
        table_cell_value_path(table_id=cnst.TABLE_POP_RANGE_ID, row_number=3, column_number=1), "2016-05-18T00:00:00"
    )
    dash_br.wait_for_text_to_equal(
        table_cell_value_path(table_id=cnst.TABLE_POP_RANGE_ID, row_number=4, column_number=1), "2016-05-18T00:00:00"
    )

    # check that we have only 3 rows in the table
    # we're using 'expected_rows_num=4' because the first row is a header
    check_table_rows_number(dash_br, table_id=cnst.TABLE_POP_RANGE_ID, expected_rows_num=4)


def test_single_date_param(dash_br):
    """Tests that single datepicker as parameter works correctly."""
    accordion_select(dash_br, accordion_name=cnst.DATEPICKER_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.DATEPICKER_PARAMS_PAGE,
    )
    # check that specific bar has blue color
    dash_br.wait_for_element(f"div[id='{cnst.BAR_CUSTOM_ID}'] g:nth-of-type(14) path[style*='(0, 0, 255)'")

    # open datepicker calendar and choose date 2 May 2018
    dash_br.multiple_click(f'button[id="{cnst.DATEPICKER_PARAMS_ID}"]', 1)
    dash_br.wait_for_element('div[data-calendar="true"]')
    dash_br.multiple_click('button[aria-label="2 April 2018"]', 1)

    # check that specific bar change color from blue to orange
    dash_br.wait_for_element(f"div[id='{cnst.BAR_CUSTOM_ID}'] g:nth-of-type(14) path[style*='(255, 165, 0)'")
