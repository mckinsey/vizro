"""Unit tests for vizro.models.NavBar."""

import re

import dash_bootstrap_components as dbc
import pytest
from asserts import STRIP_ALL, assert_component_equal
from dash import html
from pydantic import ValidationError

import vizro.models as vm

pytestmark = pytest.mark.usefixtures("prebuilt_two_page_dashboard")


class TestNavBarInstantiation:
    """Tests NavBar model instantiation."""

    def test_nav_bar_mandatory_only(self):
        nav_bar = vm.NavBar()

        assert hasattr(nav_bar, "id")
        assert nav_bar.pages == {}
        assert nav_bar.items == []

    def test_nav_bar_mandatory_and_optional(self, pages_as_dict):
        nav_link = vm.NavLink(label="Label")
        nav_bar = vm.NavBar(id="nav-bar", pages=pages_as_dict, items=[nav_link])

        assert nav_bar.id == "nav-bar"
        assert nav_bar.pages == pages_as_dict
        assert nav_bar.items == [nav_link]

    def test_valid_pages_as_list(self, pages_as_list):
        nav_bar = vm.NavBar(pages=pages_as_list)
        assert nav_bar.pages == {"Page 1": ["Page 1"], "Page 2": ["Page 2"]}

    @pytest.mark.parametrize("pages", [{"Group": []}, []])
    def test_invalid_field_pages_no_ids_provided(self, pages):
        with pytest.raises(ValidationError, match="Ensure this value has at least 1 item."):
            vm.NavBar(pages=pages)

    def test_invalid_field_pages_wrong_input_type(self):
        with pytest.raises(TypeError, match="unhashable type: 'Page'"):
            vm.NavBar(pages=[vm.Page(title="Page 3", components=[vm.Button()])])

    @pytest.mark.parametrize("pages", [["non existent page"], {"Group": ["non existent page"]}])
    def test_invalid_page(self, pages):
        with pytest.raises(
            ValidationError, match=re.escape("Unknown page ID ['non existent page'] provided to argument 'pages'.")
        ):
            vm.NavBar(pages=pages)


class TestNavBarPreBuildMethod:
    def test_default_items(self, pages_as_dict):
        nav_bar = vm.NavBar(pages=pages_as_dict)
        nav_bar.pre_build()
        assert all(isinstance(item, vm.NavLink) for item in nav_bar.items)
        assert all(item.icon == f"filter_{position}" for position, item in enumerate(nav_bar.items, 1))

    def test_items_with_with_pages_icons(self, pages_as_dict):
        nav_links = [
            vm.NavLink(label="Label", pages={"Group 1": ["Page 1"]}, icon="Home"),
            vm.NavLink(label="Label", pages={"Group 2": ["Page 2"]}),
        ]
        nav_bar = vm.NavBar(pages=pages_as_dict, items=nav_links)
        nav_bar.pre_build()
        assert nav_bar.items == nav_links
        assert nav_bar.items[0].icon == "home"
        assert nav_bar.items[1].icon == "filter_2"


class TestNavBarBuildMethod:
    """Tests NavBar model build method."""

    def test_nav_bar_active_pages_as_dict(self, pages_as_dict):
        nav_bar = vm.NavBar(pages=pages_as_dict)
        nav_bar.pre_build()
        nav_bar.items[0].id = "nav-link-1"
        built_nav_bar = nav_bar.build(active_page_id="Page 1")
        expected_navigation = dbc.Navbar(
            [
                dbc.NavLink(
                    children=[
                        html.Span("filter_1", className="material-symbols-outlined", id="nav-link-1-tooltip-target"),
                        dbc.Tooltip(
                            "Group",
                            placement="right",
                            target="nav-link-1-tooltip-target",
                        ),
                    ],
                    active=True,
                    href="/",
                )
            ]
        )
        assert_component_equal(built_nav_bar["nav-bar"], expected_navigation, keys_to_strip={"id", "className"})
        assert_component_equal(built_nav_bar["nav-panel"], dbc.Nav(id="nav-panel"), keys_to_strip={"children"})
        assert_component_equal(built_nav_bar["nav-panel"].children, [dbc.Accordion()], keys_to_strip=STRIP_ALL)

    def test_nav_bar_active_pages_as_list(self, pages_as_list):
        nav_bar = vm.NavBar(pages=pages_as_list)
        nav_bar.pre_build()
        nav_bar.items[0].id = "nav-link-1"
        nav_bar.items[1].id = "nav-link-2"
        built_nav_bar = nav_bar.build(active_page_id="Page 1")
        expected_nav_bar = dbc.Navbar(
            [
                dbc.NavLink(
                    children=[
                        html.Span("filter_1", className="material-symbols-outlined", id="nav-link-1-tooltip-target"),
                        dbc.Tooltip(
                            "Page 1",
                            placement="right",
                            target="nav-link-1-tooltip-target",
                        ),
                    ],
                    active=True,
                    href="/",
                ),
                dbc.NavLink(
                    children=[
                        html.Span("filter_2", className="material-symbols-outlined", id="nav-link-2-tooltip-target"),
                        dbc.Tooltip(
                            "Page 2",
                            placement="right",
                            target="nav-link-2-tooltip-target",
                        ),
                    ],
                    active=False,
                    href="/page-2",
                ),
            ]
        )
        assert_component_equal(built_nav_bar["nav-bar"], expected_nav_bar, keys_to_strip={"id", "className"})
        assert_component_equal(built_nav_bar["nav-panel"], dbc.Nav(id="nav-panel", className="d-none invisible"))

    def test_nav_bar_not_active_pages_as_dict(self, pages_as_dict):
        nav_bar = vm.NavBar(pages=pages_as_dict)
        nav_bar.pre_build()
        nav_bar.items[0].id = "nav-link-1"
        built_nav_bar = nav_bar.build(active_page_id="Page 3")
        expected_nav_bar = dbc.Navbar(
            [
                dbc.NavLink(
                    children=[
                        html.Span("filter_1", className="material-symbols-outlined", id="nav-link-1-tooltip-target"),
                        dbc.Tooltip(
                            "Group",
                            placement="right",
                            target="nav-link-1-tooltip-target",
                        ),
                    ],
                    active=False,
                    href="/",
                )
            ]
        )
        assert_component_equal(built_nav_bar["nav-bar"], expected_nav_bar, keys_to_strip={"id", "className"})
        assert_component_equal(built_nav_bar["nav-panel"], dbc.Nav(className="d-none invisible", id="nav-panel"))

    def test_nav_bar_not_active_pages_as_list(self, pages_as_list):
        nav_bar = vm.NavBar(pages=pages_as_list)
        nav_bar.pre_build()
        nav_bar.items[0].id = "nav-link-1"
        nav_bar.items[1].id = "nav-link-2"
        built_nav_bar = nav_bar.build(active_page_id="Page 3")
        expected_nav_bar = dbc.Navbar(
            [
                dbc.NavLink(
                    children=[
                        html.Span("filter_1", className="material-symbols-outlined", id="nav-link-1-tooltip-target"),
                        dbc.Tooltip(
                            "Page 1",
                            placement="right",
                            target="nav-link-1-tooltip-target",
                        ),
                    ],
                    active=False,
                    href="/",
                ),
                dbc.NavLink(
                    children=[
                        html.Span("filter_2", className="material-symbols-outlined", id="nav-link-2-tooltip-target"),
                        dbc.Tooltip(
                            "Page 2",
                            placement="right",
                            target="nav-link-2-tooltip-target",
                        ),
                    ],
                    active=False,
                    href="/page-2",
                ),
            ]
        )
        assert_component_equal(built_nav_bar["nav-bar"], expected_nav_bar, keys_to_strip={"id", "className"})
        assert_component_equal(built_nav_bar["nav-panel"], dbc.Nav(id="nav-panel", className="d-none invisible"))
