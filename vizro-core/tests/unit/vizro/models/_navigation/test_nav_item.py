"""Unit tests for vizro.models.NavItem."""
import json
import re

import dash_bootstrap_components as dbc
import plotly
import pytest
from dash import html
from pydantic import ValidationError

import vizro.models as vm


@pytest.mark.usefixtures("vizro_app", "prebuilt_dashboard")
class TestNavItemInstantiation:
    """Tests NavItem model instantiation."""

    def test_navitem_mandatory_only(self):
        nav_item = vm.NavItem(text="Text")

        assert hasattr(nav_item, "id")
        assert nav_item.text == "Text"
        assert nav_item.icon is None
        assert nav_item.pages == []

    def test_navitem_mandatory_and_optional(self, pages_as_list):
        nav_item = vm.NavItem(id="nav_item", icon="home", text="Homepage", pages=pages_as_list)

        assert nav_item.id == "nav_item"
        assert nav_item.text == "Homepage"
        assert nav_item.icon == "home"
        assert nav_item.pages == pages_as_list

    def test_nav_item_valid_pages_as_dict(self, pages_as_dict):
        nav_item = vm.NavItem(pages=pages_as_dict, text="Text")
        assert nav_item.pages == pages_as_dict

    def test_mandatory_text_missing(self):
        with pytest.raises(ValidationError, match="field required"):
            vm.NavItem()

    @pytest.mark.parametrize("pages", [{"Group": []}, []])
    def test_invalid_field_pages_no_ids_provided(self, pages):
        with pytest.raises(ValidationError, match="Ensure this value has at least 1 item."):
            vm.NavItem(pages=pages)

    def test_invalid_field_pages_wrong_input_type(self):
        with pytest.raises(ValidationError, match="str type expected"):
            vm.NavItem(pages=[vm.Page(title="Page 3", components=[vm.Button()])])

    @pytest.mark.parametrize("pages", [["non existent page"], {"Group": ["non existent page"]}])
    def test_invalid_page(self, pages):
        with pytest.raises(
            ValidationError, match=re.escape("Unknown page ID ['non existent page'] provided to " "argument 'pages'.")
        ):
            vm.NavItem(pages=pages)


@pytest.mark.usefixtures("vizro_app", "prebuilt_dashboard")
class TestNavItemPreBuildMethod:
    def test_nav_item(self, pages_as_dict):
        nav_item = vm.NavItem(text="Text", pages=pages_as_dict)
        nav_item.pre_build()
        assert isinstance(nav_item._selector, vm.Accordion)
        assert nav_item._selector.pages == pages_as_dict


@pytest.mark.usefixtures("vizro_app", "prebuilt_dashboard")
class TestNavItemBuildMethod:
    """Tests NavItem model build method."""

    def test_nav_item_active(self, pages_as_dict):
        nav_item = vm.NavItem(text="Text", pages=pages_as_dict)
        nav_item.pre_build()
        built_nav_item = nav_item.build(active_page_id="Page 1")
        assert isinstance(built_nav_item[nav_item.id], dbc.Button)
        assert built_nav_item[nav_item.id].href == "/"
        assert built_nav_item[nav_item.id].active
        assert isinstance(built_nav_item["nav_panel_outer"], html.Div)

    def test_nav_item_not_active(self, pages_as_dict):
        nav_item = vm.NavItem(text="Text", pages=pages_as_dict)
        nav_item.pre_build()
        built_nav_item = nav_item.build(active_page_id="Page 3")
        assert isinstance(built_nav_item[nav_item.id], dbc.Button)
        assert built_nav_item[nav_item.id].href == "/"
        assert not built_nav_item[nav_item.id].active
        assert "nav_panel_outer" not in built_nav_item
