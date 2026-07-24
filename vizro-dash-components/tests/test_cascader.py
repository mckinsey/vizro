"""Tests for the vizro_dash_components.Cascader component.

The Cascader has two mutually-exclusive, permanently-supported value modes selected by the
`full_path` prop (default `False`):

* LEAF MODE (`full_path=False`, default): `value` is a bare leaf scalar (single-select) or a list
  of leaf scalars (multi-select), exactly like the pre-0.2 component. Duplicate leaf labels across
  branches are ambiguous and unsupported (the component logs a console error).
* PATH MODE (`full_path=True`): `value` is a full root-to-leaf path (single-select) or a list of
  such paths (multi-select). Duplicate leaf labels across branches are addressed unambiguously.

Value-sensitive tests are parametrized over both modes. `_single_value`/`_multi_value` build the
mode-appropriate wire value from a canonical path, and the `*_fmt` helpers format the component's
emitted `value` back to a stable string for assertions.
"""

import dash_mantine_components as dmc
import pytest
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

# Duplicate leaf labels across branches: legal only in PATH MODE, where identity is the full path.
# "Portland" appears under both "North" and "South". In LEAF MODE this is ambiguous (console error).
OPTIONS_DUPLICATE_LEAVES = {"North": ["Portland", "Salem"], "South": ["Portland", "Austin"]}

# Boolean leaf values are supported (Vizro allows bool leaves).
OPTIONS_BOOL_LEAVES = {"Flags": [True, False]}

# The first matching leaf for "ja" ("Japan") is disabled; "Jakarta" is enabled.
OPTIONS_DISABLED_FIRST_LEAF = [
    {
        "label": "Asia",
        "value": "asia",
        "children": [
            {"label": "Japan", "value": "japan", "disabled": True},
            {"label": "Jakarta", "value": "jakarta"},
        ],
    },
]


def _app(layout):
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(layout)
    return app


# --- Mode-aware value builders and formatters ---


def _single_value(full_path, path):
    """Build a single-select wire value from a canonical path: full path (path mode) or leaf (leaf mode)."""
    return list(path) if full_path else path[-1]


def _multi_value(full_path, paths):
    """Build a multi-select wire value from canonical paths: list of paths (path mode) or leaves (leaf mode)."""
    return [list(p) for p in paths] if full_path else [p[-1] for p in paths]


def _single_leaf_fmt(v):
    """Format a single-select LEAF-mode value (a scalar). `None` -> "None"; `[]` -> "[]" (regression guard)."""
    if v is None:
        return "None"
    if isinstance(v, list):
        return "[]" if not v else "/".join(str(s) for s in v)
    return str(v)


def _single_path_fmt(v):
    """Format a single-select PATH-mode value (one path). Distinguishes `None` from `[]`."""
    if v is None:
        return "None"
    return "/".join(str(s) for s in v)


def _multi_leaf_fmt(v):
    """Format a multi-select LEAF-mode value (list of scalars), order-independent."""
    return " | ".join(sorted(str(x) for x in (v or [])))


def _multi_path_fmt(v):
    """Format a multi-select PATH-mode value (list of paths), order-independent."""
    return " | ".join(sorted("/".join(str(s) for s in path) for path in (v or [])))


def _single_fmt(full_path):
    return _single_path_fmt if full_path else _single_leaf_fmt


def _multi_fmt(full_path):
    return _multi_path_fmt if full_path else _multi_leaf_fmt


def _sorted_values_string(v):
    return str(sorted(v or []))


# --- Render / open / close (mode-agnostic) ---


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


@pytest.mark.parametrize("full_path", [False, True])
def test_cascader_keyboard_backspace_on_trigger_clears(dash_duo, full_path):
    """Backspace on the focused trigger clears selection when clearable (dcc.Dropdown parity)."""
    from selenium.webdriver.common.keys import Keys

    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(
                    id="c",
                    options=OPTIONS_2LEVEL,
                    full_path=full_path,
                    value=_single_value(full_path, ["asia", "japan"]),
                ),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(_single_fmt(full_path))
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


@pytest.mark.parametrize("full_path", [False, True])
def test_cascader_single_select_leaf(dash_duo, full_path):
    """Clicking a leaf in single mode sets the value (leaf or path per mode) and closes the panel."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(id="c", options=OPTIONS_2LEVEL, full_path=full_path),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(_single_fmt(full_path))
    dash_duo.start_server(app)
    # Open
    dash_duo.wait_for_element("#c").click()
    # Click "Asia" to expand
    dash_duo.wait_for_element(".dash-cascader-row").click()
    # Click "Japan" (leaf in second column)
    rows = dash_duo.driver.find_elements("css selector", ".dash-cascader-column:nth-child(2) .dash-cascader-row")
    rows[0].click()
    # Panel closes, value updated
    dash_duo.wait_for_text_to_equal("#out", "asia/japan" if full_path else "japan")
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


@pytest.mark.parametrize("full_path", [False, True])
def test_cascader_single_select_shows_label_in_trigger(dash_duo, full_path):
    """Selected leaf label is shown in the trigger (same label in both modes)."""
    app = _app(
        Cascader(id="c", options=OPTIONS_2LEVEL, full_path=full_path, value=_single_value(full_path, ["asia", "japan"]))
    )
    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#c .dash-dropdown-value", "Japan")


@pytest.mark.parametrize("full_path", [False, True])
def test_cascader_single_clear(dash_duo, full_path):
    """Clicking the clear button sets value to null."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(
                    id="c",
                    options=OPTIONS_2LEVEL,
                    full_path=full_path,
                    value=_single_value(full_path, ["asia", "japan"]),
                ),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(_single_fmt(full_path))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c button.dash-dropdown-clear").click()
    dash_duo.wait_for_text_to_equal("#out", "None")


# --- Multi-select ---


@pytest.mark.parametrize("full_path", [False, True])
def test_cascader_multi_select_leaf(dash_duo, full_path):
    """Clicking leaf checkboxes in multi mode toggles values (leaf or path per mode)."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(id="c", options=OPTIONS_2LEVEL, multi=True, full_path=full_path),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(_multi_fmt(full_path))
    dash_duo.start_server(app)
    # Open and expand Asia
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-cascader-row").click()
    # Check Japan checkbox (second column, first row)
    checkboxes = dash_duo.driver.find_elements(
        "css selector", ".dash-cascader-column:nth-child(2) .dash-cascader-checkbox"
    )
    checkboxes[0].click()
    dash_duo.wait_for_text_to_equal("#out", "asia/japan" if full_path else "japan")
    # Panel still open
    assert dash_duo.find_element(".dash-cascader-content")
    assert dash_duo.get_logs() == []


@pytest.mark.parametrize("full_path", [False, True])
def test_cascader_multi_shows_count_badge(dash_duo, full_path):
    """Trigger shows count badge when N > 1 values are selected."""
    app = _app(
        Cascader(
            id="c",
            options=OPTIONS_2LEVEL,
            multi=True,
            full_path=full_path,
            value=_multi_value(full_path, [["asia", "japan"], ["europe", "france"]]),
        )
    )
    dash_duo.start_server(app)
    dash_duo.wait_for_element(".dash-dropdown-value-count")
    badge_text = dash_duo.find_element(".dash-dropdown-value-count").text
    assert "2" in badge_text


@pytest.mark.parametrize("full_path", [False, True])
def test_cascader_multi_select_all(dash_duo, full_path):
    """'Select all' adds all leaf values."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(id="c", options=OPTIONS_2LEVEL, multi=True, full_path=full_path),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(_multi_fmt(full_path))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-dropdown-action-button").click()
    expected = (
        "asia/china | asia/japan | europe/france | europe/germany" if full_path else "china | france | germany | japan"
    )
    dash_duo.wait_for_text_to_equal("#out", expected)
    assert dash_duo.get_logs() == []


@pytest.mark.parametrize("full_path", [False, True])
def test_cascader_multi_deselect_all(dash_duo, full_path):
    """'Deselect all' removes all selected leaf values."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(
                    id="c",
                    options=OPTIONS_2LEVEL,
                    multi=True,
                    full_path=full_path,
                    value=_multi_value(full_path, [["asia", "japan"], ["europe", "france"]]),
                ),
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


# --- Search (display is mode-agnostic) ---


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


@pytest.mark.parametrize("full_path", [False, True])
def test_cascader_search_single_select_closes_on_pick(dash_duo, full_path):
    """Selecting a search result in single mode closes panel and clears search."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(id="c", options=OPTIONS_2LEVEL, full_path=full_path),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(_single_fmt(full_path))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-dropdown-search").send_keys("jap")
    dash_duo.wait_for_element(".dash-cascader-result-row").click()
    dash_duo.wait_for_text_to_equal("#out", "asia/japan" if full_path else "japan")
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


@pytest.mark.parametrize("full_path", [False, True])
def test_cascader_multi_select_all_search_only_leaves(dash_duo, full_path):
    """With an active search, Select all adds only leaf hits (not branch node values)."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(id="c", options=OPTIONS_2LEVEL, multi=True, full_path=full_path),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(_multi_fmt(full_path))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-dropdown-search").send_keys("a")
    dash_duo.wait_for_element(".dash-cascader-result-row-branch")
    dash_duo.wait_for_element(".dash-dropdown-action-button").click()
    expected = (
        "asia/china | asia/japan | europe/france | europe/germany" if full_path else "china | france | germany | japan"
    )
    dash_duo.wait_for_text_to_equal("#out", expected)
    assert dash_duo.get_logs() == []


# --- 3-level nesting (mode-agnostic navigation) ---


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


def test_cascader_collapse_top_level_closes_whole_branch(dash_duo):
    """Clicking an expanded top-level parent collapses the full branch, not only the deepest column."""
    app = _app(Cascader(id="c", options=OPTIONS_3LEVEL))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-cascader-column:nth-child(1) .dash-cascader-row").click()  # Asia
    rows = dash_duo.driver.find_elements("css selector", ".dash-cascader-column:nth-child(2) .dash-cascader-row")
    rows[0].click()  # East Asia
    dash_duo.wait_for_text_to_equal(".dash-cascader-column:nth-child(3) .dash-cascader-row-label", "Japan")
    assert len(dash_duo.driver.find_elements("css selector", ".dash-cascader-column")) == 3
    # Click Asia in column 1 again: expect root-only (one column), not Asia + East Asia still open.
    dash_duo.driver.find_element("css selector", ".dash-cascader-column:nth-child(1) .dash-cascader-row").click()
    cols_after = dash_duo.driver.find_elements("css selector", ".dash-cascader-column")
    assert len(cols_after) == 1
    assert dash_duo.get_logs() == []


# --- shorthand options format ---


@pytest.mark.parametrize("full_path", [False, True])
def test_cascader_shorthand_dict_list(dash_duo, full_path):
    """Dict-of-lists shorthand: keys become parents; string leaves use the same string as value."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(id="c", options=OPTIONS_SHORTHAND_DICT_LIST, full_path=full_path),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(_single_fmt(full_path))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_text_to_equal(
        ".dash-cascader-column:first-child .dash-cascader-row:first-child .dash-cascader-row-label", "Asia"
    )
    # Expand Asia and select Japan (value is the leaf string, not slugified)
    dash_duo.wait_for_element(".dash-cascader-row").click()
    rows = dash_duo.driver.find_elements("css selector", ".dash-cascader-column:nth-child(2) .dash-cascader-row")
    rows[0].click()
    dash_duo.wait_for_text_to_equal("#out", "Asia/Japan" if full_path else "Japan")
    assert dash_duo.get_logs() == []


@pytest.mark.parametrize("full_path", [False, True])
def test_cascader_shorthand_nested_dict(dash_duo, full_path):
    """Nested dict shorthand produces multi-level tree; leaf selection returns the scalar value."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(id="c", options=OPTIONS_SHORTHAND_NESTED, full_path=full_path),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(_single_fmt(full_path))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-cascader-row").click()  # Europe
    rows = dash_duo.driver.find_elements("css selector", ".dash-cascader-column:nth-child(2) .dash-cascader-row")
    rows[0].click()  # Western
    dash_duo.wait_for_text_to_equal(
        ".dash-cascader-column:nth-child(3) .dash-cascader-row:first-child .dash-cascader-row-label", "France"
    )
    dash_duo.driver.find_elements("css selector", ".dash-cascader-column:nth-child(3) .dash-cascader-row")[0].click()
    dash_duo.wait_for_text_to_equal("#out", "Europe/Western/France" if full_path else "France")
    assert dash_duo.get_logs() == []


@pytest.mark.parametrize("full_path", [False, True])
def test_cascader_shorthand_mixed_list_option_dicts_and_scalars(dash_duo, full_path):
    """List items can mix full option dicts (passed through) with scalar leaves."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(id="c", options=OPTIONS_SHORTHAND_MIXED_LEAVES, full_path=full_path),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(_single_fmt(full_path))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-cascader-row").click()  # Asia
    rows = dash_duo.driver.find_elements("css selector", ".dash-cascader-column:nth-child(2) .dash-cascader-row")
    rows[0].click()  # Nippon → leaf value "japan"
    dash_duo.wait_for_text_to_equal("#out", "Asia/japan" if full_path else "japan")
    # Re-open: activePath still has Asia expanded; clicking col1 would collapse it.
    dash_duo.wait_for_element("#c").click()
    rows = dash_duo.driver.find_elements("css selector", ".dash-cascader-column:nth-child(2) .dash-cascader-row")
    assert len(rows) >= 2
    rows[1].click()
    dash_duo.wait_for_text_to_equal("#out", "Asia/China" if full_path else "China")
    assert dash_duo.get_logs() == []


@pytest.mark.parametrize("full_path", [False, True])
def test_cascader_shorthand_numeric_leaves(dash_duo, full_path):
    """Numeric scalars in shorthand lists keep their type as option value."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(id="c", options=OPTIONS_SHORTHAND_NUMERIC, full_path=full_path),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(_single_fmt(full_path))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-cascader-row").click()  # Series
    dash_duo.wait_for_text_to_equal(
        ".dash-cascader-column:nth-child(2) .dash-cascader-row:first-child .dash-cascader-row-label", "10"
    )
    dash_duo.driver.find_elements("css selector", ".dash-cascader-column:nth-child(2) .dash-cascader-row")[0].click()
    dash_duo.wait_for_text_to_equal("#out", "Series/10" if full_path else "10")
    assert dash_duo.get_logs() == []


@pytest.mark.parametrize("full_path", [False, True])
def test_cascader_shorthand_multi_select(dash_duo, full_path):
    """Multi-select works with dict-of-lists shorthand."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(id="c", options=OPTIONS_SHORTHAND_DICT_LIST, multi=True, full_path=full_path),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(_multi_fmt(full_path))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-cascader-row").click()  # Asia
    checks = dash_duo.driver.find_elements("css selector", ".dash-cascader-column:nth-child(2) .dash-cascader-checkbox")
    checks[0].click()  # Japan
    checks[1].click()  # China
    dash_duo.wait_for_text_to_equal("#out", "Asia/China | Asia/Japan" if full_path else "China | Japan")
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


# --- search field on options (mode-agnostic) ---


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


@pytest.mark.parametrize("full_path", [False, True])
def test_cascader_debounce_defers_callback(dash_duo, full_path):
    """With debounce=True, single-select still commits immediately when the panel closes on pick."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(id="c", options=OPTIONS_2LEVEL, debounce=True, full_path=full_path),
                html.Div(id="out", children="initial"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(_single_fmt(full_path))
    dash_duo.start_server(app)
    # Open and select a leaf
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-cascader-row").click()  # Asia
    rows = dash_duo.driver.find_elements("css selector", ".dash-cascader-column:nth-child(2) .dash-cascader-row")
    rows[0].click()  # Japan — panel closes immediately in single mode, committing the value
    dash_duo.wait_for_text_to_equal("#out", "asia/japan" if full_path else "japan")
    assert dash_duo.get_logs() == []


@pytest.mark.parametrize("full_path", [False, True])
def test_cascader_debounce_multi_defers_until_close(dash_duo, full_path):
    """With debounce=True and multi=True, callback fires only when panel closes."""
    import time

    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                html.Div("outside", id="outside"),
                Cascader(id="c", options=OPTIONS_2LEVEL, multi=True, debounce=True, full_path=full_path),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(_multi_fmt(full_path))
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
    dash_duo.wait_for_text_to_equal("#out", "asia/japan" if full_path else "japan")
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


@pytest.mark.parametrize("full_path", [False, True])
def test_cascader_clearable_false_hides_clear_button(dash_duo, full_path):
    """clearable=False means the clear button is absent even when a value is set."""
    app = _app(
        Cascader(
            id="c",
            options=OPTIONS_2LEVEL,
            full_path=full_path,
            value=_single_value(full_path, ["asia", "japan"]),
            clearable=False,
        )
    )
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c")
    clears = dash_duo.driver.find_elements("css selector", "#c button.dash-dropdown-clear")
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


# --- Keyboard navigation: not-searchable, action buttons, clear button ---


def test_cascader_not_searchable_arrow_down_focuses_option(dash_duo):
    """With searchable=False, opening focuses the panel so ArrowDown moves into the options."""
    import time

    from selenium.webdriver.common.keys import Keys

    app = _app(Cascader(id="c", options=OPTIONS_2LEVEL, searchable=False))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-cascader-content")
    time.sleep(0.25)  # allow the on-open focus (requestAnimationFrame) to land on the panel
    # ArrowDown on whatever is focused after open must move focus onto the first option row,
    # rather than being lost on the trigger (the pre-fix behavior with no search input).
    dash_duo.driver.switch_to.active_element.send_keys(Keys.ARROW_DOWN)
    active = dash_duo.driver.switch_to.active_element
    assert "dash-cascader-kbd-row" in (active.get_attribute("class") or "")
    assert dash_duo.get_logs() == []


def test_cascader_action_buttons_arrow_navigation(dash_duo):
    """Select All / Deselect All: Left/Right move between them; ArrowDown jumps to the options."""
    from selenium.webdriver.common.keys import Keys

    app = _app(Cascader(id="c", options=OPTIONS_2LEVEL, multi=True))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-dropdown-action-button")
    buttons = dash_duo.driver.find_elements("css selector", ".dash-dropdown-action-button")
    assert [b.text for b in buttons] == ["Select All", "Deselect All"]

    # ArrowRight from Select All focuses Deselect All (horizontal group).
    dash_duo.driver.execute_script("arguments[0].focus();", buttons[0])
    buttons[0].send_keys(Keys.ARROW_RIGHT)
    assert dash_duo.driver.switch_to.active_element.text == "Deselect All"
    # ArrowLeft goes back to Select All.
    dash_duo.driver.switch_to.active_element.send_keys(Keys.ARROW_LEFT)
    assert dash_duo.driver.switch_to.active_element.text == "Select All"

    # ArrowDown from Select All leaves the group and focuses the first option (a checkbox), not
    # the sibling Deselect All button.
    dash_duo.driver.switch_to.active_element.send_keys(Keys.ARROW_DOWN)
    active = dash_duo.driver.switch_to.active_element
    assert active.get_attribute("type") == "checkbox"
    assert dash_duo.get_logs() == []


def test_cascader_clear_button_enter_clears_without_opening(dash_duo):
    """Enter on the focused clear button clears the selection and does not open the panel."""
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
    app.callback(Output("out", "children"), Input("c", "value"))(_single_leaf_fmt)
    dash_duo.start_server(app)
    clear = dash_duo.wait_for_element("#c button.dash-dropdown-clear")
    dash_duo.driver.execute_script("arguments[0].focus();", clear)
    clear.send_keys(Keys.ENTER)
    dash_duo.wait_for_text_to_equal("#out", "None")
    # The panel must not have opened as a side effect of the Enter keypress.
    assert not dash_duo.driver.find_elements("css selector", ".dash-cascader-content")
    assert dash_duo.get_logs() == []


# --- Multi: parent checkbox, multi clear ---


@pytest.mark.parametrize("full_path", [False, True])
def test_cascader_multi_parent_checkbox_selects_children(dash_duo, full_path):
    """Checking a parent checkbox in multi mode selects all its leaf children."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(id="c", options=OPTIONS_2LEVEL, multi=True, full_path=full_path),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(_multi_fmt(full_path))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    # Click the Asia parent checkbox (first row, first column)
    checkboxes = dash_duo.driver.find_elements(
        "css selector", ".dash-cascader-column:first-child .dash-cascader-checkbox"
    )
    checkboxes[0].click()
    dash_duo.wait_for_text_to_equal("#out", "asia/china | asia/japan" if full_path else "china | japan")
    assert dash_duo.get_logs() == []


@pytest.mark.parametrize("full_path", [False, True])
def test_cascader_multi_clear_resets_to_empty_list(dash_duo, full_path):
    """Clear button in multi mode resets value to [] (not null)."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(
                    id="c",
                    options=OPTIONS_2LEVEL,
                    multi=True,
                    full_path=full_path,
                    value=_multi_value(full_path, [["asia", "japan"], ["europe", "france"]]),
                ),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(repr)
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c button.dash-dropdown-clear").click()
    dash_duo.wait_for_text_to_equal("#out", "[]")
    assert dash_duo.get_logs() == []


# --- Flat options ---


@pytest.mark.parametrize("full_path", [False, True])
def test_cascader_flat_options(dash_duo, full_path):
    """Flat option list (no children) renders a single column and sets value on click."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(
                    id="c",
                    options=[{"label": "Red", "value": "red"}, {"label": "Blue", "value": "blue"}],
                    full_path=full_path,
                ),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(_single_fmt(full_path))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-cascader-row").click()
    # A flat leaf's path is just the leaf itself, so leaf and path modes coincide here.
    dash_duo.wait_for_text_to_equal("#out", "red")
    panels = dash_duo.driver.find_elements("css selector", ".dash-cascader-content")
    assert len(panels) == 0
    assert dash_duo.get_logs() == []


# --- Programmatic value update ---


@pytest.mark.parametrize("full_path", [False, True])
def test_cascader_programmatic_value_update(dash_duo, full_path):
    """Value driven from a callback (externally) is reflected in the trigger."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                html.Button("Set Japan", id="btn"),
                Cascader(id="c", options=OPTIONS_2LEVEL, full_path=full_path),
            ]
        )
    )
    new_value = _single_value(full_path, ["asia", "japan"])
    app.callback(Output("c", "value"), Input("btn", "n_clicks"), prevent_initial_call=True)(lambda n: new_value)
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#c .dash-dropdown-value", "Japan")
    assert dash_duo.get_logs() == []


# --- Search: select/deselect all scoped to results ---


@pytest.mark.parametrize("full_path", [False, True])
def test_cascader_multi_select_all_scoped_to_search(dash_duo, full_path):
    """'Select all' when searching adds only the filtered leaf values."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(id="c", options=OPTIONS_2LEVEL, multi=True, full_path=full_path),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(_multi_fmt(full_path))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-dropdown-search").send_keys("jap")
    dash_duo.wait_for_element(".dash-cascader-result-row")
    dash_duo.wait_for_element(".dash-dropdown-action-button").click()  # Select all (filtered)
    dash_duo.wait_for_text_to_equal("#out", "asia/japan" if full_path else "japan")
    assert dash_duo.get_logs() == []


# --- Persistence ---


@pytest.mark.parametrize("full_path", [False, True])
def test_cascader_persistence(dash_duo, full_path):
    """Value persists across page reload when persistence=True."""
    app = _app(Cascader(id="c", options=OPTIONS_2LEVEL, persistence=True, full_path=full_path))
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


# --- LEAF MODE: round-trip and duplicate-leaf handling ---


def test_cascader_leaf_mode_multi_round_trip(dash_duo):
    """Leaf mode: a preset list of leaf scalars renders, and toggling emits leaf scalars (round-trip)."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(id="c", options=OPTIONS_2LEVEL, multi=True, value=["japan", "france"]),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(_multi_leaf_fmt)
    dash_duo.start_server(app)
    # Preset value round-trips to the exact leaf scalars.
    dash_duo.wait_for_text_to_equal("#out", "france | japan")
    # Deselect France by unchecking it via the trigger clear-less path: open, expand Europe, uncheck France.
    dash_duo.wait_for_element("#c").click()
    col1 = dash_duo.driver.find_elements("css selector", ".dash-cascader-column:nth-child(1) .dash-cascader-row")
    col1[1].click()  # Europe
    checks = dash_duo.driver.find_elements("css selector", ".dash-cascader-column:nth-child(2) .dash-cascader-checkbox")
    checks[0].click()  # uncheck France
    dash_duo.wait_for_text_to_equal("#out", "japan")
    assert dash_duo.get_logs() == []


def test_cascader_leaf_mode_duplicate_leaves_logs_error(dash_duo):
    """Leaf mode with duplicate leaf values logs a console error (ambiguous) but does not crash."""
    app = _app(Cascader(id="c", options=OPTIONS_DUPLICATE_LEAVES))  # full_path defaults to False
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-cascader-content")
    logs = dash_duo.get_logs()
    assert any("duplicate" in (entry.get("message", "").lower()) for entry in logs), logs


# --- PATH MODE: duplicate leaf labels across branches (path identity) ---


def test_cascader_duplicate_leaf_labels_select_independently(dash_duo):
    """Path mode: duplicate leaf labels under different branches select independently via full-path identity."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(id="c", options=OPTIONS_DUPLICATE_LEAVES, full_path=True),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(_single_path_fmt)
    dash_duo.start_server(app)
    # Portland under North.
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-cascader-column:nth-child(1) .dash-cascader-row").click()  # North
    dash_duo.wait_for_element(".dash-cascader-column:nth-child(2) .dash-cascader-row")
    dash_duo.driver.find_elements("css selector", ".dash-cascader-column:nth-child(2) .dash-cascader-row")[
        0
    ].click()  # Portland (North)
    dash_duo.wait_for_text_to_equal("#out", "North/Portland")
    # Portland under South is a distinct selection with a distinct path.
    dash_duo.wait_for_element("#c").click()
    col1_rows = dash_duo.driver.find_elements("css selector", ".dash-cascader-column:nth-child(1) .dash-cascader-row")
    col1_rows[1].click()  # South
    # "Austin" is unique to South's column, so wait on it to confirm the column switched.
    dash_duo.wait_for_text_to_equal(
        ".dash-cascader-column:nth-child(2) .dash-cascader-row:nth-child(2) .dash-cascader-row-label", "Austin"
    )
    dash_duo.driver.find_elements("css selector", ".dash-cascader-column:nth-child(2) .dash-cascader-row")[
        0
    ].click()  # Portland (South)
    dash_duo.wait_for_text_to_equal("#out", "South/Portland")
    assert dash_duo.get_logs() == []


def test_cascader_search_duplicate_leaf_labels_distinct_rows(dash_duo):
    """Path mode: search over duplicate labels yields one distinct row per leaf, disambiguated by breadcrumb."""
    app = _app(Cascader(id="c", options=OPTIONS_DUPLICATE_LEAVES, full_path=True))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-dropdown-search").send_keys("Portland")
    dash_duo.wait_for_element(".dash-cascader-result-row")
    rows = dash_duo.driver.find_elements("css selector", ".dash-cascader-result-row")
    assert len(rows) == 2
    breadcrumbs = {el.text for el in dash_duo.driver.find_elements("css selector", ".dash-cascader-breadcrumb")}
    assert breadcrumbs == {"North", "South"}
    assert dash_duo.get_logs() == []


def test_cascader_persistence_duplicate_leaves(dash_duo):
    """Path mode: a duplicate-label selection round-trips through persistence as its full path."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(id="c", options=OPTIONS_DUPLICATE_LEAVES, persistence=True, full_path=True),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(_single_path_fmt)
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    col1_rows = dash_duo.driver.find_elements("css selector", ".dash-cascader-column:nth-child(1) .dash-cascader-row")
    col1_rows[1].click()  # South
    dash_duo.wait_for_text_to_equal(
        ".dash-cascader-column:nth-child(2) .dash-cascader-row:nth-child(2) .dash-cascader-row-label", "Austin"
    )
    dash_duo.driver.find_elements("css selector", ".dash-cascader-column:nth-child(2) .dash-cascader-row")[
        0
    ].click()  # Portland (South)
    dash_duo.wait_for_text_to_equal("#out", "South/Portland")

    # Reload and check the exact path is restored (not just the "Portland" label).
    dash_duo.driver.refresh()
    dash_duo.wait_for_element("#c")
    dash_duo.wait_for_text_to_equal("#out", "South/Portland")
    assert dash_duo.get_logs() == []


# --- Regression coverage: boolean leaves, empty/invalid values, disabled search Enter, pruning ---


@pytest.mark.parametrize("full_path", [False, True])
def test_cascader_boolean_leaves(dash_duo, full_path):
    """Boolean leaf values render, are selectable, and emit without console errors."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(id="c", options=OPTIONS_BOOL_LEAVES, full_path=full_path),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(_single_fmt(full_path))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-cascader-column:nth-child(1) .dash-cascader-row").click()  # Flags
    # The row label is JS-coerced to lowercase ("true"), but the emitted value
    # round-trips back to Python as the boolean True (str(True) == "True").
    dash_duo.wait_for_text_to_equal(
        ".dash-cascader-column:nth-child(2) .dash-cascader-row:first-child .dash-cascader-row-label", "true"
    )
    dash_duo.driver.find_elements("css selector", ".dash-cascader-column:nth-child(2) .dash-cascader-row")[0].click()
    dash_duo.wait_for_text_to_equal("#out", "Flags/True" if full_path else "True")
    assert dash_duo.get_logs() == []


def test_cascader_options_is_optional():
    """Cascader() with no `options` no longer raises; it falls back to the [] default."""
    c = Cascader(id="c")
    assert c.available_properties  # constructed without error
    assert c.to_plotly_json()["props"].get("options", []) == []


def test_cascader_full_path_defaults_false():
    """`full_path` is a real prop that defaults to False (leaf mode is the default)."""
    c = Cascader(id="c")
    assert "full_path" in c.available_properties
    # Default is not serialized into props; the component default applies.
    assert c.to_plotly_json()["props"].get("full_path", False) is False


def test_cascader_no_options_renders_empty_dropdown(dash_duo):
    """Cascader with no `options` renders an empty, clickable dropdown with no console errors."""
    app = _app(Cascader(id="c", placeholder="No options"))
    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#c .dash-dropdown-placeholder", "No options")
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-cascader-content")
    assert not dash_duo.driver.find_elements("css selector", ".dash-cascader-row")
    assert dash_duo.get_logs() == []


@pytest.mark.parametrize("full_path", [False, True])
def test_cascader_single_empty_list_value_is_no_selection(dash_duo, full_path):
    """Single-select value=[] renders as no selection (placeholder), not a phantom empty chip."""
    app = _app(Cascader(id="c", options=OPTIONS_2LEVEL, value=[], placeholder="Pick one", full_path=full_path))
    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#c .dash-dropdown-placeholder", "Pick one")
    # No selected-value chip and no clear button are rendered for an empty selection.
    assert not dash_duo.driver.find_elements("css selector", "#c .dash-dropdown-value-item")
    assert not dash_duo.driver.find_elements("css selector", "#c button.dash-dropdown-clear")
    assert dash_duo.get_logs() == []


def test_cascader_path_mode_multi_keeps_valid_drops_malformed(dash_duo):
    """Path-mode multi keeps well-formed paths and drops malformed entries (pins `.filter(isValidPath)`).

    The value mixes one valid path with two malformed entries: a bare scalar `"asia"` (not an array)
    and an empty path `[]`. Only the valid path survives. In leaf mode none of these three entries
    would resolve (the selection would be empty), so asserting that `"Japan"` is selected also proves
    the path-mode branch — not leaf mode — produced this result.
    """
    app = _app(
        Cascader(id="c", options=OPTIONS_2LEVEL, multi=True, full_path=True, value=[["asia", "japan"], "asia", []])
    )
    dash_duo.start_server(app)
    # Exactly the one valid path is rendered as a selected chip.
    dash_duo.wait_for_text_to_equal("#c .dash-dropdown-value", "Japan")
    assert len(dash_duo.driver.find_elements("css selector", "#c .dash-dropdown-value-item")) == 1
    # A surviving selection is clearable.
    assert dash_duo.driver.find_elements("css selector", "#c button.dash-dropdown-clear")
    assert dash_duo.get_logs() == []


def test_cascader_path_mode_drops_malformed_path_shapes(dash_duo):
    """Path mode drops values that are not arrays of scalars: nested-list path, null segment, empty path.

    Covers the edge shapes `isValidPath` now rejects — `[["asia","japan"]]` (a segment that is itself
    an array), `[None]` (a null segment), and `[]` (an empty path) — leaving no selection and no
    clear button, rather than rendering phantom chips.
    """
    app = _app(
        Cascader(
            id="c",
            options=OPTIONS_2LEVEL,
            multi=True,
            full_path=True,
            value=[[["asia", "japan"]], [None], []],
            placeholder="Pick",
        )
    )
    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#c .dash-dropdown-placeholder", "Pick")
    assert not dash_duo.driver.find_elements("css selector", "#c .dash-dropdown-value-item")
    assert not dash_duo.driver.find_elements("css selector", "#c button.dash-dropdown-clear")
    assert dash_duo.get_logs() == []


def test_cascader_path_mode_single_drops_nested_value(dash_duo):
    """Path-mode single drops a well-shaped-but-nested value (a list of paths given for one path).

    `[["asia", "japan"]]` is a non-empty array, so an `Array.isArray` check alone would accept it and
    render a chip labelled from its array segment; the per-segment scalar check drops it instead,
    leaving no selection and no clear button.
    """
    app = _app(Cascader(id="c", options=OPTIONS_2LEVEL, full_path=True, value=[["asia", "japan"]], placeholder="Pick"))
    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#c .dash-dropdown-placeholder", "Pick")
    assert not dash_duo.driver.find_elements("css selector", "#c .dash-dropdown-value-item")
    assert not dash_duo.driver.find_elements("css selector", "#c button.dash-dropdown-clear")
    assert dash_duo.get_logs() == []


@pytest.mark.parametrize("full_path", [False, True])
def test_cascader_search_enter_skips_disabled_leaf(dash_duo, full_path):
    """Pressing Enter in the search box selects the first ENABLED leaf, skipping disabled hits."""
    from selenium.webdriver.common.keys import Keys

    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(id="c", options=OPTIONS_DISABLED_FIRST_LEAF, full_path=full_path),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(_single_fmt(full_path))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    search = dash_duo.wait_for_element(".dash-dropdown-search")
    search.send_keys("ja")
    dash_duo.wait_for_element(".dash-cascader-result-row")
    search.send_keys(Keys.ENTER)
    # "Japan" (disabled) is the first hit in tree order; Enter must skip it and pick "Jakarta".
    dash_duo.wait_for_text_to_equal("#out", "asia/jakarta" if full_path else "jakarta")
    assert dash_duo.get_logs() == []


@pytest.mark.parametrize("full_path", [False, True])
def test_cascader_options_change_prunes_invalid_selection(dash_duo, full_path):
    """When options change so a selected leaf no longer exists, that selection is pruned from value."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascader(
                    id="c",
                    options=OPTIONS_2LEVEL,
                    multi=True,
                    full_path=full_path,
                    value=_multi_value(full_path, [["asia", "japan"], ["europe", "france"]]),
                ),
                html.Button("swap", id="btn"),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(_multi_fmt(full_path))
    # New options drop "japan" (asia now only has "china"); "europe/france" still exists.
    app.callback(Output("c", "options"), Input("btn", "n_clicks"), prevent_initial_call=True)(
        lambda n: {"asia": ["china"], "europe": ["france", "germany"]}
    )
    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#out", "asia/japan | europe/france" if full_path else "france | japan")
    dash_duo.wait_for_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#out", "europe/france" if full_path else "france")
    assert dash_duo.get_logs() == []
