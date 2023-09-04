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

    def test_navigation_default(self, accordion_from_page_as_list):
        result_navigation = vm.Navigation()
        result_navigation.pre_build()

        # setting accordion id to fix the random id generation
        result_navigation._selector.id = "accordion_list"

        result = json.loads(json.dumps(result_navigation.build(), cls=plotly.utils.PlotlyJSONEncoder))
        expected = json.loads(json.dumps(accordion_from_page_as_list, cls=plotly.utils.PlotlyJSONEncoder))

        assert result == expected

    @pytest.mark.parametrize(
        "navigation_pages",
        [
            (["Page 1", "Page 2"]),
            None,
        ],
    )
    def test_navigation_same_result_with_different_config(self, navigation_pages, accordion_from_page_as_list):
        id_accordion = "accordion_6"

        result_navigation = vm.Navigation(pages=navigation_pages)
        result_navigation.pre_build()

        # setting accordion id to fix the random id generation
        result_navigation._selector.id = id_accordion
        accordion_from_page_as_list.children.id = id_accordion

        result = json.loads(json.dumps(result_navigation.build(), cls=plotly.utils.PlotlyJSONEncoder))
        expected = json.loads(json.dumps(accordion_from_page_as_list, cls=plotly.utils.PlotlyJSONEncoder))

        assert result == expected

    def test_navigation_pages_as_list(self, pages_as_list, accordion_from_page_as_list):
        result_navigation = vm.Navigation(pages=pages_as_list)
        result_navigation.pre_build()

        # setting accordion id to fix the random id generation
        result_navigation._selector.id = "accordion_list"

        result = json.loads(json.dumps(result_navigation.build(), cls=plotly.utils.PlotlyJSONEncoder))
        expected = json.loads(json.dumps(accordion_from_page_as_list, cls=plotly.utils.PlotlyJSONEncoder))

        assert result == expected

    def test_navigation_pages_as_dict(self, pages_as_dict, accordion_from_pages_as_dict):
        result_navigation = vm.Navigation(pages=pages_as_dict)
        result_navigation.pre_build()

        # setting accordion id to fix the random id generation
        result_navigation._selector.id = "accordion_dict"

        result = json.loads(json.dumps(result_navigation.build(), cls=plotly.utils.PlotlyJSONEncoder))
        expected = json.loads(json.dumps(accordion_from_pages_as_dict, cls=plotly.utils.PlotlyJSONEncoder))

        assert result == expected
