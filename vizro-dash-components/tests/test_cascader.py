"""Tests for the vizro_dash_components.Cascader component."""

import dash_mantine_components as dmc
from dash import Dash, Input, Output, html
from vizro_dash_components import Cascader

OPTIONS_2LEVEL = [
    {
        "label": "Asia",
        "value": "asia",
        "children": [
            {"label": "Japan", "value": "japan"},
            {"label": "China", "value": "china"},
        ],
    },
    {
        "label": "Europe",
        "value": "europe",
        "children": [
            {"label": "France", "value": "france"},
            {"label": "Germany", "value": "germany"},
        ],
    },
]

OPTIONS_3LEVEL = [
    {
        "label": "Asia",
        "value": "asia",
        "children": [
            {
                "label": "East Asia",
                "value": "east_asia",
                "children": [
                    {"label": "Japan", "value": "japan"},
                ],
            },
        ],
    },
]

# Shorthand `options` (see cascaderUtils.normalizeOptions): dict keys become parents; list
# items are leaves (scalar → label and value identical); nested dicts add levels.
OPTIONS_SHORTHAND_DICT_LIST = {"Asia": ["Japan", "China"], "Europe": ["France", "Germany"]}

OPTIONS_SHORTHAND_NESTED = {"Europe": {"Western": ["France", "Germany"]}}

OPTIONS_SHORTHAND_MIXED_LEAVES = {
    "Asia": [
        {"label": "Nippon", "value": "japan"},
        "China",
    ],
}

OPTIONS_SHORTHAND_NUMERIC = {"Series": [10, 20, 30]}


def _app(layout):
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(layout)
    return app


def _multi_values_joined(v):
    return ",".join(sorted(str(x) for x in (v or [])))


def _sorted_values_string(v):
    return str(sorted(v or []))


# --- Render / open / close ---


def test_cascader_renders(dash_duo):
    """Component renders a trigger button without errors."""
    app = _app(Cascader(id="c", options=OPTIONS_2LEVEL))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c")
    assert dash_duo.get_logs() == []


def test_cascader_opens_on_click(dash_duo):
    """Clicking the trigger opens the panel."""
    app = _app(Cascader(id="c", options=OPTIONS_2LEVEL))
    dash_duo.start_server(app)
    trigger = dash_duo.wait_for_element("#c")
    trigger.click()
    dash_duo.wait_for_element(".dash-cascader-content")
    assert dash_duo.get_logs() == []


def test_cascader_keyboard_arrow_down_opens_and_focuses_search(dash_duo):
    """ArrowDown on the closed trigger opens the panel and focuses search (dcc.Dropdown parity)."""
    from selenium.webdriver.common.keys import Keys

    app = _app(Cascader(id="c", options=OPTIONS_2LEVEL))
    dash_duo.start_server(app)
    trigger = dash_duo.wait_for_element("#c")
    dash_duo.driver.execute_script("arguments[0].focus();", trigger)
    trigger.send_keys(Keys.ARROW_DOWN)
    dash_duo.wait_for_element(".dash-cascader-content")
    active = dash_duo.driver.switch_to.active_element
    assert "dash-dropdown-search" in (active.get_attribute("class") or "")
    assert dash_duo.get_logs() == []


def test_cascader_keyboard_backspace_on_trigger_clears(dash_duo):
    """Backspace on the focused trigger clears selection when clearable (dcc.Dropdown parity)."""
    from selenium.webdriver.common.keys import Keys

    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(id="c", options=OPTIONS_2LEVEL, value="japan"),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(str)
    dash_duo.start_server(app)
    trigger = dash_duo.wait_for_element("#c")
    dash_duo.driver.execute_script("arguments[0].focus();", trigger)
    trigger.send_keys(Keys.BACKSPACE)
    dash_duo.wait_for_text_to_equal("#out", "None")
    assert dash_duo.get_logs() == []


def test_cascader_shows_root_column(dash_duo):
    """Root column shows top-level option labels after opening."""
    app = _app(Cascader(id="c", options=OPTIONS_2LEVEL))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_text_to_equal(
        ".dash-cascader-column:first-child .dash-cascader-row:first-child .dash-cascader-row-label", "Asia"
    )


def test_cascader_closes_on_outside_click(dash_duo):
    """Clicking outside the component closes the panel."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    app = _app(
        html.Div(
            [
                html.Div("outside", id="outside"),
                Cascader(id="c", options=OPTIONS_2LEVEL),
            ]
        )
    )
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-cascader-content")
    dash_duo.find_element("#outside").click()
    WebDriverWait(dash_duo.driver, 3).until(
        EC.invisibility_of_element_located((By.CSS_SELECTOR, ".dash-cascader-content"))
    )


# --- Single-select ---


def test_cascader_single_select_leaf(dash_duo):
    """Clicking a leaf in single mode sets the value and closes the panel."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(id="c", options=OPTIONS_2LEVEL),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(str)
    dash_duo.start_server(app)
    # Open
    dash_duo.wait_for_element("#c").click()
    # Click "Asia" to expand
    dash_duo.wait_for_element(".dash-cascader-row").click()
    # Click "Japan" (leaf in second column)
    rows = dash_duo.driver.find_elements("css selector", ".dash-cascader-column:nth-child(2) .dash-cascader-row")
    rows[0].click()
    # Panel closes, value updated
    dash_duo.wait_for_text_to_equal("#out", "japan")
    panels = dash_duo.driver.find_elements("css selector", ".dash-cascader-content")
    assert len(panels) == 0
    assert dash_duo.get_logs() == []


def test_cascader_parent_expand_then_collapse(dash_duo):
    """Clicking an expanded parent again collapses the child column."""
    app = _app(Cascader(id="c", options=OPTIONS_2LEVEL))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    asia_row = dash_duo.wait_for_element(".dash-cascader-column:nth-child(1) .dash-cascader-row")
    asia_row.click()
    cols = dash_duo.driver.find_elements("css selector", ".dash-cascader-column")
    assert len(cols) == 2
    expanded = dash_duo.driver.find_element("css selector", ".dash-cascader-chevron-expanded")
    assert expanded
    dash_duo.driver.find_element("css selector", ".dash-cascader-column:nth-child(1) .dash-cascader-row").click()
    cols_after = dash_duo.driver.find_elements("css selector", ".dash-cascader-column")
    assert len(cols_after) == 1
    assert dash_duo.get_logs() == []


def test_cascader_single_select_shows_label_in_trigger(dash_duo):
    """Selected leaf label is shown in the trigger."""
    app = _app(Cascader(id="c", options=OPTIONS_2LEVEL, value="japan"))
    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#c .dash-dropdown-value", "Japan")


def test_cascader_single_clear(dash_duo):
    """Clicking the clear button sets value to null."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(id="c", options=OPTIONS_2LEVEL, value="japan"),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(str)
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c a.dash-dropdown-clear").click()
    dash_duo.wait_for_text_to_equal("#out", "None")


# --- Multi-select ---


def test_cascader_multi_select_leaf(dash_duo):
    """Clicking leaf checkboxes in multi mode toggles values."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(id="c", options=OPTIONS_2LEVEL, multi=True),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(_multi_values_joined)
    dash_duo.start_server(app)
    # Open and expand Asia
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-cascader-row").click()
    # Check Japan checkbox (second column, first row)
    checkboxes = dash_duo.driver.find_elements(
        "css selector", ".dash-cascader-column:nth-child(2) .dash-cascader-checkbox"
    )
    checkboxes[0].click()
    dash_duo.wait_for_text_to_equal("#out", "japan")
    # Panel still open
    assert dash_duo.find_element(".dash-cascader-content")
    assert dash_duo.get_logs() == []


def test_cascader_multi_shows_count_badge(dash_duo):
    """Trigger shows count badge when N > 1 values are selected."""
    app = _app(Cascader(id="c", options=OPTIONS_2LEVEL, multi=True, value=["japan", "france"]))
    dash_duo.start_server(app)
    dash_duo.wait_for_element(".dash-dropdown-value-count")
    badge_text = dash_duo.find_element(".dash-dropdown-value-count").text
    assert "2" in badge_text


def test_cascader_multi_select_all(dash_duo):
    """'Select all' adds all leaf values."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(id="c", options=OPTIONS_2LEVEL, multi=True),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(_multi_values_joined)
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-dropdown-action-button").click()
    dash_duo.wait_for_text_to_equal("#out", "china,france,germany,japan")
    assert dash_duo.get_logs() == []


def test_cascader_multi_deselect_all(dash_duo):
    """'Deselect all' removes all selected leaf values."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(id="c", options=OPTIONS_2LEVEL, multi=True, value=["japan", "france"]),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(_sorted_values_string)
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    buttons = dash_duo.driver.find_elements("css selector", ".dash-dropdown-action-button")
    buttons[1].click()  # "Deselect all"
    dash_duo.wait_for_text_to_equal("#out", "[]")
    assert dash_duo.get_logs() == []


# --- Search ---


def test_cascader_search_filters_results(dash_duo):
    """Typing in the search bar shows matching leaves and parent branches."""
    app = _app(Cascader(id="c", options=OPTIONS_2LEVEL))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-dropdown-search").send_keys("jap")
    dash_duo.wait_for_element(".dash-cascader-result-row")
    result_labels = [
        el.text for el in dash_duo.driver.find_elements("css selector", ".dash-cascader-row-label") if el.is_displayed()
    ]
    assert "Japan" in result_labels

    dash_duo.find_element(".dash-dropdown-search").clear()
    dash_duo.wait_for_element(".dash-dropdown-search").send_keys("asi")
    dash_duo.wait_for_element(".dash-cascader-result-row-branch")
    branch_labels = [
        el.text for el in dash_duo.driver.find_elements("css selector", ".dash-cascader-row-label") if el.is_displayed()
    ]
    assert "Asia" in branch_labels


def test_cascader_search_single_select_closes_on_pick(dash_duo):
    """Selecting a search result in single mode closes panel and clears search."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(id="c", options=OPTIONS_2LEVEL),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(str)
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-dropdown-search").send_keys("jap")
    dash_duo.wait_for_element(".dash-cascader-result-row").click()
    dash_duo.wait_for_text_to_equal("#out", "japan")
    panels = dash_duo.driver.find_elements("css selector", ".dash-cascader-content")
    assert len(panels) == 0


def test_cascader_search_branch_navigates_to_columns(dash_duo):
    """Clicking a branch search result clears search and opens the column view at that node."""
    app = _app(Cascader(id="c", options=OPTIONS_2LEVEL))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-dropdown-search").send_keys("asia")
    dash_duo.wait_for_element(".dash-cascader-result-row-branch").click()
    dash_duo.wait_for_element(".dash-cascader-columns")
    search = dash_duo.wait_for_element(".dash-dropdown-search")
    assert search.get_attribute("value") == ""
    labels_col2 = [
        el.text
        for el in dash_duo.driver.find_elements(
            "css selector", ".dash-cascader-column:nth-child(2) .dash-cascader-row-label"
        )
    ]
    assert "Japan" in labels_col2
    assert "China" in labels_col2
    assert dash_duo.get_logs() == []


def test_cascader_multi_select_all_search_only_leaves(dash_duo):
    """With an active search, Select all adds only leaf hits (not branch node values)."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(id="c", options=OPTIONS_2LEVEL, multi=True),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(_multi_values_joined)
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-dropdown-search").send_keys("a")
    dash_duo.wait_for_element(".dash-cascader-result-row-branch")
    dash_duo.wait_for_element(".dash-dropdown-action-button").click()
    dash_duo.wait_for_text_to_equal("#out", "china,france,germany,japan")
    assert dash_duo.get_logs() == []


# --- 3-level nesting ---


def test_cascader_three_levels(dash_duo):
    """Component correctly renders 3 levels of nesting."""
    app = _app(Cascader(id="c", options=OPTIONS_3LEVEL))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    # Expand Asia
    dash_duo.wait_for_element(".dash-cascader-row").click()
    # Expand East Asia
    rows = dash_duo.driver.find_elements("css selector", ".dash-cascader-column:nth-child(2) .dash-cascader-row")
    rows[0].click()
    # Third column should show Japan
    dash_duo.wait_for_text_to_equal(".dash-cascader-column:nth-child(3) .dash-cascader-row-label", "Japan")
    assert dash_duo.get_logs() == []


# --- shorthand options format ---


def test_cascader_shorthand_dict_list(dash_duo):
    """Dict-of-lists shorthand: keys become parents; string leaves use the same string as value."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(id="c", options=OPTIONS_SHORTHAND_DICT_LIST),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(str)
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_text_to_equal(
        ".dash-cascader-column:first-child .dash-cascader-row:first-child .dash-cascader-row-label", "Asia"
    )
    # Expand Asia and select Japan (value is the leaf string, not slugified)
    dash_duo.wait_for_element(".dash-cascader-row").click()
    rows = dash_duo.driver.find_elements("css selector", ".dash-cascader-column:nth-child(2) .dash-cascader-row")
    rows[0].click()
    dash_duo.wait_for_text_to_equal("#out", "Japan")
    assert dash_duo.get_logs() == []


def test_cascader_shorthand_nested_dict(dash_duo):
    """Nested dict shorthand produces multi-level tree; leaf selection returns the scalar value."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(id="c", options=OPTIONS_SHORTHAND_NESTED),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(str)
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-cascader-row").click()  # Europe
    rows = dash_duo.driver.find_elements("css selector", ".dash-cascader-column:nth-child(2) .dash-cascader-row")
    rows[0].click()  # Western
    dash_duo.wait_for_text_to_equal(
        ".dash-cascader-column:nth-child(3) .dash-cascader-row:first-child .dash-cascader-row-label", "France"
    )
    dash_duo.driver.find_elements("css selector", ".dash-cascader-column:nth-child(3) .dash-cascader-row")[0].click()
    dash_duo.wait_for_text_to_equal("#out", "France")
    assert dash_duo.get_logs() == []


def test_cascader_shorthand_mixed_list_option_dicts_and_scalars(dash_duo):
    """List items can mix full option dicts (passed through) with scalar leaves."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(id="c", options=OPTIONS_SHORTHAND_MIXED_LEAVES),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(str)
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-cascader-row").click()  # Asia
    rows = dash_duo.driver.find_elements("css selector", ".dash-cascader-column:nth-child(2) .dash-cascader-row")
    rows[0].click()  # Nippon → value japan
    dash_duo.wait_for_text_to_equal("#out", "japan")
    # Re-open and pick scalar leaf China
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-cascader-row").click()
    rows = dash_duo.driver.find_elements("css selector", ".dash-cascader-column:nth-child(2) .dash-cascader-row")
    rows[1].click()
    dash_duo.wait_for_text_to_equal("#out", "China")
    assert dash_duo.get_logs() == []


def test_cascader_shorthand_numeric_leaves(dash_duo):
    """Numeric scalars in shorthand lists keep their type as option value."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(id="c", options=OPTIONS_SHORTHAND_NUMERIC),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(str)
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-cascader-row").click()  # Series
    dash_duo.wait_for_text_to_equal(
        ".dash-cascader-column:nth-child(2) .dash-cascader-row:first-child .dash-cascader-row-label", "10"
    )
    dash_duo.driver.find_elements("css selector", ".dash-cascader-column:nth-child(2) .dash-cascader-row")[0].click()
    dash_duo.wait_for_text_to_equal("#out", "10")
    assert dash_duo.get_logs() == []


def test_cascader_shorthand_multi_select(dash_duo):
    """Multi-select works with dict-of-lists shorthand (values are leaf scalars)."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(id="c", options=OPTIONS_SHORTHAND_DICT_LIST, multi=True),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(_multi_values_joined)
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-cascader-row").click()  # Asia
    checks = dash_duo.driver.find_elements("css selector", ".dash-cascader-column:nth-child(2) .dash-cascader-checkbox")
    checks[0].click()  # Japan
    checks[1].click()  # China
    dash_duo.wait_for_text_to_equal("#out", "China,Japan")
    assert dash_duo.get_logs() == []


def test_cascader_shorthand_search_finds_normalized_leaves(dash_duo):
    """Search over shorthand-normalized tree matches leaf labels."""
    app = _app(Cascader(id="c", options=OPTIONS_SHORTHAND_DICT_LIST))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-dropdown-search").send_keys("Germ")
    dash_duo.wait_for_element(".dash-cascader-result-row")
    labels = [
        el.text for el in dash_duo.driver.find_elements("css selector", ".dash-cascader-row-label") if el.is_displayed()
    ]
    assert "Germany" in labels
    assert dash_duo.get_logs() == []


# --- search field on options ---


def test_cascader_option_search_field_used_for_filtering(dash_duo):
    """Search field overrides label for search matching; parent search can match branches."""
    options = [
        {
            "label": "Asia",
            "value": "asia",
            "search": "east-region",
            "children": [
                {"label": "Japan", "value": "japan", "search": "nippon"},
            ],
        }
    ]
    app = _app(Cascader(id="c", options=options))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    # "nippon" matches via search field, not label
    dash_duo.wait_for_element(".dash-dropdown-search").send_keys("nippon")
    dash_duo.wait_for_element(".dash-cascader-result-row")
    labels = [
        el.text for el in dash_duo.driver.find_elements("css selector", ".dash-cascader-row-label") if el.is_displayed()
    ]
    assert "Japan" in labels
    # "japan" does NOT match (search field replaces label matching)
    dash_duo.find_element(".dash-dropdown-search").clear()
    dash_duo.wait_for_element(".dash-dropdown-search").send_keys("japan")
    import time

    time.sleep(0.3)
    results = dash_duo.driver.find_elements("css selector", ".dash-cascader-result-row")
    assert len(results) == 0

    dash_duo.find_element(".dash-dropdown-search").clear()
    dash_duo.wait_for_element(".dash-dropdown-search").send_keys("east-region")
    dash_duo.wait_for_element(".dash-cascader-result-row-branch").click()
    dash_duo.wait_for_element(".dash-cascader-columns")
    dash_duo.wait_for_text_to_equal(".dash-cascader-column:nth-child(2) .dash-cascader-row-label", "Japan")
    assert dash_duo.get_logs() == []


# --- style, optionHeight, debounce ---


def test_cascader_style_applied_to_wrapper(dash_duo):
    """Style prop is applied inline to the wrapper div."""
    app = _app(Cascader(id="c", options=OPTIONS_2LEVEL, style={"width": "400px"}))
    dash_duo.start_server(app)
    wrapper = dash_duo.wait_for_element(".dash-cascader-wrapper")
    assert "400px" in wrapper.get_attribute("style")
    assert dash_duo.get_logs() == []


def test_cascader_option_height_applied_to_rows(dash_duo):
    """OptionHeight sets a fixed pixel height on each option row."""
    app = _app(Cascader(id="c", options=OPTIONS_2LEVEL, optionHeight=50))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    row = dash_duo.wait_for_element(".dash-cascader-row")
    style = row.get_attribute("style")
    assert "50px" in style
    assert dash_duo.get_logs() == []


def test_cascader_debounce_defers_callback(dash_duo):
    """With debounce=True, the callback is not fired until the panel closes."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(id="c", options=OPTIONS_2LEVEL, debounce=True),
                html.Div(id="out", children="initial"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(str)
    dash_duo.start_server(app)
    # Open and select a leaf
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-cascader-row").click()  # Asia
    rows = dash_duo.driver.find_elements("css selector", ".dash-cascader-column:nth-child(2) .dash-cascader-row")
    rows[0].click()  # Japan — panel closes immediately in single mode, committing the value
    dash_duo.wait_for_text_to_equal("#out", "japan")
    assert dash_duo.get_logs() == []


def test_cascader_debounce_multi_defers_until_close(dash_duo):
    """With debounce=True and multi=True, callback fires only when panel closes."""
    import time

    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                html.Div("outside", id="outside"),
                Cascader(id="c", options=OPTIONS_2LEVEL, multi=True, debounce=True),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(_multi_values_joined)
    dash_duo.start_server(app)
    # Open and check Japan
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-cascader-row").click()  # Asia
    checkboxes = dash_duo.driver.find_elements(
        "css selector", ".dash-cascader-column:nth-child(2) .dash-cascader-checkbox"
    )
    checkboxes[0].click()  # Japan
    # Callback should NOT have fired yet (still empty from initial render)
    time.sleep(0.5)
    assert dash_duo.find_element("#out").text == ""
    # Close by clicking outside — now it fires
    dash_duo.find_element("#outside").click()
    dash_duo.wait_for_text_to_equal("#out", "japan")
    assert dash_duo.get_logs() == []


# --- Props: searchable, clearable, disabled ---


def test_cascader_searchable_false_hides_search_bar(dash_duo):
    """searchable=False means no search input is rendered when the panel is open."""
    app = _app(Cascader(id="c", options=OPTIONS_2LEVEL, searchable=False))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-cascader-content")
    inputs = dash_duo.driver.find_elements("css selector", ".dash-dropdown-search")
    assert len(inputs) == 0
    assert dash_duo.get_logs() == []


def test_cascader_clearable_false_hides_clear_button(dash_duo):
    """clearable=False means the clear button is absent even when a value is set."""
    app = _app(Cascader(id="c", options=OPTIONS_2LEVEL, value="japan", clearable=False))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c")
    clears = dash_duo.driver.find_elements("css selector", "#c a.dash-dropdown-clear")
    assert len(clears) == 0
    assert dash_duo.get_logs() == []


def test_cascader_disabled_does_not_open(dash_duo):
    """Clicking a disabled trigger does not open the panel."""
    import time

    app = _app(Cascader(id="c", options=OPTIONS_2LEVEL, disabled=True))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c")
    # pointer-events: none blocks Selenium's native click, so use JS
    dash_duo.driver.execute_script("document.querySelector('#c').click()")
    time.sleep(0.3)
    panels = dash_duo.driver.find_elements("css selector", ".dash-cascader-content")
    assert len(panels) == 0
    assert dash_duo.get_logs() == []


# --- Keyboard: Escape ---


def test_cascader_escape_closes_panel(dash_duo):
    """Pressing Escape while the panel is open closes it."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    app = _app(Cascader(id="c", options=OPTIONS_2LEVEL))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-cascader-content")
    dash_duo.driver.find_element(By.CSS_SELECTOR, ".dash-dropdown-search").send_keys(Keys.ESCAPE)
    WebDriverWait(dash_duo.driver, 3).until(
        EC.invisibility_of_element_located((By.CSS_SELECTOR, ".dash-cascader-content"))
    )
    assert dash_duo.get_logs() == []


# --- Multi: parent checkbox, multi clear ---


def test_cascader_multi_parent_checkbox_selects_children(dash_duo):
    """Checking a parent checkbox in multi mode selects all its leaf children."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(id="c", options=OPTIONS_2LEVEL, multi=True),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(_multi_values_joined)
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    # Click the Asia parent checkbox (first row, first column)
    checkboxes = dash_duo.driver.find_elements(
        "css selector", ".dash-cascader-column:first-child .dash-cascader-checkbox"
    )
    checkboxes[0].click()
    dash_duo.wait_for_text_to_equal("#out", "china,japan")
    assert dash_duo.get_logs() == []


def test_cascader_multi_clear_resets_to_empty_list(dash_duo):
    """Clear button in multi mode resets value to [] (not null)."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(id="c", options=OPTIONS_2LEVEL, multi=True, value=["japan", "france"]),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(repr)
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c a.dash-dropdown-clear").click()
    dash_duo.wait_for_text_to_equal("#out", "[]")
    assert dash_duo.get_logs() == []


# --- Flat options ---


def test_cascader_flat_options(dash_duo):
    """Flat option list (no children) renders a single column and sets value on click."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(id="c", options=[{"label": "Red", "value": "red"}, {"label": "Blue", "value": "blue"}]),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(str)
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-cascader-row").click()
    dash_duo.wait_for_text_to_equal("#out", "red")
    panels = dash_duo.driver.find_elements("css selector", ".dash-cascader-content")
    assert len(panels) == 0
    assert dash_duo.get_logs() == []


# --- Programmatic value update ---


def test_cascader_programmatic_value_update(dash_duo):
    """Value driven from a callback (externally) is reflected in the trigger."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                html.Button("Set Japan", id="btn"),
                Cascader(id="c", options=OPTIONS_2LEVEL),
            ]
        )
    )
    app.callback(Output("c", "value"), Input("btn", "n_clicks"), prevent_initial_call=True)(lambda n: "japan")
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#c .dash-dropdown-value", "Japan")
    assert dash_duo.get_logs() == []


# --- Search: select/deselect all scoped to results ---


def test_cascader_multi_select_all_scoped_to_search(dash_duo):
    """'Select all' when searching adds only the filtered leaf values."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(id="c", options=OPTIONS_2LEVEL, multi=True),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(_multi_values_joined)
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-dropdown-search").send_keys("jap")
    dash_duo.wait_for_element(".dash-cascader-result-row")
    dash_duo.wait_for_element(".dash-dropdown-action-button").click()  # Select all (filtered)
    dash_duo.wait_for_text_to_equal("#out", "japan")
    assert dash_duo.get_logs() == []


# --- Persistence ---


def test_cascader_persistence(dash_duo):
    """Value persists across page reload when persistence=True."""
    app = _app(Cascader(id="c", options=OPTIONS_2LEVEL, persistence=True))
    dash_duo.start_server(app)

    # Open panel and select Japan (Asia > Japan)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-cascader-row").click()  # Asia
    rows = dash_duo.driver.find_elements("css selector", ".dash-cascader-column:nth-child(2) .dash-cascader-row")
    rows[0].click()  # Japan
    dash_duo.wait_for_text_to_equal("#c .dash-dropdown-value", "Japan")

    # Reload and check value is restored
    dash_duo.driver.refresh()
    dash_duo.wait_for_element("#c")
    dash_duo.wait_for_text_to_equal("#c .dash-dropdown-value", "Japan")
    assert dash_duo.get_logs() == []
