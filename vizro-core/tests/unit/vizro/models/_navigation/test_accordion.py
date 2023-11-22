"""Unit tests for vizro.models.Accordion."""
import json
import re

import dash_bootstrap_components as dbc
import plotly
import pytest
from dash import html
from pydantic import ValidationError

import vizro.models as vm
from vizro._constants import ACCORDION_DEFAULT_TITLE


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
        ],
        className="nav_panel",
        id="nav_panel_outer",
    )
    return accordion


@pytest.mark.usefixtures("vizro_app", "prebuilt_dashboard")
class TestAccordionInstantiation:
    """Tests accordion model instantiation."""

    def test_mandatory_only(self):
        accordion = vm.Accordion()

        assert hasattr(accordion, "id")
        assert accordion.pages == {}

    def test_mandatory_and_optional(self, pages_as_dict):
        accordion = vm.Accordion(id="accordion", pages=pages_as_dict)
        assert hasattr(accordion, "id")
        assert accordion.pages == pages_as_dict

    def test_valid_pages_as_list(self, pages_as_list):
        accordion = vm.Accordion(pages=pages_as_list)
        assert accordion.pages == {ACCORDION_DEFAULT_TITLE: pages_as_list}

    @pytest.mark.parametrize("pages", [{"Group": []}, []])
    def test_invalid_field_pages_no_ids_provided(self, pages):
        with pytest.raises(ValidationError, match="Ensure this value has at least 1 item."):
            vm.Accordion(pages=pages)

    def test_invalid_field_pages_wrong_input_type(self):
        with pytest.raises(ValidationError, match="str type expected"):
            vm.Accordion(pages=[vm.Page(title="Page 3", components=[vm.Button()])])

    @pytest.mark.parametrize("pages", [["non existent page"], {"Group": ["non existent page"]}])
    def test_invalid_page(self, pages):
        with pytest.raises(
            ValidationError, match=re.escape("Unknown page ID ['non existent page'] provided to " "argument 'pages'.")
        ):
            vm.Accordion(pages=pages)


@pytest.mark.usefixtures("vizro_app", "prebuilt_dashboard")
class TestAccordionBuild:
    """Tests accordion build method."""

    def test_accordion_build_pages(self, pages_as_dict, accordion_from_pages_as_dict):
        accordion = vm.Accordion(pages=pages_as_dict, id="accordion_dict").build(active_page_id="Page 1")
        result = json.loads(json.dumps(accordion, cls=plotly.utils.PlotlyJSONEncoder))
        expected = json.loads(json.dumps(accordion_from_pages_as_dict, cls=plotly.utils.PlotlyJSONEncoder))
        assert result == expected

    def test_single_page_and_hidden_div(self):
        accordion = vm.Accordion(pages=["Page 1"]).build()
        result = json.loads(json.dumps(accordion, cls=plotly.utils.PlotlyJSONEncoder))
        expected = json.loads(
            json.dumps(html.Div(hidden=True, id="nav_panel_outer"), cls=plotly.utils.PlotlyJSONEncoder)
        )
        assert result == expected


# AM: Do as active/inactive?

## AM: def accordion_from_page_as_list unused
