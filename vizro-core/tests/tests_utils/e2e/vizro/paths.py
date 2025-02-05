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


def categorical_components_value_path(elem_id, value):
    return f"div[id='{elem_id}'] div:nth-of-type({value}) input"
