"""Unit tests for vizro.models.Button."""
import json

import dash_bootstrap_components as dbc
import plotly
import pytest
from dash import html

import vizro.models as vm
from vizro.actions import export_data


@pytest.fixture
def expected_button():
    return html.Div(
        [
            dbc.Button(
                id="button_id",
                children="Click me!",
                className="button_primary",
            ),
        ],
        className="button_container",
        id="button_id_outer",
    )


class TestButtonInstantiation:
    """Tests model instantiation and the validators run at that time."""

    def test_create_default_button(self):
        button = vm.Button()
        assert hasattr(button, "id")
        assert button.type == "button"
        assert button.text == "Click me!"
        assert button.actions == []

    @pytest.mark.parametrize(
        "text",
        ["Test", 123, 1.23, True, """# Header""", """<p>Hello </p>"""],
    )
    def test_create_button_with_optional(self, text):
        button = vm.Button(text=text)
        assert hasattr(button, "id")
        assert button.type == "button"
        assert button.text == str(text)
        assert button.actions == []

    def test_set_action_via_validator(self):
        button = vm.Button(actions=[vm.Action(function=export_data())])
        actions_chain = button.actions[0]
        assert actions_chain.trigger.component_property == "n_clicks"


class TestBuildMethod:
    def test_button_build(self, expected_button):
        button = vm.Button(id="button_id", text="Click me!").build()
        result = json.loads(json.dumps(button, cls=plotly.utils.PlotlyJSONEncoder))
        expected = json.loads(json.dumps(expected_button, cls=plotly.utils.PlotlyJSONEncoder))

        assert result == expected
