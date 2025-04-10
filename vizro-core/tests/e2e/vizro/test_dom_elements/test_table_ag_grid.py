import e2e.vizro.constants as cnst
from e2e.vizro.checkers import check_graph_is_loading, check_table_ag_grid_rows_number
from e2e.vizro.navigation import accordion_select, page_select
from e2e.vizro.paths import categorical_components_value_path, slider_value_path, table_ag_grid_cell_value_path


def test_filters(dash_br):
    """Test ag_grid filtering."""
    accordion_select(dash_br, accordion_name=cnst.AG_GRID_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.TABLE_AG_GRID_PAGE,
    )

    # select 'Africa'
    dash_br.multiple_click(categorical_components_value_path(elem_id=cnst.RADIOITEMS_AGGRID_FILTER, value=2), 1)
    # select 'Asia', but 'ALL' still selected
    dash_br.multiple_click(categorical_components_value_path(elem_id=cnst.CHECKLIST_AGGRID_FILTER, value=2), 1)
    # select '5000000' as min value
    dash_br.multiple_click(slider_value_path(elem_id=cnst.RANGESLIDER_AGGRID_FILTER, value=5), 1)

    # check data for the 2nd row
    dash_br.wait_for_text_to_equal(
        table_ag_grid_cell_value_path(table_id=cnst.TABLE_AG_GRID_ID, row_number=2, column_number=1), "Burundi"
    )
    dash_br.wait_for_text_to_equal(
        table_ag_grid_cell_value_path(table_id=cnst.TABLE_AG_GRID_ID, row_number=2, column_number=2), "Africa"
    )
    dash_br.wait_for_text_to_equal(
        table_ag_grid_cell_value_path(table_id=cnst.TABLE_AG_GRID_ID, row_number=2, column_number=3), "2007"
    )
    dash_br.wait_for_text_to_equal(
        table_ag_grid_cell_value_path(table_id=cnst.TABLE_AG_GRID_ID, row_number=2, column_number=4), "49.58"
    )
    dash_br.wait_for_text_to_equal(
        table_ag_grid_cell_value_path(table_id=cnst.TABLE_AG_GRID_ID, row_number=2, column_number=5), "8390505"
    )

    # check that number of rows with data is 8
    check_table_ag_grid_rows_number(dash_br, table_id=cnst.TABLE_AG_GRID_ID, expected_rows_num=8)


def test_interactions(dash_br):
    """Test filter interaction between ag_grid and line graph."""
    accordion_select(dash_br, accordion_name=cnst.AG_GRID_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.TABLE_AG_GRID_INTERACTIONS_PAGE,
    )

    # check if column 'country' is available
    dash_br.wait_for_element(f"div[id='{cnst.TABLE_AG_GRID_INTERACTIONS_ID}'] div:nth-of-type(1) div[col-id='country']")

    # click on Bosnia and Herzegovina country
    dash_br.multiple_click(
        f"div[id='{cnst.TABLE_AG_GRID_INTERACTIONS_ID}'] div[class='ag-center-cols-container'] "
        f"div:nth-of-type(4) div[col-id='country']",
        1,
    )
    check_graph_is_loading(dash_br, cnst.LINE_AG_GRID_INTERACTIONS_ID)
