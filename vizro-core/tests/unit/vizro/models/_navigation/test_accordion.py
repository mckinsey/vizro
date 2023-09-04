"""Unit tests for vizro.models.Accordion."""
import json

import plotly
import pytest
from pydantic import ValidationError

import vizro.models as vm
from vizro.models._navigation._accordion import Accordion


@pytest.mark.usefixtures("dashboard_build")
class TestAccordionInstantiation:
    """Tests accordion model instantiation."""

    def test_create_accordion_default(self):
        accordion = Accordion(id="accordion_id")
        assert accordion.id == "accordion_id"
        assert accordion.pages is None

    def test_create_accordion_pages_as_list(self, pages_as_list):
        accordion = Accordion(pages=pages_as_list, id="accordion_id")
        assert accordion.id == "accordion_id"
        assert accordion.pages == pages_as_list

    def test_create_accordion_pages_as_dict(self, pages_as_dict):
        accordion = Accordion(pages=pages_as_dict, id="accordion_id")
        assert accordion.id == "accordion_id"
        assert accordion.pages == pages_as_dict

    def test_field_invalid_pages_input_type(self):
        with pytest.raises(ValidationError, match="2 validation errors for Accordion"):
            Accordion(pages=[vm.Button()])

    def test_field_invalid_pages_empty_list(self):
        with pytest.raises(ValidationError, match="Ensure this value has at least 1 item."):
            Accordion(pages=[])


@pytest.mark.usefixtures("dashboard_build")
class TestAccordionBuild:
    """Tests accordion build method."""

    def test_accordion_build_default(self, accordion_from_page_as_list):
        accordion_div = Accordion(id="accordion_list")
        component = accordion_div.build()

        result = json.loads(json.dumps(component, cls=plotly.utils.PlotlyJSONEncoder))
        expected = json.loads(json.dumps(accordion_from_page_as_list, cls=plotly.utils.PlotlyJSONEncoder))

        assert result == expected

    def test_accordion_build_pages_as_list(self, pages_as_list, accordion_from_page_as_list):
        accordion_div = Accordion(pages=pages_as_list, id="accordion_list")
        component = accordion_div.build()

        result = json.loads(json.dumps(component, cls=plotly.utils.PlotlyJSONEncoder))
        expected = json.loads(json.dumps(accordion_from_page_as_list, cls=plotly.utils.PlotlyJSONEncoder))

        assert result == expected

    def test_accordion_build_pages_as_dict(self, pages_as_dict, accordion_from_pages_as_dict):
        accordion_div = Accordion(pages=pages_as_dict, id="accordion_dict")
        component = accordion_div.build()

        result = json.loads(json.dumps(component, cls=plotly.utils.PlotlyJSONEncoder))
        expected = json.loads(json.dumps(accordion_from_pages_as_dict, cls=plotly.utils.PlotlyJSONEncoder))

        assert result == expected

    def test_navigation_not_all_pages_included(self, dashboard_build):
        with pytest.warns(UserWarning):
            Accordion(pages=["Page 1"])

    @pytest.mark.parametrize(
        "accordion_pages, id_accordion",
        [
            (["Page 1", "Page 2"], "accordion_4"),
            (None, "accordion_5"),
        ],
    )
    def test_accordion_same_result_with_different_config(
        self, accordion_pages, id_accordion, accordion_from_page_as_list
    ):
        result_navigation = Accordion(pages=accordion_pages, id=id_accordion)
        expected_navigation = accordion_from_page_as_list

        # setting accordion id to fix the random id generation
        expected_navigation.children.id = id_accordion

        result = json.loads(json.dumps(result_navigation.build(), cls=plotly.utils.PlotlyJSONEncoder))
        expected = json.loads(json.dumps(expected_navigation, cls=plotly.utils.PlotlyJSONEncoder))

        assert result == expected
