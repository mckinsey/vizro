"""Unit tests for vizro.models.NavBar."""
import json
import re

import plotly
import pytest
from pydantic import ValidationError

import vizro.models as vm
from dash import html


@pytest.mark.usefixtures("vizro_app", "dashboard_prebuild")
class TestNavBarInstantiation:
    """Tests accordion model instantiation."""

    def test_navbar_mandatory_only(self):
        navigation = vm.NavBar()
        assert hasattr(navigation, "id")
        assert navigation.pages == ["Page 1", "Page 2"]

    def test_navbar_valid_pages_as_list(self, pages_as_list):
        nav_bar = vm.NavBar(pages=pages_as_list, id="nav_bar")

        assert nav_bar.id == "nav_bar"
        assert nav_bar.pages == pages_as_list

    def test_navbar_valid_pages_as_dict(self, pages_as_dict):
        nav_bar = vm.NavBar(pages=pages_as_dict, id="nav_bar")

        assert nav_bar.id == "nav_bar"
        assert nav_bar.pages == pages_as_dict

    def test_navbar_valid_pages_not_all_included(self):
        nav_bar = vm.NavBar(pages=["Page 1"], id="nav_bar")
        assert nav_bar.id == "nav_bar"
        assert nav_bar.pages == ["Page 1"]

    def test_navbar_invalid_pages_empty_list(self):
        with pytest.raises(ValidationError, match="Ensure this value has at least 1 item."):
            vm.NavBar(pages=[], id="nav_bar")

    def test_navbar_invalid_pages_unknown_page(self):
        with pytest.raises(ValidationError, match=re.escape("Unknown page ID ['Test'] provided to argument 'pages'.")):
            vm.NavBar(pages=["Test"], id="nav_bar")


@pytest.mark.usefixtures("vizro_app", "dashboard_prebuild")
def test_navbar_build_default(navbar_div_default):
    navbar = vm.NavBar()

    navbar.items[0].id = "nav_id_1"
    navbar.items[1].id = "nav_id_2"
    result = json.loads(json.dumps(navbar.build(active_page_id="Page 1"), cls=plotly.utils.PlotlyJSONEncoder))
    expected = json.loads(json.dumps(navbar_div_default, cls=plotly.utils.PlotlyJSONEncoder))

    assert result == expected


@pytest.mark.usefixtures("vizro_app", "dashboard_prebuild")
def test_navbar_build_pages_as_list(navbar_div_default):
    navbar = vm.NavBar(pages=["Page 1", "Page 2"])

    navbar.items[0].id = "nav_id_1"
    navbar.items[1].id = "nav_id_2"
    result = json.loads(json.dumps(navbar.build(active_page_id="Page 1"), cls=plotly.utils.PlotlyJSONEncoder))
    expected = json.loads(json.dumps(navbar_div_default, cls=plotly.utils.PlotlyJSONEncoder))

    assert result == expected


@pytest.mark.usefixtures("vizro_app", "dashboard_prebuild")
def test_navbar_build_pages_as_dict(navbar_div_from_dict):
    navbar = vm.NavBar(pages={"Icon": ["Page 1", "Page 2"]})

    navbar.items[0].id = "accordion_list"
    result = json.loads(json.dumps(navbar.build(active_page_id="Page 1"), cls=plotly.utils.PlotlyJSONEncoder))

    print("result>>>>", result)
    expected = json.loads(json.dumps(navbar_div_from_dict, cls=plotly.utils.PlotlyJSONEncoder))

    assert result == expected


@pytest.mark.usefixtures("vizro_app", "dashboard_prebuild")
def test_navbar_build_items(navbar_div_default):
    navbar = vm.NavBar(items=[vm.NavItem(pages=["Page 1"]), vm.NavItem(pages=["Page 2"])])
    navbar.items[0].id = "nav_id_1"
    navbar.items[1].id = "nav_id_2"

    result = json.loads(json.dumps(navbar.build(active_page_id="Page 1"), cls=plotly.utils.PlotlyJSONEncoder))
    expected = json.loads(json.dumps(navbar_div_default, cls=plotly.utils.PlotlyJSONEncoder))

    assert result == expected


@pytest.mark.usefixtures("vizro_app", "dashboard_prebuild")
@pytest.mark.parametrize("pages", [(["Page 1", "Page 2"]), ([["Page 1"], ["Page 2"]])])
def test_navbar_and_navigation_build_default(navbar_div_default, pages):
    if isinstance(pages[0], str):
        navbar = vm.NavBar(pages=pages)
    else:
        navbar = vm.NavBar(items=[vm.NavItem(pages=pages[0]), vm.NavItem(pages=pages[1])])

    navbar.items[0].id = "nav_id_1"
    navbar.items[1].id = "nav_id_2"
    result = json.loads(json.dumps(navbar.build(active_page_id="Page 1"), cls=plotly.utils.PlotlyJSONEncoder))
    expected = json.loads(json.dumps(navbar_div_default, cls=plotly.utils.PlotlyJSONEncoder))

    assert result == expected


@pytest.mark.usefixtures("vizro_app", "dashboard_prebuild")
@pytest.mark.parametrize(
    "nav_pages, item_pages",
    [
        (["Page 1", "Page 2"], [["Page 1"], ["Page 2"]]),
        (
            {"title_1": ["Page 1", "Page 2"], "title_2": ["Page 1", "Page 2"]},
            [["Page 1", "Page 2"], ["Page 1", "Page 2"]],
        ),
    ],
)
def test_navbar_and_navigation_build_equality(nav_pages, item_pages, nav_id_1="nav_id_1", nav_id_2="nav_id_2"):
    navbar_with_pages = vm.NavBar(pages=nav_pages)
    navbar_with_items = vm.NavBar(items=[vm.NavItem(pages=item_pages[0]), vm.NavItem(pages=item_pages[1])])

    navbar_with_pages.items[0].id, navbar_with_pages.items[1].id = nav_id_1, nav_id_2
    navbar_with_pages.items[0].selector.id, navbar_with_pages.items[1].selector.id = "accordion_1", "accordion_2"

    navbar_with_items.items[0].id, navbar_with_items.items[1].id = nav_id_1, nav_id_2
    navbar_with_items.items[0].selector.id, navbar_with_items.items[1].selector.id = "accordion_1", "accordion_2"

    navbar_with_pages = json.loads(
        json.dumps(navbar_with_pages.build(active_page_id="Page 1"), cls=plotly.utils.PlotlyJSONEncoder)
    )
    navbar_with_items = json.loads(
        json.dumps(navbar_with_items.build(active_page_id="Page 1"), cls=plotly.utils.PlotlyJSONEncoder)
    )

    assert navbar_with_pages == navbar_with_items


@pytest.mark.usefixtures("vizro_app", "dashboard_prebuild")
@pytest.mark.parametrize(
    "nav_pages, item_pages",
    [
        (["Page 1"], ["Page 1"]),
        ({"title_1": ["Page 1"]}, {"title_1": ["Page 1"]}),
    ],
)
def test_navbar_build_equality(nav_pages, item_pages, nav_id="nav_id"):
    navbar_with_pages = vm.NavBar(pages=nav_pages)
    navbar_with_items = vm.NavBar(items=[vm.NavItem(pages=item_pages, id=nav_id)])

    navbar_with_pages.items[0].id = nav_id

    navbar_with_pages = json.loads(
        json.dumps(navbar_with_pages.build(active_page_id="Page 1"), cls=plotly.utils.PlotlyJSONEncoder)
    )
    navbar_with_items = json.loads(
        json.dumps(navbar_with_items.build(active_page_id="Page 1"), cls=plotly.utils.PlotlyJSONEncoder)
    )

    assert navbar_with_pages == navbar_with_items
