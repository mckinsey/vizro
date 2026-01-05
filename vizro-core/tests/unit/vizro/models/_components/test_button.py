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
        assert button.icon == ""
        assert button.href == ""
        assert button.actions == []
        assert button.variant == "filled"
        assert button.description is None
        assert button._action_triggers == {"__default__": f"{button.id}.n_clicks"}
        assert button._action_outputs == {
            "__default__": f"{button.id}.n_clicks",
            "text": f"{button.id}.children",
        }
        assert button._action_inputs == {"__default__": f"{button.id}.n_clicks"}

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
        button = vm.Button(
            id="button-id",
            text=text,
            href=href,
            variant=variant,
            description=vm.Tooltip(id="tooltip_id", text="Test Tooltip", icon="info"),
        )

        assert button.id == "button-id"
        assert button.type == "button"
        assert button.text == str(text)
        assert button.icon == ""
        assert button.href == href
        assert button.actions == []
        assert button.variant == variant
        assert isinstance(button.description, vm.Tooltip)

        assert button._action_triggers == {"__default__": "button-id.n_clicks"}
        assert button._action_outputs == {
            "__default__": "button-id.n_clicks",
            "text": "button-id.children",
            "description": "tooltip_id-text.children",
        }
        assert button._action_inputs == {"__default__": "button-id.n_clicks"}

    def test_button_trigger(self):
        button = vm.Button(id="button-id", actions=[export_data()])
        [action] = button.actions
        assert action._trigger == "button-id.n_clicks"

    def test_invalid_variant(self):
        with pytest.raises(ValidationError, match=r"Input should be 'plain', 'filled' or 'outlined'."):
            vm.Button(variant="test")

    def test_invalid_text(self):
        with pytest.raises(ValueError, match=r"You must provide either the `text` or `icon` argument."):
            vm.Button(text="")

    def test_invalid_href_and_actions(self):
        with pytest.raises(ValueError, match=r"Button cannot have both `href` and `actions` defined."):
            vm.Button(href="/page_1_reference", actions=[export_data()])


class TestBuildMethod:
    def test_button_build(self):
        result = vm.Button(id="button", text="Click me!").build()
        expected_text = html.Span("Click me!", className="btn-text")
        assert_component_equal(
            result,
            dbc.Button(
                children=[None, expected_text, None],
                id="button",
                href="",
                target="_top",
                color="primary",
                class_name="",
            ),
        )

    def test_button_build_with_extra(self):
        """Test that extra arguments correctly override defaults."""
        result = vm.Button(id="button", extra={"color": "success", "outline": True, "href": "www.google.com"}).build()
        expected_text = html.Span("Click me!", className="btn-text")
        assert_component_equal(
            result,
            dbc.Button(
                children=[None, expected_text, None],
                id="button",
                color="success",
                outline=True,
                href="www.google.com",
                target="_top",
                class_name="",
            ),
        )

    def test_button_build_with_href(self):
        button = vm.Button(id="button_id", text="My text!", href="www.google.com").build()
        expected_text = html.Span("My text!", className="btn-text")

        assert_component_equal(
            button,
            dbc.Button(
                id="button_id",
                children=[None, expected_text, None],
                href="www.google.com",
                target="_top",
                color="primary",
                class_name="",
            ),
            keys_to_strip={"id"},
        )

    @pytest.mark.parametrize(
        "variant, expected_color",
        [("plain", "link"), ("filled", "primary"), ("outlined", "secondary")],
    )
    def test_button_with_variant(self, variant, expected_color):
        result = vm.Button(variant=variant).build()
        expected_text = html.Span("Click me!", className="btn-text")

        assert_component_equal(
            result,
            dbc.Button(
                children=[None, expected_text, None],
                href="",
                target="_top",
                color=expected_color,
                class_name="",
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

        expected_text = html.Span("Click me", className="btn-text")
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
                children=[None, expected_text, *expected_description],
                id="button",
                href="",
                target="_top",
                color="primary",
                class_name="",
            ),
        )

    @pytest.mark.parametrize(
        "icon, text, class_name",
        [("home", "Test", ""), ("home", "", "btn-circular")],
    )
    def test_button_build_with_icon(self, icon, text, class_name):
        button = vm.Button(id="button_id", icon=icon, text=text).build()

        expected_icon = html.Span(f"{icon}", id="button_id-icon", className="material-symbols-outlined tooltip-icon")
        expected_text = html.Span(text, className="btn-text") if text else None
        assert_component_equal(
            button,
            dbc.Button(
                id="button_id",
                children=[expected_icon, expected_text, None],
                target="_top",
                href="",
                color="primary",
                class_name=class_name,
            ),
        )

    def test_button_build_description_with_icon_no_text(self):
        """Test that description argument correctly builds the tooltip and targets the button icon when text=''."""
        button = vm.Button(
            id="button_id",
            icon="home",
            text="",
            description=vm.Tooltip(text="Test description", icon="info", id="info"),
        ).build()

        expected_icon = html.Span("home", id="button_id-icon", className="material-symbols-outlined tooltip-icon")
        expected_description = [
            dbc.Tooltip(
                children=dcc.Markdown("Test description", id="info-text", className="card-text"),
                id="info",
                target="button_id-icon",
                autohide=False,
            ),
        ]

        assert_component_equal(
            button,
            dbc.Button(
                id="button_id",
                children=[expected_icon, None, *expected_description],
                target="_top",
                href="",
                color="primary",
                class_name="btn-circular",
            ),
        )
