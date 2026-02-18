from e2e.vizro import constants as cnst
from e2e.vizro.checkers import check_graph_is_loaded, check_table_rows_number
from e2e.vizro.navigation import accordion_select, page_select, select_slider_value
from e2e.vizro.paths import categorical_components_value_path, table_cell_value_path


def test_filters(dash_br):
    """Test table filtering."""
    accordion_select(dash_br, accordion_name=cnst.AG_GRID_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.TABLE_PAGE,
        graph_check=False,
    )

    # select 'Africa'
    dash_br.multiple_click(categorical_components_value_path(elem_id=cnst.RADIOITEMS_TABLE_FILTER, value=2), 1)
    # select '6000000' as max value
    select_slider_value(dash_br, elem_id=cnst.RANGESLIDER_TABLE_FILTER, value="6M")

    # check if country Benin is available
    dash_br.wait_for_text_to_equal(
        f"div[id='{cnst.TABLE_ID}'] tr:nth-of-type(2) div[class='unfocused selectable dash-cell-value']", "Botswana"
    )

    # check that number of rows is 15, because we're counting it with header
    check_table_rows_number(dash_br, table_id=cnst.TABLE_ID, expected_rows_num=15)

    # check data for the 3rd row
    dash_br.wait_for_text_to_equal(
        table_cell_value_path(table_id=cnst.TABLE_ID, row_number=3, column_number=1), "Central African Republic"
    )
    dash_br.wait_for_text_to_equal(
        table_cell_value_path(table_id=cnst.TABLE_ID, row_number=3, column_number=2), "Africa"
    )
    dash_br.wait_for_text_to_equal(table_cell_value_path(table_id=cnst.TABLE_ID, row_number=3, column_number=3), "2007")
    dash_br.wait_for_text_to_equal(
        table_cell_value_path(table_id=cnst.TABLE_ID, row_number=3, column_number=4), "44.74100000000001"
    )
    dash_br.wait_for_text_to_equal(
        table_cell_value_path(table_id=cnst.TABLE_ID, row_number=3, column_number=5), "4369038"
    )
    dash_br.wait_for_text_to_equal(
        table_cell_value_path(table_id=cnst.TABLE_ID, row_number=3, column_number=6), "706.016537"
    )
    dash_br.wait_for_text_to_equal(
        table_cell_value_path(table_id=cnst.TABLE_ID, row_number=3, column_number=7),
        "CAF",  # codespell:ignore
    )
    dash_br.wait_for_text_to_equal(table_cell_value_path(table_id=cnst.TABLE_ID, row_number=3, column_number=8), "140")


def test_interactions(dash_br):
    """Test filter interaction between table and line graph."""
    accordion_select(dash_br, accordion_name=cnst.AG_GRID_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.TABLE_INTERACTIONS_PAGE,
    )
    # click on Bosnia and Herzegovina country
    dash_br.multiple_click(
        f"div[id='{cnst.TABLE_INTERACTIONS_ID}'] tr:nth-of-type(5) div[class='unfocused selectable dash-cell-value']", 1
    )
    check_graph_is_loaded(dash_br, cnst.LINE_INTERACTIONS_ID)
    check_table_rows_number(dash_br, table_id=cnst.TABLE_INTERACTIONS_ID, expected_rows_num=31)
