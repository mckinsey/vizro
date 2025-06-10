"""Unit tests for vizro.models.Tooltip."""

import dash_bootstrap_components as dbc
import pytest
from asserts import assert_component_equal
from dash import dcc, html
from pydantic import ValidationError

from vizro.models import Tooltip


class TestTooltipInstantiation:
    """Tests model instantiation."""

    def test_create_tooltip_mandatory_only(self):
        tooltip = Tooltip(text="Tooltip text", icon="info")

        assert hasattr(tooltip, "id")
        assert tooltip.text == "Tooltip text"
        assert tooltip.icon == "info"
        assert tooltip._action_outputs == {
            "__default__": f"{tooltip.id}-text.children",
            "text": f"{tooltip.id}-text.children",
            "icon": f"{tooltip.id}-icon.children",
        }

    def test_validate_tooltip_invalid(self):
        with pytest.raises(ValidationError):
            Tooltip(text="Tooltip text")


class TestTooltipBuild:
    """Tests model build method."""

    def test_tooltip_build(self):
        tooltip = Tooltip(text="Tooltip text", icon="help", id="tooltip").build()

        expected_tooltip = html.Div(
            [
                html.Span("help", id="tooltip-icon", className="material-symbols-outlined tooltip-icon"),
                dbc.Tooltip(
                    children=dcc.Markdown("Tooltip text", id="tooltip-text", className="card-text"),
                    id="tooltip",
                    target="tooltip-icon",
                    autohide=False,
                ),
            ]
        )

        assert_component_equal(tooltip, expected_tooltip)

    def test_tooltip_build_with_extra(self):
        tooltip = Tooltip(text="Tooltip text", icon="help", id="tooltip", extra={"flip": False}).build()

        expected_tooltip = html.Div(
            [
                html.Span("help", id="tooltip-icon", className="material-symbols-outlined tooltip-icon"),
                dbc.Tooltip(
                    children=dcc.Markdown("Tooltip text", id="tooltip-text", className="card-text"),
                    id="tooltip",
                    target="tooltip-icon",
                    autohide=False,
                    flip=False,
                ),
            ]
        )

        assert_component_equal(tooltip, expected_tooltip)
