"""Unit tests for vizro.models.NavLink."""

import re

import dash_bootstrap_components as dbc
import pytest
from asserts import STRIP_ALL, assert_component_equal
from dash import html
from pydantic import ValidationError

import vizro.models as vm

pytestmark = pytest.mark.usefixtures("prebuilt_two_page_dashboard")


class TestNavLinkInstantiation:
    """Tests NavLink model instantiation."""

    def test_nav_link_mandatory_only(self):
        nav_link = vm.NavLink(label="Label")

        assert hasattr(nav_link, "id")
        assert nav_link.label == "Label"
        assert nav_link.icon == ""
        assert nav_link.pages == []

    def test_nav_link_mandatory_and_optional(self, pages_as_list):
        nav_link = vm.NavLink(id="nav_link", icon="home", label="Homepage", pages=pages_as_list)

        assert nav_link.id == "nav_link"
        assert nav_link.label == "Homepage"
        assert nav_link.icon == "home"
        assert nav_link.pages == pages_as_list

    @pytest.mark.parametrize("icon", ["Bar Chart", "bar chart", "bar_chart", "Bar_Chart", " bar_chart "])
    def test_validate_icon(self, icon):
        nav_link = vm.NavLink(icon=icon, label="Label")
        assert nav_link.icon == "bar_chart"

    def test_nav_link_valid_pages_as_dict(self, pages_as_dict):
        nav_link = vm.NavLink(pages=pages_as_dict, label="Label")
        assert nav_link.pages == pages_as_dict

    def test_mandatory_label_missing(self):
        with pytest.raises(ValidationError, match="Field required"):
            vm.NavLink()

    @pytest.mark.parametrize("pages", [{"Group": []}, []])
    def test_invalid_field_pages_no_ids_provided(self, pages):
        with pytest.raises(ValidationError, match="Ensure this value has at least 1 item."):
            vm.NavLink(pages=pages)

    def test_invalid_field_pages_wrong_input_type(self):
        with pytest.raises(ValidationError, match="Input should be a valid"):
            vm.NavLink(pages=[vm.Page(title="Page 3", components=[vm.Button()])], label="Foo")

    @pytest.mark.parametrize("pages", [["non existent page"], {"Group": ["non existent page"]}])
    def test_invalid_page(self, pages):
        with pytest.raises(
            ValidationError, match=re.escape("Unknown page ID ['non existent page'] provided to argument 'pages'.")
        ):
            vm.NavLink(pages=pages)


class TestNavLinkPreBuildMethod:
    def test_nav_link(self, pages_as_dict):
        nav_link = vm.NavLink(label="Label", pages=pages_as_dict)
        nav_link.pre_build()
        assert isinstance(nav_link._nav_selector, vm.Accordion)
        assert nav_link._nav_selector.pages == pages_as_dict


@pytest.mark.parametrize("pages", ["pages_as_dict", "pages_as_list"])
class TestNavLinkBuildMethod:
    """Tests NavLink model build method."""

    def test_nav_link_active(self, pages, request):
        pages = request.getfixturevalue(pages)
        nav_link = vm.NavLink(id="nav-link", label="Label", icon="icon", pages=pages)
        nav_link.pre_build()
        built_nav_link = nav_link.build(active_page_id="Page 1")
        expected_nav_link = dbc.NavLink(
            children=[
                html.Span("icon", className="material-symbols-outlined", id="nav-link-tooltip-target"),
                dbc.Tooltip(
                    "Label",
                    placement="right",
                    target="nav-link-tooltip-target",
                ),
            ],
            active=True,
            href="/",
            id="nav-link",
        )
        assert_component_equal(built_nav_link["nav-link"], expected_nav_link)
        assert_component_equal(built_nav_link["nav-panel"].children, [dbc.Accordion()], keys_to_strip=STRIP_ALL)

    def test_nav_link_not_active(self, pages, request):
        pages = request.getfixturevalue(pages)
        nav_link = vm.NavLink(id="nav-link", label="Label", icon="icon", pages=pages)
        nav_link.pre_build()
        built_nav_link = nav_link.build(active_page_id="Page 3")
        expected_button = dbc.NavLink(
            children=[
                html.Span("icon", className="material-symbols-outlined", id="nav-link-tooltip-target"),
                dbc.Tooltip(
                    "Label",
                    placement="right",
                    target="nav-link-tooltip-target",
                ),
            ],
            active=False,
            href="/",
            id="nav-link",
        )
        assert_component_equal(built_nav_link["nav-link"], expected_button)
        assert "nav-panel" not in built_nav_link
