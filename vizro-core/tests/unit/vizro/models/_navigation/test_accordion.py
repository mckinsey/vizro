"""Unit tests for vizro.models.Accordion."""

import re

import dash_bootstrap_components as dbc
import pytest
from asserts import assert_component_equal
from pydantic import ValidationError

import vizro.models as vm
from vizro._constants import ACCORDION_DEFAULT_TITLE

pytestmark = pytest.mark.usefixtures("prebuilt_two_page_dashboard")


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
        with pytest.raises(ValidationError, match="Input should be a valid string"):
            vm.Accordion(pages=[vm.Page(title="Page 3", components=[vm.Button()])])

    @pytest.mark.parametrize("pages", [["non existent page"], {"Group": ["non existent page"]}])
    def test_invalid_page(self, pages):
        with pytest.raises(
            ValidationError, match=re.escape("Unknown page ID ['non existent page'] provided to argument 'pages'.")
        ):
            vm.Accordion(pages=pages)


class TestAccordionBuild:
    """Tests accordion build method."""

    common_args = {"always_open": True, "persistence": True, "persistence_type": "session", "id": "accordion"}

    test_cases = [
        (
            {"Group": ["Page 1", "Page 2"]},
            dbc.Accordion(
                children=[
                    dbc.AccordionItem(
                        children=[
                            dbc.NavLink(children="Page 1", active="exact", href="/"),
                            dbc.NavLink(children="Page 2", active="exact", href="/page-2"),
                        ],
                        title="GROUP",
                        item_id="Group",
                    )
                ],
                active_item="Group",
                **common_args,
            ),
        ),
        (
            {"Group 1": ["Page 1"], "Group 2": ["Page 2"]},
            dbc.Accordion(
                children=[
                    dbc.AccordionItem(
                        children=[dbc.NavLink(children="Page 1", active="exact", href="/")],
                        title="GROUP 1",
                        item_id="Group 1",
                    ),
                    dbc.AccordionItem(
                        children=[dbc.NavLink(children="Page 2", active="exact", href="/page-2")],
                        title="GROUP 2",
                        item_id="Group 2",
                    ),
                ],
                active_item="Group 1",
                **common_args,
            ),
        ),
        (
            ["Page 1", "Page 2"],
            dbc.Accordion(
                children=[
                    dbc.AccordionItem(
                        children=[
                            dbc.NavLink(children="Page 1", active="exact", href="/"),
                            dbc.NavLink(children="Page 2", active="exact", href="/page-2"),
                        ],
                        title=ACCORDION_DEFAULT_TITLE,
                        item_id="SELECT PAGE",
                    )
                ],
                active_item="SELECT PAGE",
                **common_args,
            ),
        ),
    ]

    @pytest.mark.parametrize("pages, expected", test_cases)
    def test_accordion(self, pages, expected):
        accordion = vm.Accordion(id="accordion", pages=pages).build(active_page_id="Page 1")
        assert_component_equal(accordion, dbc.Nav(id="nav-panel"), keys_to_strip={"children"})
        assert_component_equal(accordion["accordion"], expected, keys_to_strip={"class_name", "className"})

    def test_accordion_one_page(self):
        accordion = vm.Accordion(pages={"Group": ["Page 1"]}).build(active_page_id="Page 1")
        assert_component_equal(accordion, dbc.Nav(className="d-none invisible", id="nav-panel"))
