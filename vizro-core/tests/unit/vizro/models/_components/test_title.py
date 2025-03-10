"""Unit tests for vizro.models.Card."""

import dash_bootstrap_components as dbc
import pytest
from asserts import assert_component_equal
from dash import dcc, html
from pydantic import ValidationError

import vizro.models as vm


class TestTitleInstantiation:
    """Tests model instantiation."""

    def test_create_title_mandatory_only(self):
        title = vm.Title(text="Text to test title", tooltip="Tooltip text to test Title")

        assert hasattr(title, "id")
        assert title.type == "title"
        assert title.text == "Text to test title"
        assert title.tooltip == "Tooltip text to test Title"

    @pytest.mark.parametrize("id, icon", [("id_1", "help"), ("id_2", "warning")])
    def test_create_title_mandatory_and_optional(self, id, icon):
        title = vm.Title(id=id, text="Text to test title", icon=icon, tooltip="Test text for tooltip")

        assert title.id == id
        assert title.type == "title"
        assert title.text == "Text to test title"
        assert title.icon == icon
        assert title.tooltip == "Test text for tooltip"

    def test_mandatory_text_missing(self):
        with pytest.raises(ValidationError, match="Field required"):
            vm.Title(tooltip="Test text for tooltip")

    def test_mandatory_tooltip_missing(self):
        with pytest.raises(ValidationError, match="Field required"):
            vm.Title(text="Text to test title")

    def test_none_as_text(self):
        with pytest.raises(ValidationError, match="Input should be a valid string"):
            vm.Title(text=None)


class TestBuildMethod:
    """Tests build method."""

    def test_title_build(self):
        title = vm.Title(id="title_id", text="Test title", tooltip="Test tooltip")
        title = title.build()

        expected_title = html.Div(
            id="dashboard-title",
            children=[
                html.H2(id="dashboard-title-text", children="Test title"),
                html.Span("info", className="material-symbols-outlined", id="title_id-icon"),
                dbc.Tooltip(
                    id="title_id-tooltip",
                    children=dcc.Markdown("Test tooltip", dangerously_allow_html=True, id="dashboard-title-markdown"),
                    placement="left",
                    target="title_id-icon",
                ),
            ],
        )

        assert_component_equal(title, expected_title)
