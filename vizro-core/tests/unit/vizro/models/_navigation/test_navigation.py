"""Unit tests for vizro.models.Navigation."""
import json
import re

import plotly
import pytest
from dash import html
from pydantic import ValidationError

import vizro.models as vm
from vizro._constants import ACCORDION_DEFAULT_TITLE


# AM: move to dashboard tests
@pytest.mark.parametrize("navigation", [None, vm.Navigation()])
def test_navigation_default(page1, page2, navigation):
    # Navigation is optional inside Dashboard and navigation.pages will always be auto-populated if not provided
    dashboard = vm.Dashboard(pages=[page1, page2], navigation=navigation)
    assert hasattr(dashboard.navigation, "id")
    assert dashboard.navigation.pages == ["Page 1", "Page 2"]


@pytest.mark.usefixtures("vizro_app", "prebuilt_dashboard")
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
            ValidationError, match=re.escape("Unknown page ID ['non existent page'] provided to " "argument 'pages'.")
        ):
            vm.Navigation(pages=pages)


@pytest.mark.usefixtures("vizro_app", "prebuilt_dashboard")
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


@pytest.mark.usefixtures("vizro_app", "prebuilt_dashboard")
class TestNavigationBuildMethod:
    """Tests navigation model build method."""

    def test_default_nav_selector(self, pages_as_dict):
        navigation = vm.Navigation(pages=pages_as_dict)
        navigation.pre_build()
        built_navigation = navigation.build()
        assert isinstance(built_navigation["nav_bar_outer"], html.Div)
        assert isinstance(built_navigation["nav_panel_outer"], html.Div)
        assert built_navigation["nav_bar_outer"].className == "hidden"

    def test_non_default_nav_selector(self, pages_as_dict):
        navigation = vm.Navigation(pages=pages_as_dict, nav_selector=vm.NavBar())
        navigation.pre_build()
        built_navigation = navigation.build()
        assert isinstance(built_navigation["nav_bar_outer"], html.Div)
        assert isinstance(built_navigation["nav_panel_outer"], html.Div)
        assert built_navigation["nav_bar_outer"].className != "hidden"


# TODO: cleanuip unused fixture
