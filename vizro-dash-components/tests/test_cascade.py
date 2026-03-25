"""Tests for the vizro_dash_components.Cascade component."""

import dash_mantine_components as dmc
from dash import Dash, Input, Output, html
from vizro_dash_components import Cascade

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


def _app(layout):
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(layout)
    return app


# --- Render / open / close ---


def test_cascade_renders(dash_duo):
    """Component renders a trigger button without errors."""
    app = _app(Cascade(id="c", options=OPTIONS_2LEVEL))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c")
    assert dash_duo.get_logs() == []


def test_cascade_opens_on_click(dash_duo):
    """Clicking the trigger opens the panel."""
    app = _app(Cascade(id="c", options=OPTIONS_2LEVEL))
    dash_duo.start_server(app)
    trigger = dash_duo.wait_for_element("#c")
    trigger.click()
    dash_duo.wait_for_element(".dash-cascade-panel")
    assert dash_duo.get_logs() == []


def test_cascade_shows_root_column(dash_duo):
    """Root column shows top-level option labels after opening."""
    app = _app(Cascade(id="c", options=OPTIONS_2LEVEL))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_text_to_equal(
        ".dash-cascade-column:first-child .dash-cascade-row:first-child .dash-cascade-row-label", "Asia"
    )


def test_cascade_closes_on_outside_click(dash_duo):
    """Clicking outside the component closes the panel."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    app = _app(
        html.Div(
            [
                html.Div("outside", id="outside"),
                Cascade(id="c", options=OPTIONS_2LEVEL),
            ]
        )
    )
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-cascade-panel")
    dash_duo.find_element("#outside").click()
    WebDriverWait(dash_duo.driver, 3).until(
        EC.invisibility_of_element_located((By.CSS_SELECTOR, ".dash-cascade-panel"))
    )


# --- Single-select ---


def test_cascade_single_select_leaf(dash_duo):
    """Clicking a leaf in single mode sets the value and closes the panel."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascade(id="c", options=OPTIONS_2LEVEL),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(lambda v: str(v))
    dash_duo.start_server(app)
    # Open
    dash_duo.wait_for_element("#c").click()
    # Click "Asia" to expand
    dash_duo.wait_for_element(".dash-cascade-row").click()
    # Click "Japan" (leaf in second column)
    rows = dash_duo.driver.find_elements("css selector", ".dash-cascade-column:nth-child(2) .dash-cascade-row")
    rows[0].click()
    # Panel closes, value updated
    dash_duo.wait_for_text_to_equal("#out", "japan")
    panels = dash_duo.driver.find_elements("css selector", ".dash-cascade-panel")
    assert len(panels) == 0
    assert dash_duo.get_logs() == []


def test_cascade_single_select_shows_label_in_trigger(dash_duo):
    """Selected leaf label is shown in the trigger."""
    app = _app(Cascade(id="c", options=OPTIONS_2LEVEL, value="japan"))
    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#c .dash-cascade-value", "Japan")


def test_cascade_single_clear(dash_duo):
    """Clicking the clear button sets value to null."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascade(id="c", options=OPTIONS_2LEVEL, value="japan"),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(lambda v: str(v))
    dash_duo.start_server(app)
    dash_duo.wait_for_element(".dash-cascade-clear").click()
    dash_duo.wait_for_text_to_equal("#out", "None")


# --- Multi-select ---


def test_cascade_multi_select_leaf(dash_duo):
    """Clicking leaf checkboxes in multi mode toggles values."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascade(id="c", options=OPTIONS_2LEVEL, multi=True),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(lambda v: ",".join(sorted(str(x) for x in (v or []))))
    dash_duo.start_server(app)
    # Open and expand Asia
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-cascade-row").click()
    # Check Japan checkbox (second column, first row)
    checkboxes = dash_duo.driver.find_elements(
        "css selector", ".dash-cascade-column:nth-child(2) .dash-cascade-checkbox"
    )
    checkboxes[0].click()
    dash_duo.wait_for_text_to_equal("#out", "japan")
    # Panel still open
    assert dash_duo.find_element(".dash-cascade-panel")
    assert dash_duo.get_logs() == []


def test_cascade_multi_shows_count_badge(dash_duo):
    """Trigger shows count badge when N > 1 values are selected."""
    app = _app(Cascade(id="c", options=OPTIONS_2LEVEL, multi=True, value=["japan", "france"]))
    dash_duo.start_server(app)
    dash_duo.wait_for_element(".dash-cascade-count")
    badge_text = dash_duo.find_element(".dash-cascade-count").text
    assert "2" in badge_text


def test_cascade_multi_select_all(dash_duo):
    """'Select all' adds all leaf values."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascade(id="c", options=OPTIONS_2LEVEL, multi=True),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(lambda v: ",".join(sorted(str(x) for x in (v or []))))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-cascade-action-button").click()
    dash_duo.wait_for_text_to_equal("#out", "china,france,germany,japan")
    assert dash_duo.get_logs() == []


def test_cascade_multi_deselect_all(dash_duo):
    """'Deselect all' removes all selected leaf values."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascade(id="c", options=OPTIONS_2LEVEL, multi=True, value=["japan", "france"]),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(lambda v: str(sorted(v or [])))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    buttons = dash_duo.driver.find_elements("css selector", ".dash-cascade-action-button")
    buttons[1].click()  # "Deselect all"
    dash_duo.wait_for_text_to_equal("#out", "[]")
    assert dash_duo.get_logs() == []


# --- Search ---


def test_cascade_search_filters_results(dash_duo):
    """Typing in the search bar shows matching leaves."""
    app = _app(Cascade(id="c", options=OPTIONS_2LEVEL))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-cascade-search-input").send_keys("jap")
    dash_duo.wait_for_element(".dash-cascade-result-row")
    result_labels = [
        el.text for el in dash_duo.driver.find_elements("css selector", ".dash-cascade-row-label") if el.is_displayed()
    ]
    assert "Japan" in result_labels


def test_cascade_search_single_select_closes_on_pick(dash_duo):
    """Selecting a search result in single mode closes panel and clears search."""
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                Cascade(id="c", options=OPTIONS_2LEVEL),
                html.Div(id="out"),
            ]
        )
    )
    app.callback(Output("out", "children"), Input("c", "value"))(lambda v: str(v))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-cascade-search-input").send_keys("jap")
    dash_duo.wait_for_element(".dash-cascade-result-row").click()
    dash_duo.wait_for_text_to_equal("#out", "japan")
    panels = dash_duo.driver.find_elements("css selector", ".dash-cascade-panel")
    assert len(panels) == 0


# --- 3-level nesting ---


def test_cascade_three_levels(dash_duo):
    """Component correctly renders 3 levels of nesting."""
    app = _app(Cascade(id="c", options=OPTIONS_3LEVEL))
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#c").click()
    # Expand Asia
    dash_duo.wait_for_element(".dash-cascade-row").click()
    # Expand East Asia
    rows = dash_duo.driver.find_elements("css selector", ".dash-cascade-column:nth-child(2) .dash-cascade-row")
    rows[0].click()
    # Third column should show Japan
    dash_duo.wait_for_text_to_equal(".dash-cascade-column:nth-child(3) .dash-cascade-row-label", "Japan")
    assert dash_duo.get_logs() == []


# --- Persistence ---


def test_cascade_persistence(dash_duo):
    """Value persists across page reload when persistence=True."""
    app = _app(Cascade(id="c", options=OPTIONS_2LEVEL, persistence=True))
    dash_duo.start_server(app)

    # Open panel and select Japan (Asia > Japan)
    dash_duo.wait_for_element("#c").click()
    dash_duo.wait_for_element(".dash-cascade-row").click()  # Asia
    rows = dash_duo.driver.find_elements("css selector", ".dash-cascade-column:nth-child(2) .dash-cascade-row")
    rows[0].click()  # Japan
    dash_duo.wait_for_text_to_equal("#c .dash-cascade-value", "Japan")

    # Reload and check value is restored
    dash_duo.driver.refresh()
    dash_duo.wait_for_element("#c")
    dash_duo.wait_for_text_to_equal("#c .dash-cascade-value", "Japan")
    assert dash_duo.get_logs() == []
