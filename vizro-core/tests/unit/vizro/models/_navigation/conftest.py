"""Fixtures to be shared across several tests."""
import dash_bootstrap_components as dbc
import pytest
from dash import html

from vizro import Vizro


@pytest.fixture
def dashboard_build(dashboard):
    return Vizro().build(dashboard)


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
            className="accordion_button",
            key="/",
            href="/",
        ),
        dbc.Button(
            children=["Page 2"],
            className="accordion_button",
            key="/page-2",
            href="/page-2",
        ),
    ]
    accordion_items = [
        dbc.AccordionItem(
            children=[*accordion_buttons],
            title="SELECT PAGE",
            class_name="accordion_item",
        )
    ]
    accordion = html.Div(
        children=dbc.Accordion(
            id="accordion_list",
            children=accordion_items,
            class_name="accordion",
            persistence=True,
            persistence_type="session",
        ),
        className="nav_panel",
        id="accordion_list_outer",
    )
    return accordion


@pytest.fixture
def accordion_from_pages_as_dict():
    accordion_items = [
        dbc.AccordionItem(
            children=[dbc.Button(children=["Page 1"], className="accordion_button", key="/", href="/")],
            title="PAGE 1",
            class_name="accordion_item",
        ),
        dbc.AccordionItem(
            children=[dbc.Button(children=["Page 2"], className="accordion_button", key="/page-2", href="/page-2")],
            title="PAGE 2",
            class_name="accordion_item",
        ),
    ]
    accordion = html.Div(
        children=dbc.Accordion(
            id="accordion_dict",
            children=accordion_items,
            class_name="accordion",
            persistence=True,
            persistence_type="session",
        ),
        className="nav_panel",
        id="accordion_dict_outer",
    )
    return accordion
