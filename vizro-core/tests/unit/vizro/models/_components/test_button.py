"""Unit tests for vizro.models.Button."""

import dash_bootstrap_components as dbc
import pytest
from asserts import assert_component_equal

import vizro.models as vm
from vizro.actions import export_data


class TestButtonInstantiation:
    """Tests model instantiation and the validators run at that time."""

    def test_create_default_button(self):
        button = vm.Button()
        assert hasattr(button, "id")
        assert button.type == "button"
        assert button.text == "Click me!"
        assert button.href == ""
        assert button.actions == []

    @pytest.mark.parametrize(
        "text, href",
        [
            ("Test", "/page_1_reference"),
            ("Test", "https://www.google.de/"),
            (123, "/"),
            ("""# Header""", "/"),
            (1.23, "/"),
            ("""<p>Hello </p>""", "/"),
            (True, "/"),
        ],
    )
    def test_create_button_with_optional(self, text, href):
        button = vm.Button(id="button-id", text=text, href=href)

        assert button.id == "button-id"
        assert button.type == "button"
        assert button.text == str(text)
        assert button.href == href
        assert button.actions == []

    def test_set_action_via_validator(self):
        button = vm.Button(actions=[vm.Action(function=export_data())])
        actions_chain = button.actions[0]
        assert actions_chain.trigger.component_property == "n_clicks"


class TestBuildMethod:
    def test_button_build_wo_href(self):
        button = vm.Button(id="button_id", text="My text").build()
        expected = dbc.Button(id="button_id", children="My text", href="", target="_top")
        assert_component_equal(button, expected)

    def test_button_build_with_href(self):
        button = vm.Button(id="button_id", text="My text", href="https://www.google.com").build()
        expected = dbc.Button(id="button_id", children="My text", href="https://www.google.com", target="_top")
        assert_component_equal(button, expected)
