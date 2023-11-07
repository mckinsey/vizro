"""Unit tests for vizro.models.NavBar."""
import json
import re

import plotly
import pytest
from pydantic import ValidationError

import vizro.models as vm


@pytest.mark.usefixtures("vizro_app", "dashboard_prebuild")
class TestNavBarInstantiation:
    """Tests NavBar model instantiation."""

    def test_navbar_mandatory_only(self):
        nav_bar = vm.NavBar()

        assert hasattr(nav_bar, "id")
        assert nav_bar.type == "navbar"
        assert nav_bar.pages == ["Page 1", "Page 2"]

    def test_navbar_valid_pages_as_list(self, pages_as_list):
        nav_bar = vm.NavBar(pages=pages_as_list, id="nav_bar")

        assert nav_bar.id == "nav_bar"
        assert nav_bar.type == "navbar"
        assert nav_bar.pages == pages_as_list

    def test_navbar_valid_pages_as_dict(self, pages_as_dict):
        nav_bar = vm.NavBar(pages=pages_as_dict, id="nav_bar")

        assert nav_bar.id == "nav_bar"
        assert nav_bar.type == "navbar"
        assert nav_bar.pages == pages_as_dict

    def test_navbar_valid_pages_not_all_included(self):
        nav_bar = vm.NavBar(pages=["Page 1"], id="nav_bar")

        assert nav_bar.id == "nav_bar"
        assert nav_bar.type == "navbar"
        assert nav_bar.pages == ["Page 1"]

    def test_navbar_invalid_pages_empty_list(self):
        with pytest.raises(ValidationError, match="Ensure this value has at least 1 item."):
            vm.NavBar(pages=[], id="nav_bar")

    def test_navbar_invalid_pages_unknown_page(self):
        with pytest.raises(ValidationError, match=re.escape("Unknown page ID ['Test'] provided to argument 'pages'.")):
            vm.NavBar(pages=["Test"], id="nav_bar")


@pytest.mark.usefixtures("vizro_app", "dashboard_prebuild")
class TestNavBarBuildMethod:
    """Tests NavBar model build method."""

    def test_navbar_build_default(self, navbar_div_default):
        navbar = vm.NavBar()
        navbar.items[0].id, navbar.items[1].id = "nav_id_1", "nav_id_2"

        result = json.loads(json.dumps(navbar.build(active_page_id="Page 1"), cls=plotly.utils.PlotlyJSONEncoder))
        expected = json.loads(json.dumps(navbar_div_default, cls=plotly.utils.PlotlyJSONEncoder))

        assert result == expected

    @pytest.mark.parametrize(
        "pages",
        [
            (["Page 1", "Page 2"]),  # pages provided as list
            ({"Icon 1": ["Page 1"], "Icon 2": ["Page 2"]}),  # pages provided as dict
        ],
    )
    def test_navbar_build_pages(self, navbar_div_default, pages):
        navbar = vm.NavBar(pages=pages)
        navbar.items[0].id, navbar.items[1].id = "nav_id_1", "nav_id_2"
        navbar.items[0].selector.id, navbar.items[1].selector.id = "accordion_list", "accordion_list"

        result = json.loads(json.dumps(navbar.build(active_page_id="Page 1"), cls=plotly.utils.PlotlyJSONEncoder))
        expected = json.loads(json.dumps(navbar_div_default, cls=plotly.utils.PlotlyJSONEncoder))

        assert result == expected

    @pytest.mark.parametrize(
        "nav_item_1, nav_item_2",
        [
            (["Page 1"], ["Page 2"]),  # NavItem pages provided as list
            ({"Icon 1": ["Page 1"]}, {"Icon 2": ["Page 2"]}),  # NavItem pages provided as dict
        ],
    )
    def test_navbar_build_items(self, navbar_div_default, nav_item_1, nav_item_2):
        navbar = vm.NavBar(items=[vm.NavItem(pages=nav_item_1), vm.NavItem(pages=nav_item_2)])
        navbar.items[0].id, navbar.items[1].id = "nav_id_1", "nav_id_2"

        result = json.loads(json.dumps(navbar.build(active_page_id="Page 1"), cls=plotly.utils.PlotlyJSONEncoder))
        expected = json.loads(json.dumps(navbar_div_default, cls=plotly.utils.PlotlyJSONEncoder))

        assert result == expected
