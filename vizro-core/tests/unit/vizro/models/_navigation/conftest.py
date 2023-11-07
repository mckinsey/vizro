"""Fixtures to be shared across several tests."""

import dash_bootstrap_components as dbc
import pytest
from dash import html

from vizro._constants import ACCORDION_DEFAULT_TITLE


@pytest.fixture()
def pages_as_list():
    return ["Page 1", "Page 2"]


@pytest.fixture
def pages_as_dict():
    return {"Page 1": ["Page 1"], "Page 2": ["Page 2"]}


@pytest.fixture
def accordion_from_page_as_list():
    accordion_buttons = [
        dbc.Button(
            children=["Page 1"],
            className="accordion-item-button",
            active=True,
            key="/",
            href="/",
        ),
        dbc.Button(
            children=["Page 2"],
            className="accordion-item-button",
            active=False,
            key="/page-2",
            href="/page-2",
        ),
    ]
    accordion_items = [
        dbc.AccordionItem(
            children=[*accordion_buttons],
            title=ACCORDION_DEFAULT_TITLE,
            class_name="accordion_item",
        )
    ]
    accordion = html.Div(
        children=[
            dbc.Accordion(
                id="accordion_list",
                children=accordion_items,
                class_name="accordion",
                persistence=True,
                persistence_type="session",
                always_open=True,
            ),
            html.Hr(),
        ],
        className="nav_panel",
        id="nav_panel_outer",
    )
    return accordion


@pytest.fixture
def accordion_from_pages_as_dict():
    accordion_items = [
        dbc.AccordionItem(
            children=[
                dbc.Button(children=["Page 1"], className="accordion-item-button", active=True, key="/", href="/")
            ],
            title="PAGE 1",
            class_name="accordion_item",
        ),
        dbc.AccordionItem(
            children=[
                dbc.Button(
                    children=["Page 2"], className="accordion-item-button", active=False, key="/page-2", href="/page-2"
                )
            ],
            title="PAGE 2",
            class_name="accordion_item",
        ),
    ]
    accordion = html.Div(
        children=[
            dbc.Accordion(
                id="accordion_dict",
                children=accordion_items,
                class_name="accordion",
                persistence=True,
                persistence_type="session",
                always_open=True,
            ),
            html.Hr(),
        ],
        className="nav_panel",
        id="nav_panel_outer",
    )
    return accordion


@pytest.fixture
def navbar_div_from_dict(accordion_from_page_as_list):
    accordion = accordion_from_page_as_list
    return html.Div(
        children=[
            html.Div(
                children=[
                    dbc.Button(
                        id="nav_id_1",
                        children=[
                            html.Div(
                                children=[
                                    html.Span("dashboard", className="material-symbols-outlined"),
                                    html.Div(className="hidden"),
                                ],
                                className="nav-icon-text",
                            ),
                            None,
                        ],
                        className="icon-button",
                        href="/",
                        active=True,
                    ),
                ],
                className="nav-bar",
                id="nav_bar_outer",
            ),
            accordion,
        ]
    )


@pytest.fixture
def nav_item_default():
    return dbc.Button(
        id="navitem",
        children=[
            html.Div(
                children=[html.Span("dashboard", className="material-symbols-outlined"), html.Div(className="hidden")],
                className="nav-icon-text",
            ),
            None,
        ],
        className="icon-button",
        href="/",
        active=True,
    )


@pytest.fixture
def nav_item_with_optional():
    return dbc.Button(
        id="navitem",
        children=[
            html.Div(
                children=[
                    html.Span("home", className="material-symbols-outlined"),
                    html.Div(children=["This is "], className="icon-text"),
                ],
                className="nav-icon-text",
            ),
            dbc.Tooltip(
                children=html.P("This is a long text input"),
                target="navitem",
                placement="bottom",
                className="custom-tooltip",
            ),
        ],
        className="icon-button",
        href="/",
        active=True,
    )
