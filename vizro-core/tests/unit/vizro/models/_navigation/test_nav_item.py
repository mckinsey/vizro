"""Unit tests for vizro.models.NavItem."""
import json
import re

import plotly
import pytest
from pydantic import ValidationError

import vizro.models as vm


@pytest.mark.usefixtures("vizro_app", "dashboard_prebuild")
class TestNavItemInstantiation:
    """Tests NavItem model instantiation."""

    def test_navitem_mandatory_only(self):
        nav_item = vm.NavItem(pages=["Page 1", "Page 2"])

        assert nav_item.type == "navitem"
        assert nav_item.pages == ["Page 1", "Page 2"]
        assert nav_item.icon == "dashboard"
        assert nav_item.max_text_length == 8
        assert hasattr(nav_item, "id")
        assert hasattr(nav_item, "text")
        assert hasattr(nav_item, "tooltip")
        assert hasattr(nav_item, "selector")

    def test_navitem_mandatory_and_optional(self):
        nav_item = vm.NavItem(
            pages=["Page 1", "Page 2"], id="nav_item", icon="home", text="Homepage", tooltip="Homepage icon"
        )

        assert nav_item.id == "nav_item"
        assert nav_item.type == "navitem"
        assert nav_item.pages == ["Page 1", "Page 2"]
        assert nav_item.icon == "home"
        assert nav_item.text == "Homepage"
        assert nav_item.tooltip == "Homepage icon"

    def test_navitem_text_validation(self):
        nav_item = vm.NavItem(pages=["Page 1"], text="Homepage", tooltip="Homepage icon")
        nav_item.set_text_and_tooltip()
        assert nav_item.text == "Homepage"
        assert nav_item.tooltip == "Homepage icon"

    def test_navitem_invalid_pages_empty_list(self):
        with pytest.raises(ValidationError, match="Ensure this value has at least 1 item."):
            vm.NavItem(pages=[], id="nav_item")

    def test_navitem_invalid_pages_unknown_page(self):
        with pytest.raises(ValidationError, match=re.escape("Unknown page ID ['Test'] provided to argument 'pages'.")):
            vm.NavItem(pages=["Test"], id="nav_item")


@pytest.mark.usefixtures("vizro_app", "dashboard_prebuild")
class TestNavItemBuildMethod:
    """Tests NavItem model build method."""

    def test_navitem_build_mandatory_only(self, nav_item_default):
        nav_item = vm.NavItem(pages=["Page 1", "Page 2"])
        nav_item.id = "navitem"

        result = json.loads(json.dumps(nav_item.build(active_page_id="Page 1"), cls=plotly.utils.PlotlyJSONEncoder))
        expected = json.loads(json.dumps(nav_item_default, cls=plotly.utils.PlotlyJSONEncoder))

        assert result == expected

    def test_navitem_build_mandatory_and_optional(self, nav_item_with_optional):
        nav_item = vm.NavItem(pages=["Page 1", "Page 2"], icon="home", text="This is a long text input")
        nav_item.id = "navitem"

        result = json.loads(json.dumps(nav_item.build(active_page_id="Page 1"), cls=plotly.utils.PlotlyJSONEncoder))
        expected = json.loads(json.dumps(nav_item_with_optional, cls=plotly.utils.PlotlyJSONEncoder))

        assert result == expected
