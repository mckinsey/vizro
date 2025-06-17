def theme_toggle_path():
    return "#theme-selector"


# Navigation


def tab_path(tab_id, classname):
    return f"ul[id='{tab_id}'] a[class='{classname}']"


# Components


def page_title_path():
    return "#page-title"


def nav_card_link_path(href):
    return f"a[href='{href}'][class='nav-link']"


def slider_value_path(elem_id, value):
    return f"div[id='{elem_id}'] div div span:nth-of-type({value})"


def slider_handler_path(elem_id, handler_class="rc-slider-handle"):
    return f"div[id='{elem_id}'] div[class^='{handler_class}']"


def categorical_components_value_path(elem_id, value):
    return f"div[id='{elem_id}'] div:nth-of-type({value}) input"


def categorical_components_value_name_path(elem_id, value):
    return f"div[id='{elem_id}'] div:nth-of-type({value}) label"


def kpi_card_path():
    return ".card-body"


def select_all_path(elem_id):
    """Select All option path for checklist and dropdown."""
    return f"input[id='{elem_id}_select_all']"


def dropdown_arrow_path(dropdown_id):
    return f"div[id='{dropdown_id}'] .Select-arrow"


def button_path():
    return "button[class='btn btn-primary']"


def table_cell_value_path(table_id, row_number, column_number):
    return f"div[id='{table_id}'] tr:nth-of-type({row_number}) td:nth-of-type({column_number}) div"


def table_ag_grid_cell_value_path(table_id, row_number, column_number):
    return (
        f"div[id='{table_id}'] div[class='ag-center-cols-container'] div:nth-of-type({row_number}) "
        f"div:nth-of-type({column_number})"
    )


def graph_axis_value_path(graph_id, axis_value_number, axis_value):
    """Path to x or y axis values of the graph according to axis_value_number."""
    return f"div[id='{graph_id}'] g:nth-of-type({axis_value_number}) text[data-unformatted='{axis_value}']"
