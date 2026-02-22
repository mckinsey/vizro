def theme_toggle_path():
    return "#theme-selector"


def switch_path_using_filter_control_id(filter_control_id):
    return f"#{filter_control_id} input[type='checkbox']"


# Navigation


def tab_path(tab_id, classname):
    return f"ul[id='{tab_id}'] a[class='{classname}']"


# Components


def page_title_path():
    return "#page-title"


def nav_card_link_path(href):
    return f"a[href='{href}'][class='nav-link']"


def slider_value_path(elem_id, value):
    return f"div[id='{elem_id}'] div div:nth-of-type({value})"


def slider_handler_path(elem_id, handler_class="rc-slider-handle"):
    return f"div[id='{elem_id}'] div[class^='{handler_class}']"


def categorical_components_value_path(elem_id, value):
    return f"div[id='{elem_id}'] div:nth-of-type({value}) input"


def categorical_components_value_name_path(elem_id, value):
    return f"div[id='{elem_id}'] div:nth-of-type({value}) label"


def kpi_card_path():
    return ".card-body"


def select_all_path(elem_id):
    """Select All option path for checklist."""
    return f"input[id='{elem_id}_select_all']"


def dropdown_id_path(dropdown_id):
    return f"button[id='{dropdown_id}']"


def dropdown_select_all_path(dropdown_id):
    return f"{dropdown_id_path(dropdown_id)} + div .dash-dropdown-action-button:nth-of-type(1)"


def dropdown_deselect_all_path(dropdown_id):
    return f"{dropdown_id_path(dropdown_id)} + div .dash-dropdown-action-button:nth-of-type(2)"


def button_id_path(btn_id):
    return f"button[id='{btn_id}']"


def table_cell_value_path(table_id, row_number, column_number):
    return f"div[id='{table_id}'] tr:nth-of-type({row_number}) td:nth-of-type({column_number}) div"


def table_ag_grid_cell_value_path(table_id, row_number, column_number):
    return (
        f"div[id='{table_id}'] div[class='ag-center-cols-container'] div:nth-of-type({row_number}) "
        f"div:nth-of-type({column_number})"
    )


def table_ag_grid_cell_path_by_row(table_id, row_index, col_id):
    """Path to AG Grid table cell by row index and column id."""
    return f"div[id='{table_id}'] div[row-index='{row_index}'] div[col-id='{col_id}']"


def table_ag_grid_checkbox_path_by_row(table_id, row_index):
    """Path to AG Grid table checkbox input by row index."""
    return f"div[id='{table_id}'] div[row-index='{row_index}'] input.ag-checkbox-input"


def graph_axis_value_path(graph_id, axis, tick_index, value):
    axis = axis.lower()
    if axis not in {"x", "y"}:
        raise ValueError("axis must be either 'x' or 'y'")
    return f"div[id='{graph_id}'] .{axis}axislayer-below g:nth-of-type({tick_index}) text[data-unformatted='{value}']"


def actions_progress_indicator_path():
    return 'span[class="material-symbols-outlined progress-indicator"]'


def scatter_point_path(graph_id, point_number, trace_index=2):
    return f"div[id='{graph_id}'] g[class^='trace']:nth-of-type({trace_index}) path:nth-of-type({point_number})"
