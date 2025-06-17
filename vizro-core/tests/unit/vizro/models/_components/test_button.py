"""Unit tests for vizro.models.Button."""

import dash_bootstrap_components as dbc
import pytest
from asserts import assert_component_equal
from dash import dcc, html
from pydantic import ValidationError

import vizro.models as vm
from vizro.actions import export_data


class TestButtonInstantiation:
    """Tests model instantiation and the validators run at that time."""

    def test_create_default_button_mandatory_only(self):
        button = vm.Button()
        assert hasattr(button, "id")
        assert button.type == "button"
        assert button.text == "Click me!"
        assert button.href == ""
        assert button.actions == []
        assert button.variant == "filled"
        assert button._action_outputs == {"text": f"{button.id}.children"}
        assert button.description is None

    @pytest.mark.parametrize(
        "text, href, variant",
        [
            ("Test", "/page_1_reference", "plain"),
            ("Test", "www.google.de/", "filled"),
            ("""# Header""", "/", "outlined"),
            ("""<p>Hello </p>""", "/", "plain"),
        ],
    )
    def test_create_button_mandatory_and_optional(self, text, href, variant):
        button = vm.Button(id="button-id", text=text, href=href, variant=variant, description="This is description")

        assert button.id == "button-id"
        assert button.type == "button"
        assert button.text == str(text)
        assert button.href == href
        assert button.actions == []
        assert button.variant == variant
        assert isinstance(button.description, vm.Tooltip)
        assert button._action_outputs == {
            "text": f"{button.id}.children",
            "description": f"{button.description.id}-text.children",
        }

    def test_set_action_via_validator(self):
        button = vm.Button(actions=[vm.Action(function=export_data())])
        actions_chain = button.actions[0]
        assert actions_chain.trigger.component_property == "n_clicks"

    def test_invalid_variant(self):
        with pytest.raises(ValidationError, match="Input should be 'plain', 'filled' or 'outlined'."):
            vm.Button(variant="test")


class TestBuildMethod:
    def test_button_build(self):
        result = vm.Button(id="button", text="Click me!").build()
        assert_component_equal(
            result,
            dbc.Button(
                html.Span(["Click me!", None], className="button-text"),
                id="button",
                href="",
                target="_top",
                color="primary",
            ),
        )

    def test_button_build_with_extra(self):
        """Test that extra arguments correctly override defaults."""
        result = vm.Button(
            id="button", text="Click me!", extra={"color": "success", "outline": True, "href": "www.google.com"}
        ).build()
        assert_component_equal(
            result,
            dbc.Button(
                html.Span(["Click me!", None], className="button-text"),
                id="button",
                color="success",
                outline=True,
                href="www.google.com",
                target="_top",
            ),
        )

    def test_button_build_with_href(self):
        button = vm.Button(id="button_id", text="My text!", href="www.google.com").build()
        expected = dbc.Button(
            id="button_id",
            children=html.Span(["My text!", None], className="button-text"),
            href="www.google.com",
            target="_top",
            color="primary",
        )
        assert_component_equal(button, expected)

    @pytest.mark.parametrize(
        "variant, expected_color",
        [("plain", "link"), ("filled", "primary"), ("outlined", "secondary")],
    )
    def test_button_with_variant(self, variant, expected_color):
        result = vm.Button(variant=variant).build()
        assert_component_equal(
            result,
            dbc.Button(
                children=html.Span(["Click me!", None], className="button-text"),
                href="",
                target="_top",
                color=expected_color,
            ),
            keys_to_strip={"id"},
        )

    def test_button_build_with_description(self):
        """Test that description argument correctly builds icon and tooltip."""
        result = vm.Button(
            id="button",
            text="Click me",
            description=vm.Tooltip(text="Test description", icon="info", id="info"),
        ).build()

        expected_description = [
            html.Span("info", id="info-icon", className="material-symbols-outlined tooltip-icon"),
            dbc.Tooltip(
                children=dcc.Markdown("Test description", id="info-text", className="card-text"),
                id="info",
                target="info-icon",
                autohide=False,
            ),
        ]

        assert_component_equal(
            result,
            dbc.Button(
                html.Span(["Click me", *expected_description], className="button-text"),
                id="button",
                href="",
                target="_top",
                color="primary",
            ),
        )
