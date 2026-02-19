import e2e.vizro.constants as cnst
from e2e.vizro.checkers import check_graph_is_loaded, check_table_ag_grid_rows_number
from e2e.vizro.navigation import accordion_select, page_select, select_slider_value
from e2e.vizro.paths import (
    categorical_components_value_path,
    table_ag_grid_cell_path_by_row,
    table_ag_grid_cell_value_path,
)


def test_filters(dash_br):
    """Test ag_grid filtering."""
    accordion_select(dash_br, accordion_name=cnst.AG_GRID_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.TABLE_AG_GRID_PAGE,
    )

    # select 'Africa'
    dash_br.multiple_click(categorical_components_value_path(elem_id=cnst.RADIOITEMS_AGGRID_FILTER, value=2), 1)
    # select '6000000' as max value
    select_slider_value(dash_br, elem_id=cnst.RANGESLIDER_AGGRID_FILTER, value="6M")

    # check data for the 2nd row
    dash_br.wait_for_text_to_equal(
        table_ag_grid_cell_value_path(table_id=cnst.TABLE_AG_GRID_ID, row_number=2, column_number=1),
        "Central African Republic",
    )
    dash_br.wait_for_text_to_equal(
        table_ag_grid_cell_value_path(table_id=cnst.TABLE_AG_GRID_ID, row_number=2, column_number=2), "Africa"
    )
    dash_br.wait_for_text_to_equal(
        table_ag_grid_cell_value_path(table_id=cnst.TABLE_AG_GRID_ID, row_number=2, column_number=3), "2007"
    )
    dash_br.wait_for_text_to_equal(
        table_ag_grid_cell_value_path(table_id=cnst.TABLE_AG_GRID_ID, row_number=2, column_number=4),
        "44.74100000000001",
    )
    dash_br.wait_for_text_to_equal(
        table_ag_grid_cell_value_path(table_id=cnst.TABLE_AG_GRID_ID, row_number=2, column_number=5), "4369038"
    )

    # check that number of rows with data is 14
    check_table_ag_grid_rows_number(dash_br, table_id=cnst.TABLE_AG_GRID_ID, expected_rows_num=14)


def test_interactions(dash_br):
    """Test filter interaction between ag_grid and line graph."""
    accordion_select(dash_br, accordion_name=cnst.AG_GRID_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.TABLE_AG_GRID_INTERACTIONS_PAGE,
    )

    # check if column 'country' is available
    dash_br.wait_for_element(
        table_ag_grid_cell_path_by_row(cnst.TABLE_AG_GRID_INTERACTIONS_ID, row_index=0, col_id="country")
    )

    # click on Bosnia and Herzegovina country
    dash_br.multiple_click(
        table_ag_grid_cell_path_by_row(cnst.TABLE_AG_GRID_INTERACTIONS_ID, row_index=3, col_id="country"),
        1,
    )
    check_graph_is_loaded(dash_br, cnst.LINE_AG_GRID_INTERACTIONS_ID)
