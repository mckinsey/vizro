"""Unit tests for vizro.models.Accordion."""
import json

import plotly
import pytest
from dash import html
from pydantic import ValidationError

import vizro.models as vm
from vizro.models._navigation._accordion import Accordion


@pytest.mark.usefixtures("vizro_app", "dashboard_prebuild")
class TestAccordionInstantiation:
    """Tests accordion model instantiation."""

    def test_accordion_valid_pages_as_list(self, pages_as_list):
        accordion = Accordion(pages=pages_as_list, id="accordion_id")
        assert accordion.id == "accordion_id"
        assert accordion.pages == {"SELECT PAGE": pages_as_list}

    def test_accordion_valid_pages_as_dict(self, pages_as_dict):
        accordion = Accordion(pages=pages_as_dict, id="accordion_id")
        assert accordion.id == "accordion_id"
        assert accordion.pages == pages_as_dict

    def test_navigation_valid_pages_not_all_included(self):
        accordion = Accordion(pages=["Page 1"], id="accordion_id")
        assert accordion.id == "accordion_id"
        assert accordion.pages == {"SELECT PAGE": ["Page 1"]}

    def test_invalid_field_pages_required(self):
        with pytest.raises(ValidationError, match="field required"):
            Accordion()

    @pytest.mark.parametrize("pages", [{"SELECT PAGE": []}, []])
    def test_invalid_field_pages_no_ids_provided(self, pages):
        with pytest.raises(ValidationError, match="Ensure this value has at least 1 item."):
            Accordion(pages=pages)

    def test_invalid_field_pages_wrong_input_type(self):
        with pytest.raises(ValidationError, match="str type expected"):
            Accordion(pages=[vm.Page(title="Page 3", components=[vm.Button()])])


@pytest.mark.usefixtures("vizro_app", "dashboard_prebuild")
class TestAccordionBuild:
    """Tests accordion build method."""

    def test_accordion_build_pages_as_list(self, pages_as_list, accordion_from_page_as_list):
        accordion = Accordion(pages=pages_as_list, id="accordion_list").build(active_page_id="Page 1")
        result = json.loads(json.dumps(accordion, cls=plotly.utils.PlotlyJSONEncoder))
        expected = json.loads(json.dumps(accordion_from_page_as_list, cls=plotly.utils.PlotlyJSONEncoder))
        assert result == expected

    def test_accordion_build_pages_as_dict(self, pages_as_dict, accordion_from_pages_as_dict):
        accordion = Accordion(pages=pages_as_dict, id="accordion_dict").build(active_page_id="Page 1")
        result = json.loads(json.dumps(accordion, cls=plotly.utils.PlotlyJSONEncoder))
        expected = json.loads(json.dumps(accordion_from_pages_as_dict, cls=plotly.utils.PlotlyJSONEncoder))
        assert result == expected

    def test_single_page_and_hidden_div(self):
        accordion = Accordion(pages=["Page 1"]).build()
        result = json.loads(json.dumps(accordion, cls=plotly.utils.PlotlyJSONEncoder))
        expected = json.loads(json.dumps(html.Div(hidden=True), cls=plotly.utils.PlotlyJSONEncoder))
        assert result == expected
