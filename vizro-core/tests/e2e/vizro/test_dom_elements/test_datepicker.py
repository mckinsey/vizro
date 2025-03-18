import e2e.vizro.constants as cnst
from e2e.vizro.checkers import check_graph_is_loading, check_table_rows_number
from e2e.vizro.navigation import accordion_select, page_select
from e2e.vizro.paths import table_cell_value_path


def test_single_date(dash_br):
    accordion_select(
        dash_br, accordion_name=cnst.DATEPICKER_ACCORDION.upper(), accordion_number=cnst.DATEPICKER_ACCORDION_NUMBER
    )
    page_select(
        dash_br,
        page_path=cnst.DATEPICKER_PAGE_PATH,
        page_name=cnst.DATEPICKER_PAGE,
        graph_id=cnst.BAR_POP_DATE_ID,
    )
    dash_br.multiple_click(f'button[id="{cnst.DATEPICKER_SINGLE_ID}"]', 1)
    dash_br.wait_for_element('div[data-calendar="true"]')
    dash_br.multiple_click('button[aria-label="17 May 2016"]', 1)
    check_graph_is_loading(dash_br, cnst.BAR_POP_DATE_ID)
    dash_br.wait_for_text_to_equal(
        table_cell_value_path(table_id=cnst.TABLE_POP_DATE_ID, row_number=2, column_number=1), "2016-05-17T00:00:00"
    )
    check_table_rows_number(dash_br, table_id=cnst.TABLE_POP_DATE_ID, expected_rows_num=2)
    dash_br.wait_for_text_to_equal(f'button[id="{cnst.DATEPICKER_SINGLE_ID}"]', "May 17, 2016")


def test_date_range(dash_br):
    accordion_select(
        dash_br, accordion_name=cnst.DATEPICKER_ACCORDION.upper(), accordion_number=cnst.DATEPICKER_ACCORDION_NUMBER
    )
    page_select(
        dash_br,
        page_path=cnst.DATEPICKER_PAGE_PATH,
        page_name=cnst.DATEPICKER_PAGE,
        graph_id=cnst.BAR_POP_DATE_ID,
    )
    dash_br.multiple_click(f'button[id="{cnst.DATEPICKER_RANGE_ID}"]', 1)
    dash_br.wait_for_element('div[data-calendar="true"]')
    dash_br.multiple_click('button[aria-label="17 May 2016"]', 1)
    dash_br.multiple_click('button[aria-label="18 May 2016"]', 1)
    check_graph_is_loading(dash_br, cnst.BAR_POP_RANGE_ID)
    dash_br.wait_for_text_to_equal(
        table_cell_value_path(table_id=cnst.TABLE_POP_RANGE_ID, row_number=2, column_number=1), "2016-05-17T00:00:00"
    )
    check_table_rows_number(dash_br, table_id=cnst.TABLE_POP_RANGE_ID, expected_rows_num=4)
    dash_br.wait_for_text_to_equal(f'button[id="{cnst.DATEPICKER_RANGE_ID}"]', "May 17, 2016 – May 18, 2016")  # noqa: RUF001


def test_single_date_param(dash_br):
    accordion_select(
        dash_br, accordion_name=cnst.DATEPICKER_ACCORDION.upper(), accordion_number=cnst.DATEPICKER_ACCORDION_NUMBER
    )
    page_select(
        dash_br,
        page_path=cnst.DATEPICKER_PARAMS_PAGE_PATH,
        page_name=cnst.DATEPICKER_PARAMS_PAGE,
        graph_id=cnst.BAR_CUSTOM_ID,
    )
    dash_br.multiple_click(f'button[id="{cnst.DATEPICKER_PARAMS_ID}"]', 1)
    dash_br.wait_for_element('div[data-calendar="true"]')
    dash_br.multiple_click('button[aria-label="2 April 2018"]', 1)
    # check that one of the bars change color from blue to orange
    dash_br.wait_for_element(f"div[id='{cnst.BAR_CUSTOM_ID}'] g:nth-of-type(14) path[style*='(255, 165, 0)'")
