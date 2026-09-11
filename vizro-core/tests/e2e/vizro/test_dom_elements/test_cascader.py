import e2e.vizro.constants as cnst
from e2e.vizro.checkers import (
    check_cascader_trigger_value,
    check_table_ag_grid_column_values,
    check_table_ag_grid_rows_number,
)
from e2e.vizro.navigation import (
    accordion_select,
    clear_cascader_multi,
    clear_cascader_single,
    page_select,
    select_cascader_path,
)
from e2e.vizro.paths import button_id_path, table_ag_grid_cell_path_by_row


def _open_cascader_leaf_page(dash_br):
    accordion_select(dash_br, accordion_name=cnst.CASCADER_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.CASCADER_LEAF_PAGE,
        page_path=cnst.CASCADER_LEAF_PAGE_PATH,
        graph_check=False,
    )


def _open_cascader_path_page(dash_br):
    accordion_select(dash_br, accordion_name=cnst.CASCADER_ACCORDION)
    page_select(
        dash_br,
        page_name=cnst.CASCADER_PATH_PAGE,
        page_path=cnst.CASCADER_PATH_PAGE_PATH,
        graph_check=False,
    )


def test_cascader_leaf_single_select_filters_ag_grid(dash_br):
    """Leaf-mode single Cascader filters on the leaf column when a new country is selected."""
    _open_cascader_leaf_page(dash_br)

    clear_cascader_single(dash_br, cnst.CASCADER_LEAF_ID)
    select_cascader_path(
        dash_br,
        cnst.CASCADER_LEAF_ID,
        ["Asia", "South", "China"],
        multi=False,
    )

    check_cascader_trigger_value(dash_br, cnst.CASCADER_LEAF_ID, "China")
    check_table_ag_grid_rows_number(dash_br, table_id=cnst.CASCADER_LEAF_AG_GRID_ID, expected_rows_num=1)
    check_table_ag_grid_column_values(
        dash_br, table_id=cnst.CASCADER_LEAF_AG_GRID_ID, col_id="country", expected_values=["China"]
    )


def test_cascader_leaf_multi_select_filters_ag_grid(dash_br):
    """Leaf-mode multi Cascader filters on multiple leaf countries independently."""
    _open_cascader_leaf_page(dash_br)

    clear_cascader_multi(dash_br, cnst.CASCADER_LEAF_MULTI_ID)
    select_cascader_path(
        dash_br,
        cnst.CASCADER_LEAF_MULTI_ID,
        ["Americas", "South", "Brazil"],
        multi=True,
    )
    select_cascader_path(
        dash_br,
        cnst.CASCADER_LEAF_MULTI_ID,
        ["Asia", "South", "Japan"],
        multi=True,
    )

    check_table_ag_grid_rows_number(dash_br, table_id=cnst.CASCADER_LEAF_MULTI_AG_GRID_ID, expected_rows_num=2)
    check_table_ag_grid_column_values(
        dash_br,
        table_id=cnst.CASCADER_LEAF_MULTI_AG_GRID_ID,
        col_id="country",
        expected_values=["Brazil", "Japan"],
    )


def test_cascader_path_single_select_filters_duplicate_leaf(dash_br):
    """Path-mode single Cascader disambiguates duplicate leaf labels via the full path."""
    _open_cascader_path_page(dash_br)

    clear_cascader_single(dash_br, cnst.CASCADER_PATH_ID)
    select_cascader_path(
        dash_br,
        cnst.CASCADER_PATH_ID,
        ["Maine", "Portland"],
        multi=False,
    )

    check_cascader_trigger_value(dash_br, cnst.CASCADER_PATH_ID, "Portland")
    check_table_ag_grid_rows_number(dash_br, table_id=cnst.CASCADER_PATH_AG_GRID_ID, expected_rows_num=1)
    check_table_ag_grid_column_values(
        dash_br,
        table_id=cnst.CASCADER_PATH_AG_GRID_ID,
        col_id="state",
        expected_values=["Maine"],
    )


def test_cascader_path_multi_select_filters_duplicate_leaves(dash_br):
    """Path-mode multi Cascader filters both 'Portland' paths independently."""
    _open_cascader_path_page(dash_br)

    clear_cascader_multi(dash_br, cnst.CASCADER_PATH_MULTI_ID)
    select_cascader_path(
        dash_br,
        cnst.CASCADER_PATH_MULTI_ID,
        ["Oregon", "Portland"],
        multi=True,
    )
    select_cascader_path(
        dash_br,
        cnst.CASCADER_PATH_MULTI_ID,
        ["Maine", "Portland"],
        multi=True,
    )

    check_table_ag_grid_rows_number(dash_br, table_id=cnst.CASCADER_PATH_MULTI_AG_GRID_ID, expected_rows_num=2)
    check_table_ag_grid_column_values(
        dash_br,
        table_id=cnst.CASCADER_PATH_MULTI_AG_GRID_ID,
        col_id="state",
        expected_values=["Oregon", "Maine"],
    )
    check_table_ag_grid_column_values(
        dash_br,
        table_id=cnst.CASCADER_PATH_MULTI_AG_GRID_ID,
        col_id="city",
        expected_values=["Portland", "Portland"],
    )


def test_set_control_cascader_leaf_button_filters_ag_grid(dash_br):
    """set_control from a button sets a leaf-mode Cascader filter and refreshes its target AgGrid."""
    _open_cascader_leaf_page(dash_br)

    dash_br.multiple_click(button_id_path(btn_id=cnst.CASCADER_LEAF_SET_CONTROL_BUTTON_ID), 1, delay=0.1)

    check_cascader_trigger_value(dash_br, cnst.CASCADER_LEAF_ID, "China")
    check_table_ag_grid_rows_number(dash_br, table_id=cnst.CASCADER_LEAF_AG_GRID_ID, expected_rows_num=1)
    check_table_ag_grid_column_values(
        dash_br, table_id=cnst.CASCADER_LEAF_AG_GRID_ID, col_id="country", expected_values=["China"]
    )


def test_set_control_cascader_leaf_ag_grid_filters_ag_grid(dash_br):
    """set_control from an AgGrid sets a leaf-mode Cascader filter and refreshes its target AgGrid."""
    _open_cascader_leaf_page(dash_br)

    # Select Brazil on AgGrid
    dash_br.multiple_click(
        table_ag_grid_cell_path_by_row(
            cnst.CASCADER_LEAF_SET_CONTROL_AG_GRID_SOURCE_ID, row_index=14, col_id="country"
        ),
        1,
    )

    check_cascader_trigger_value(dash_br, cnst.CASCADER_LEAF_ID, "Brazil")
    check_table_ag_grid_rows_number(dash_br, table_id=cnst.CASCADER_LEAF_AG_GRID_ID, expected_rows_num=1)
    check_table_ag_grid_column_values(
        dash_br, table_id=cnst.CASCADER_LEAF_AG_GRID_ID, col_id="country", expected_values=["Brazil"]
    )


def test_set_control_cascader_path_ag_grid_filters_ag_grid(dash_br):
    """set_control from an AgGrid sets a leaf-mode Cascader on the path page and refreshes its target AgGrid."""
    _open_cascader_path_page(dash_br)

    # Select vity Augusta on AgGrid
    dash_br.multiple_click(
        table_ag_grid_cell_path_by_row(cnst.CASCADER_PATH_SET_CONTROL_AG_GRID_SOURCE_ID, row_index=4, col_id="city"),
        1,
    )

    check_cascader_trigger_value(dash_br, cnst.CASCADER_PATH_SET_CONTROL_ID, "Augusta")
    check_table_ag_grid_rows_number(dash_br, table_id=cnst.CASCADER_PATH_SET_CONTROL_AG_GRID_ID, expected_rows_num=1)
    check_table_ag_grid_column_values(
        dash_br,
        table_id=cnst.CASCADER_PATH_SET_CONTROL_AG_GRID_ID,
        col_id="state",
        expected_values=["Maine"],
    )
    check_table_ag_grid_column_values(
        dash_br,
        table_id=cnst.CASCADER_PATH_SET_CONTROL_AG_GRID_ID,
        col_id="city",
        expected_values=["Augusta"],
    )
