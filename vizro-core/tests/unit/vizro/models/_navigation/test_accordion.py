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

    @pytest.mark.parametrize("pages", [["Page 1", "Page 2"], None])
    def test_accordion_build_default(self, pages, accordion_from_page_as_list):
        accordion = Accordion(pages=pages, id="accordion_list").build()
        result = json.loads(json.dumps(accordion, cls=plotly.utils.PlotlyJSONEncoder))
        expected = json.loads(json.dumps(accordion_from_page_as_list, cls=plotly.utils.PlotlyJSONEncoder))
        assert result == expected

    def test_accordion_build_pages_as_list(self, pages_as_list, accordion_from_page_as_list):
        accordion = Accordion(pages=pages_as_list, id="accordion_list").build()
        result = json.loads(json.dumps(accordion, cls=plotly.utils.PlotlyJSONEncoder))
        expected = json.loads(json.dumps(accordion_from_page_as_list, cls=plotly.utils.PlotlyJSONEncoder))
        assert result == expected

    def test_accordion_build_pages_as_dict(self, pages_as_dict, accordion_from_pages_as_dict):
        accordion = Accordion(pages=pages_as_dict, id="accordion_dict").build()
        result = json.loads(json.dumps(accordion, cls=plotly.utils.PlotlyJSONEncoder))
        expected = json.loads(json.dumps(accordion_from_pages_as_dict, cls=plotly.utils.PlotlyJSONEncoder))
        assert result == expected

    def test_accordion_build_single_page_accordion(self):
        accordion = Accordion(pages=["Page 1"], id="single_accordion").build()
        assert accordion is None

    def test_navigation_not_all_pages_included(self, dashboard_build):
        with pytest.warns(UserWarning):
            Accordion(pages=["Page 1"])
