"""Unit tests for vizro.models.ControlGroup."""

import dash_bootstrap_components as dbc
import pytest
import vizro_dash_components as vdc
from asserts import assert_component_equal
from dash import html
from pydantic import ValidationError

import vizro.models as vm


class TestControlGroupInstantiation:
    """Tests model instantiation and the validators run at that time."""

    def test_create_control_group_mandatory_only(self):
        control_group = vm.ControlGroup(controls=[vm.Filter(column="species")])
        assert len(control_group.controls) == 1
        assert isinstance(control_group.controls[0], vm.Filter)
        assert control_group.type == "control_group"
        assert control_group.title == ""
        assert control_group.description is None
        assert control_group._action_outputs == {}

    def test_create_control_group_mandatory_and_optional(self):
        control_group = vm.ControlGroup(
            id="control-group-id",
            title="Filters",
            description=vm.Tooltip(id="tooltip-id", text="Test description", icon="info"),
            controls=[
                vm.Filter(column="species", selector=vm.Dropdown(options=["a", "b"])),
            ],
        )
        assert control_group.id == "control-group-id"
        assert len(control_group.controls) == 1
        assert isinstance(control_group.controls[0], vm.Filter)
        assert control_group.title == "Filters"
        assert isinstance(control_group.description, vm.Tooltip)
        assert control_group._action_outputs == {
            "title": "control-group-id_title.children",
            "description": "tooltip-id-text.children",
        }

    def test_controls_required_missing(self):
        with pytest.raises(ValidationError, match="Field required"):
            vm.ControlGroup()

    def test_controls_min_length(self):
        with pytest.raises(ValidationError, match=r"List should have at least 1 item"):
            vm.ControlGroup(controls=[])


class TestControlGroupBuildMethod:
    """Tests build method."""

    def test_control_group_build_without_title(self):
        control_group = vm.ControlGroup(
            id="control-group",
            controls=[vm.Filter(column="species", selector=vm.Dropdown(options=["a", "b"]))],
        )
        result = control_group.build()
        assert_component_equal(
            result,
            dbc.Container(id="control-group", fluid=True, className="control-group-panel"),
            keys_to_strip={"children"},
        )

        assert result.children[0] is None
        assert_component_equal(
            result.children[1],
            html.Div(id="control-group-control-panel", className="control-group"),
            keys_to_strip={"children", "hidden"},
        )

    def test_control_group_build_with_title(self):
        result = vm.ControlGroup(
            id="control-group",
            title="Filters",
            controls=[
                vm.Filter(
                    column="species",
                    selector=vm.RadioItems(id="radio-items-id", options=["A", "B", "C"], value="A"),
                    visible=True,
                )
            ],
        ).build()

        assert_component_equal(
            result,
            dbc.Container(id="control-group", fluid=True, className="control-group-panel"),
            keys_to_strip={"children"},
        )

        assert_component_equal(
            result.children[0],
            html.H3(
                [html.Div([html.Span("Filters", id="control-group_title"), None], className="inner-container-title")],
                className="control-group-title",
                id="control-group_title_content",
            ),
        )
        assert_component_equal(
            result.children[1],
            html.Div(id="control-group-control-panel", className="control-group"),
            keys_to_strip={"children", "hidden"},
        )

    def test_control_group_build_with_extra(self):
        result = vm.ControlGroup(
            id="control-group",
            title="Filters",
            controls=[
                vm.Filter(
                    column="species",
                    selector=vm.RadioItems(id="radio-items-id", options=["A", "B", "C"], value="A"),
                    visible=True,
                )
            ],
            extra={"fluid": False, "className": "custom-class"},
        ).build()
        assert_component_equal(
            result,
            dbc.Container(id="control-group", fluid=False, className="custom-class"),
            keys_to_strip={"children"},
        )

    def test_control_group_build_with_description(self):
        control_group = vm.ControlGroup(
            id="control-group",
            title="Filters",
            description=vm.Tooltip(text="Tooltip text", icon="Info", id="info"),
            controls=[vm.Filter(column="x", selector=vm.Dropdown())],
        )
        result = control_group.build()
        expected_description = [
            html.Span("info", id="info-icon", className="material-symbols-outlined tooltip-icon"),
            dbc.Tooltip(
                children=vdc.Markdown("Tooltip text", id="info-text", className="card-text"),
                id="info",
                target="info-icon",
                autohide=False,
            ),
        ]
        assert_component_equal(
            result["control-group_title_content"],
            html.H3(
                [
                    html.Div(
                        [html.Span("Filters", id="control-group_title"), *expected_description],
                        className="inner-container-title",
                    )
                ],
                className="control-group-title",
                id="control-group_title_content",
            ),
        )
