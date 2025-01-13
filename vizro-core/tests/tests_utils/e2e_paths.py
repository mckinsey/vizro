def href_path(href):
    return f'//*[@href="{href}"]'


def theme_toggle_path():
    return '//*[@id="theme-selector"]'

# Navigation


def accordion_path(accordion_name):
    return f'//*[@class="accordion accordion"]//*[text()="{accordion_name}"]'


def page_accordion_path(page):
    return f'//*[@class="accordion-item-link nav-link"][text()="{page}"]'


def page_title_path(page_title):
    return f'//*[@id="right-header"]/h2[text()="{page_title}"]'


def tab_path(tab_id, classname):
    return f'//*[@class="{classname}"][text()="{tab_id}"]'

# Components


def nav_card_text_path(href):
    return f'//*[@href="{href}"][@class="nav-link"]'


def graph_xaxis_tick_path(graph_id):
    return f'//*[@id="{graph_id}"]//*[@class="xtick ticks crisp"]'


def dropdown_path(elem_id=None):
    if elem_id:
        return f'//*[@id="{elem_id}"]'
    else:
        return '//*[@class="dash-dropdown"]'


def dropdown_arrow_path(xpath=dropdown_path()):
    return f'{xpath}//*[@class="Select-arrow"]'


def dropdown_value_path(value, xpath=dropdown_path()):
    return f'{xpath}//*[@class="ReactVirtualized__Grid__innerScrollContainer"]/div[{value}]'


def dropdown_clear_all_path(xpath=dropdown_path()):
    return f'{xpath}//*[@class="Select-clear-zone"]//*[@class="Select-clear"][text()="×"]'  # noqa: RUF001


def checklist_value_path(title, value):
    return f"//*[@class='form-label'][text()='{title}']/..//*[@type='checkbox']/../../div[{value}]//*[@type='checkbox']"


def radio_items_value_path(title, value):
    return f"//*[@class='form-label'][text()='{title}']/..//*[@type='radio']/../../div[{value}]//*[@type='radio']"


def slider_value_path(elem_id, value):
    return f"//*[@id='{elem_id}']/div/div/span[{value}]"


def range_slider_value_path(elem_id, value):
    return f"//*[@id='{elem_id}']/div/div/span[{value}]"


def kpi_card_text_path():
    return "//*[@id='page-components']//*[@class='card-body']"


def button_path(button_text):
    return f'//*[contains(@class, "btn btn-primary")][text()="{button_text}"]'


def graph_path(graph_id):
    return f'//*[@id="{graph_id}"]//*[@class="main-svg"]'


