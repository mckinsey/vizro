"""Unit tests for vizro.models.Navigation."""
import json

import plotly
import pytest
from pydantic import ValidationError

import vizro.models as vm
from vizro.models._navigation._accordion import Accordion


@pytest.mark.usefixtures("dashboard_build")
class TestNavigationInstantiation:
    """Tests navigation model instantiation."""

    def test_navigation_default(self):
        navigation = vm.Navigation(id="navigation")
        assert navigation.id == "navigation"
        assert navigation.pages is None

    def test_navigation_pages_as_list(self, pages_as_list):
        navigation = vm.Navigation(pages=pages_as_list, id="navigation")
        assert navigation.id == "navigation"
        assert navigation.pages == pages_as_list

    def test_navigation_pages_as_dict(self, pages_as_dict):
        navigation = vm.Navigation(pages=pages_as_dict, id="navigation")
        assert navigation.id == "navigation"
        assert navigation.pages == pages_as_dict

    def test_navigation_not_all_pages_included(self, dashboard_build):
        with pytest.warns(UserWarning):
            vm.Navigation(pages=["Page 1"])

    @pytest.mark.parametrize(
        "pages, expected_error",
        [
            ([], "Ensure this value has at least 1 item."),
            ([Accordion()], "2 validation errors for Navigation"),
            (["Page_1", "Page 2"], "1 validation error for Navigation"),
        ],
    )
    def test_field_invalid_pages_input(self, pages, expected_error):
        with pytest.raises(ValidationError, match=expected_error):
            vm.Navigation(pages=pages)


@pytest.mark.usefixtures("dashboard_build")
class TestNavigationBuild:
    """Tests navigation build method."""

    @pytest.mark.parametrize("pages", [["Page 1", "Page 2"], {"Page 1": ["Page 1"], "Page 2": ["Page 2"]}, None])
    def test_navigation_build(self, pages):
        navigation = vm.Navigation(pages=pages)
        navigation.pre_build()
        accordion = Accordion(pages=pages)
        navigation._selector.id = accordion.id

        result = json.loads(json.dumps(navigation.build(), cls=plotly.utils.PlotlyJSONEncoder))
        expected = json.loads(json.dumps(accordion.build(), cls=plotly.utils.PlotlyJSONEncoder))
        assert result == expected
