"""Unit tests for vizro.models.Navigation."""
import json
import re

import plotly
import pytest
from pydantic import ValidationError

import vizro.models as vm
from vizro.models._navigation._accordion import Accordion


@pytest.mark.usefixtures("vizro_app", "dashboard_prebuild")
class TestNavigationInstantiation:
    """Tests navigation model instantiation ."""

    @pytest.mark.parametrize("navigation", [None, vm.Navigation()])
    def test_navigation_default(self, page1, page2, navigation):
        # Navigation is optional inside Dashboard and navigation.pages will always be auto-populated if not provided
        dashboard = vm.Dashboard(pages=[page1, page2], navigation=navigation)
        assert hasattr(dashboard.navigation, "id")
        assert dashboard.navigation.pages == ["Page 1", "Page 2"]

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
    navigation.pre_build()

    assert navigation.id == "navigation"
    assert navigation.pages == pages
    assert isinstance(navigation._selector, Accordion)
    assert navigation._selector.pages == {"SELECT PAGE": ["Page 1", "Page 2"]}


@pytest.mark.usefixtures("vizro_app", "dashboard_prebuild")
@pytest.mark.parametrize("pages", [["Page 1", "Page 2"], {"Page 1": ["Page 1"], "Page 2": ["Page 2"]}])
def test_navigation_build(pages):
    navigation = vm.Navigation(pages=pages)
    navigation.pre_build()  # Required such that an Accordion is assigned as selector
    accordion = Accordion(pages=pages)
    navigation._selector.id = accordion.id

    result = json.loads(json.dumps(navigation.build(), cls=plotly.utils.PlotlyJSONEncoder))
    expected = json.loads(json.dumps(accordion.build(), cls=plotly.utils.PlotlyJSONEncoder))
    assert result == expected
