"""Unit tests for vizro.models.Navigation."""
import json
import re

import plotly
import pytest
from dash import html
from pydantic import ValidationError

import vizro.models as vm
from vizro.models._navigation.accordion import Accordion


@pytest.mark.usefixtures("vizro_app", "dashboard_prebuild")
class TestNavigationInstantiation:
    """Tests navigation model instantiation ."""

    def test_navigation_mandatory_only(self):
        navigation = vm.Navigation()
        assert hasattr(navigation, "id")
        assert navigation.pages == ["Page 1", "Page 2"]

    # TODO: Extend this test with optional selectors
    def test_navigation_mandatory_and_optional(self):
        navigation = vm.Navigation(id="navigation")
        assert navigation.id == "navigation"
        assert navigation.pages == ["Page 1", "Page 2"]

    def test_navigation_valid_pages_as_list(self, pages_as_list):
        navigation = vm.Navigation(pages=pages_as_list, id="navigation")
        assert navigation.id == "navigation"
        assert navigation.pages == pages_as_list

    def test_navigation_valid_pages_as_dict(self, pages_as_dict):
        navigation = vm.Navigation(pages=pages_as_dict, id="navigation")
        assert navigation.id == "navigation"
        assert navigation.pages == pages_as_dict

    def test_navigation_valid_pages_not_all_included(self):
        navigation = vm.Navigation(pages=["Page 1"], id="navigation")
        assert navigation.id == "navigation"
        assert navigation.pages == ["Page 1"]

    def test_navigation_invalid_pages_empty_list(self):
        with pytest.raises(ValidationError, match="Ensure this value has at least 1 item."):
            vm.Navigation(pages=[], id="navigation")

    def test_navigation_invalid_pages_unknown_page(self):
        with pytest.raises(ValidationError, match=re.escape("Unknown page ID ['Test'] provided to argument 'pages'.")):
            vm.Navigation(pages=["Test"], id="navigation")


@pytest.mark.usefixtures("vizro_app", "dashboard_prebuild")
@pytest.mark.parametrize("pages", [["Page 1", "Page 2"], {"SELECT PAGE": ["Page 1", "Page 2"]}])
def test_navigation_pre_build(pages):
    navigation = vm.Navigation(pages=pages, id="navigation")

    assert navigation.id == "navigation"
    assert navigation.pages == pages
    assert isinstance(navigation.selector, Accordion)
    assert navigation.selector.pages == {"SELECT PAGE": ["Page 1", "Page 2"]}


@pytest.mark.usefixtures("vizro_app", "dashboard_prebuild")
@pytest.mark.parametrize("pages", [["Page 1", "Page 2"], {"Page 1": ["Page 1"], "Page 2": ["Page 2"]}])
def test_navigation_build(pages):
    navigation = vm.Navigation(pages=pages)
    accordion = Accordion(pages=pages)
    navigation.selector.id = accordion.id
    expected_navigation = html.Div(children=[html.Div(className="hidden", id="nav_bar_outer"), accordion.build()])
    result = json.loads(json.dumps(navigation.build(), cls=plotly.utils.PlotlyJSONEncoder))
    expected = json.loads(json.dumps(expected_navigation, cls=plotly.utils.PlotlyJSONEncoder))
    assert result == expected


@pytest.mark.usefixtures("vizro_app", "dashboard_prebuild")
class TestNavigationBuildMethod:
    """Tests navigation model build method."""

    def test_navigation_build_default(self):
        navigation = vm.Navigation()
        accordion = Accordion(pages=["Page 1", "Page 2"])
        navigation.selector.id = accordion.id

        expected_navigation = html.Div(children=[html.Div(className="hidden", id="nav_bar_outer"), accordion.build()])
        result = json.loads(json.dumps(navigation.build(), cls=plotly.utils.PlotlyJSONEncoder))
        expected = json.loads(json.dumps(expected_navigation, cls=plotly.utils.PlotlyJSONEncoder))
        assert result == expected

    @pytest.mark.parametrize("pages", [["Page 1", "Page 2"], {"Page 1": ["Page 1"], "Page 2": ["Page 2"]}])
    def test_navigation_build_pages(self, pages):
        navigation = vm.Navigation(pages=pages)
        accordion = Accordion(pages=pages)
        navigation.selector.id = accordion.id

        expected_navigation = html.Div(children=[html.Div(className="hidden", id="nav_bar_outer"), accordion.build()])
        result = json.loads(json.dumps(navigation.build(), cls=plotly.utils.PlotlyJSONEncoder))
        expected = json.loads(json.dumps(expected_navigation, cls=plotly.utils.PlotlyJSONEncoder))
        assert result == expected

    @pytest.mark.parametrize("pages", [["Page 1", "Page 2"], {"Icon 1": ["Page 1"], "Icon 2": ["Page 2"]}])
    def test_navigation_build_selector_accordion(self, pages):
        nav_with_selector = vm.Navigation(selector=vm.Accordion(pages=pages))
        nav_with_pages = vm.Navigation(pages=pages)
        nav_with_selector.selector.id = nav_with_pages.selector.id

        nav_with_selector = json.loads(
            json.dumps(nav_with_selector.build(active_page_id="Page 1"), cls=plotly.utils.PlotlyJSONEncoder)
        )
        nav_with_pages = json.loads(
            json.dumps(nav_with_pages.build(active_page_id="Page 1"), cls=plotly.utils.PlotlyJSONEncoder)
        )

        assert nav_with_selector == nav_with_pages

    @pytest.mark.parametrize("pages", [None, ["Page 1", "Page 2"], {"Icon 1": ["Page 1"], "Icon 2": ["Page 2"]}])
    def test_navigation_build_selector(self, navbar_div_default, pages):
        navigation = vm.Navigation(pages=pages, selector=vm.NavBar())
        navigation.selector.items[0].id, navigation.selector.items[1].id = "nav_id_1", "nav_id_2"

        result = json.loads(json.dumps(navigation.build(active_page_id="Page 1"), cls=plotly.utils.PlotlyJSONEncoder))
        expected = json.loads(json.dumps(navbar_div_default, cls=plotly.utils.PlotlyJSONEncoder))

        assert result == expected

    def test_navigation_all_options(self):
        navigation_configs = [
            vm.Navigation(),
            vm.Navigation(pages=["Page 1", "Page 2"]),
            vm.Navigation(selector=vm.Accordion(pages=["Page 1", "Page 2"])),
            vm.Navigation(selector=vm.Accordion(pages={"Accordion title": ["Page 1", "Page 2"]})),
            vm.Navigation(pages=["Page 1", "Page 2"], selector=vm.NavBar()),
            vm.Navigation(selector=vm.NavBar()),
            vm.Navigation(selector=vm.NavBar(pages=["Page 1", "Page 2"])),
            vm.Navigation(selector=vm.NavBar(items=[vm.NavItem(pages=["Page 1", "Page 2"])])),
            vm.Navigation(selector=vm.NavBar(items=[vm.NavItem(pages={"Icon 1": ["Page 1", "Page 2"]})])),
        ]

        for config in navigation_configs:
            navigation = config.build(active_page_id="Page 1")
            assert isinstance(navigation, html.Div)
