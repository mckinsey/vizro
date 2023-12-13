"""Unit tests for vizro.models.Navigation."""
import re

import dash_bootstrap_components as dbc
import pytest
from asserts import assert_component_equal
from dash import html

try:
    from pydantic.v1 import ValidationError
except ImportError:  # pragma: no cov
    from pydantic import ValidationError

import vizro.models as vm

pytestmark = pytest.mark.usefixtures("prebuilt_two_page_dashboard")


class TestNavigationInstantiation:
    def test_navigation_mandatory_only(self):
        navigation = vm.Navigation()

        assert hasattr(navigation, "id")
        assert navigation.pages == []
        assert navigation.nav_selector is None

    def test_navigation_mandatory_and_optional(self):
        accordion = vm.Accordion()
        navigation = vm.Navigation(id="navigation", pages=["Page 1", "Page 2"], nav_selector=accordion)

        assert navigation.id == "navigation"
        assert navigation.pages == ["Page 1", "Page 2"]
        assert navigation.nav_selector == accordion

    @pytest.mark.parametrize("pages", [{"Group": []}, []])
    def test_invalid_field_pages_no_ids_provided(self, pages):
        with pytest.raises(ValidationError, match="Ensure this value has at least 1 item."):
            vm.Navigation(pages=pages)

    def test_invalid_field_pages_wrong_input_type(self):
        with pytest.raises(ValidationError, match="str type expected"):
            vm.Navigation(pages=[vm.Page(title="Page 3", components=[vm.Button()])])

    @pytest.mark.parametrize("pages", [["non existent page"], {"Group": ["non existent page"]}])
    def test_invalid_page(self, pages):
        with pytest.raises(
            ValidationError, match=re.escape("Unknown page ID ['non existent page'] provided to argument 'pages'.")
        ):
            vm.Navigation(pages=pages)


class TestNavigationPreBuildMethod:
    def test_default_nav_selector(self, pages_as_dict):
        navigation = vm.Navigation(pages=pages_as_dict)
        navigation.pre_build()
        assert isinstance(navigation.nav_selector, vm.Accordion)
        assert navigation.nav_selector.pages == pages_as_dict

    def test_default_nav_selector_with_pages(self, pages_as_dict):
        navigation = vm.Navigation(pages=pages_as_dict, nav_selector=vm.Accordion(pages={"Group": ["Page 1"]}))
        navigation.pre_build()
        assert isinstance(navigation.nav_selector, vm.Accordion)
        assert navigation.nav_selector.pages == {"Group": ["Page 1"]}

    def test_non_default_nav_selector(self, pages_as_dict):
        navigation = vm.Navigation(pages=pages_as_dict, nav_selector=vm.NavBar())
        navigation.pre_build()
        assert isinstance(navigation.nav_selector, vm.NavBar)
        assert navigation.nav_selector.pages == pages_as_dict

    def test_non_default_nav_selector_with_pages(self, pages_as_dict):
        navigation = vm.Navigation(pages=pages_as_dict, nav_selector=vm.NavBar(pages={"Group": ["Page 1"]}))
        navigation.pre_build()
        assert isinstance(navigation.nav_selector, vm.NavBar)
        assert navigation.nav_selector.pages == {"Group": ["Page 1"]}


class TestNavigationBuildMethod:
    """Tests navigation model build method."""

    @pytest.mark.parametrize("pages", ["pages_as_dict", "pages_as_list"])
    def test_default_nav_selector(self, pages, request):
        pages = request.getfixturevalue(pages)
        navigation = vm.Navigation(pages=pages)
        navigation.pre_build()
        built_navigation = navigation.build(active_page_id="Page 1")
        assert_component_equal(
            built_navigation["nav_bar_outer"], html.Div(hidden=True, id="nav_bar_outer"), keys_to_strip={}
        )
        assert_component_equal(
            built_navigation["nav_panel_outer"], html.Div(id="nav_panel_outer"), keys_to_strip={"children", "className"}
        )
        assert all(isinstance(child, dbc.Accordion) for child in built_navigation["nav_panel_outer"].children)

    def test_non_default_nav_selector_pags_as_dict(self, pages_as_dict):
        navigation = vm.Navigation(pages=pages_as_dict, nav_selector=vm.NavBar())
        navigation.pre_build()
        built_navigation = navigation.build(active_page_id="Page 1")
        assert_component_equal(
            built_navigation["nav_bar_outer"],
            html.Div(id="nav_bar_outer", className="nav-bar"),
            keys_to_strip={"children"},
        )
        assert_component_equal(
            built_navigation["nav_panel_outer"],
            html.Div(id="nav_panel_outer"),
            keys_to_strip={"children", "className"},
        )
        assert all(isinstance(child, dbc.Accordion) for child in built_navigation["nav_panel_outer"].children)

    def test_non_default_nav_selector_pages_as_list(self, pages_as_list):
        navigation = vm.Navigation(pages=pages_as_list, nav_selector=vm.NavBar())
        navigation.pre_build()
        built_navigation = navigation.build(active_page_id="Page 1")
        assert_component_equal(
            built_navigation["nav_bar_outer"],
            html.Div(id="nav_bar_outer", className="nav-bar"),
            keys_to_strip={"children"},
        )
        assert_component_equal(
            built_navigation["nav_panel_outer"],
            html.Div(id="nav_panel_outer", hidden=True),
            keys_to_strip={"children"},
        )
