"""Unit tests for vizro.models.Container."""

import dash_bootstrap_components as dbc
import pytest
from asserts import STRIP_ALL, assert_component_equal
from dash import dcc, html
from pydantic import ValidationError

import vizro.models as vm


class TestContainerInstantiation:
    """Tests model instantiation and the validators run at that time."""

    def test_create_container_mandatory_only(self):
        container = vm.Container(components=[vm.Button(), vm.Button()])
        assert isinstance(container.components[0], vm.Button) and isinstance(container.components[1], vm.Button)
        assert container.layout.grid == [[0], [1]]
        assert container.title == ""
        assert container.variant == "plain"
        assert container._action_outputs == {}

    @pytest.mark.parametrize("variant", ["plain", "filled", "outlined"])
    def test_create_container_mandatory_and_optional(self, variant):
        container = vm.Container(
            id="my-id",
            title="Title",
            description="Test description",
            components=[vm.Button(), vm.Button()],
            layout=vm.Grid(grid=[[0, 1]]),
            variant=variant,
            collapsed=True,
            controls=[vm.Filter(column="test")],
        )
        assert container.id == "my-id"
        assert isinstance(container.components[0], vm.Button) and isinstance(container.components[1], vm.Button)
        assert container.layout.grid == [[0, 1]]
        assert container.title == "Title"
        assert container.variant == variant
        assert container.collapsed is True
        assert isinstance(container.controls[0], vm.Filter)
        assert container._action_outputs == {
            "title": f"{container.id}_title.children",
            "description": f"{container.description.id}-text.children",
        }

    def test_create_container_mandatory_and_optional_legacy_layout(self):
        with pytest.warns(FutureWarning, match="The `Layout` model has been renamed `Grid`"):
            container = vm.Container(
                id="my-id",
                title="Title",
                components=[vm.Button(), vm.Button()],
                layout=vm.Layout(grid=[[0, 1]]),
            )
        assert container.id == "my-id"
        assert isinstance(container.components[0], vm.Button) and isinstance(container.components[1], vm.Button)
        assert container.layout.grid == [[0, 1]]
        assert container.title == "Title"

    def test_mandatory_components_missing(self):
        with pytest.raises(ValidationError, match="Field required"):
            vm.Container(title="Title")

    def test_invalid_variant(self):
        with pytest.raises(ValidationError, match="Input should be 'plain', 'filled' or 'outlined'."):
            vm.Container(title="Title", components=[vm.Button()], variant="test")

    def test_invalid_collapsed(self):
        with pytest.raises(
            ValidationError, match="`Container` must have a `title` explicitly set when `collapsed` is not None."
        ):
            vm.Container(components=[vm.Button()], collapsed=True)


class TestContainerBuildMethod:
    def test_container_build_without_title(self):
        result = vm.Container(
            id="container", components=[vm.Button()], layout=vm.Grid(id="layout_id", grid=[[0]])
        ).build()
        assert_component_equal(
            result, dbc.Container(id="container", class_name="", fluid=True), keys_to_strip={"children"}
        )
        assert_component_equal(result.children, [None, None, html.Div()], keys_to_strip=STRIP_ALL)

    def test_container_build_with_title(self):
        result = vm.Container(
            id="container", title="Title", components=[vm.Button()], layout=vm.Grid(id="layout_id", grid=[[0]])
        ).build()
        assert_component_equal(
            result, dbc.Container(id="container", class_name="", fluid=True), keys_to_strip={"children"}
        )
        assert_component_equal(result.children, [html.H3(), None, html.Div()], keys_to_strip=STRIP_ALL)
        # We still want to test the exact H3 produced in Container.build:
        assert_component_equal(
            result.children[0],
            html.H3(
                [html.Div([html.Span("Title", id="container_title"), None], className="inner-container-title")],
                className="container-title",
                id="container_title_content",
            ),
        )

    def test_container_build_legacy_layout(self):
        with pytest.warns(FutureWarning, match="The `Layout` model has been renamed `Grid`"):
            result = vm.Container(
                id="container", title="Title", components=[vm.Button()], layout=vm.Layout(id="layout_id", grid=[[0]])
            ).build()
        assert_component_equal(
            result, dbc.Container(id="container", class_name="", fluid=True), keys_to_strip={"children"}
        )
        assert_component_equal(result.children, [html.H3(), None, html.Div()], keys_to_strip=STRIP_ALL)
        # We still want to test the exact H3 produced in Container.build:
        assert_component_equal(
            result.children[0],
            html.H3(
                [html.Div([html.Span("Title", id="container_title"), None], className="inner-container-title")],
                className="container-title",
                id="container_title_content",
            ),
        )
        # And also that a button has been inserted in the right place:
        assert_component_equal(result["layout_id_0"].children, dbc.Button(), keys_to_strip=STRIP_ALL)

    def test_container_build_with_extra(self):
        """Test that extra arguments correctly override defaults."""
        result = vm.Container(
            id="container",
            title="Title",
            components=[vm.Button()],
            extra={"fluid": False, "class_name": "bg-container"},
        ).build()
        assert_component_equal(
            result, dbc.Container(id="container", fluid=False, class_name="bg-container"), keys_to_strip={"children"}
        )

    @pytest.mark.parametrize(
        "variant, expected_classname", [("plain", ""), ("filled", "bg-container p-3"), ("outlined", "border p-3")]
    )
    def test_container_with_variant(self, variant, expected_classname):
        result = vm.Container(title="Title", components=[vm.Button()], variant=variant).build()
        assert_component_equal(
            result, dbc.Container(class_name=expected_classname, fluid=True), keys_to_strip={"children", "id"}
        )

    @pytest.mark.parametrize(
        "collapsed",
        [True],
    )
    def test_container_with_collapse(self, collapsed):
        container = vm.Container(title="Title", components=[vm.Button()], collapsed=collapsed, id="container")
        assert container.variant == "outlined"

        result = container.build()
        assert_component_equal(result.children, [html.H3(), None, dbc.Collapse()], keys_to_strip=STRIP_ALL)

        # We still want to test the exact H3 and dbc.Collapse inside the result
        expected_title_content = [
            html.Div([html.Span("Title", id="container_title"), None], className="inner-container-title"),
            html.Span(
                "keyboard_arrow_down" if collapsed else "keyboard_arrow_up",
                className="material-symbols-outlined",
                id="container_icon",
            ),
            dbc.Tooltip(
                id="container_tooltip",
                children="Show Content" if collapsed else "Hide Content",
                target="container_icon",
            ),
        ]

        assert_component_equal(
            result.children[0],
            html.H3(expected_title_content, className="container-title-collapse", id="container_title_content"),
        )
        assert_component_equal(
            result.children[2],
            dbc.Collapse(
                id="container_collapse", is_open=not collapsed, className="collapsible-container", key="container"
            ),
            keys_to_strip={"children"},
        )
        # We want to test if the correct style is applied: default style for collapsible containers is outlined
        assert result.class_name == "border p-3"

    def test_container_build_with_description(self):
        result = vm.Container(
            id="container",
            title="Title",
            components=[vm.Button()],
            layout=vm.Grid(id="layout_id", grid=[[0]]),
            description=vm.Tooltip(text="Tooltip test", icon="info", id="info"),
        ).build()

        expected_description = [
            html.Span("info", id="info-icon", className="material-symbols-outlined tooltip-icon"),
            dbc.Tooltip(
                children=dcc.Markdown("Tooltip test", id="info-text", className="card-text"),
                id="info",
                target="info-icon",
                autohide=False,
            ),
        ]

        assert_component_equal(
            result, dbc.Container(id="container", class_name="", fluid=True), keys_to_strip={"children"}
        )
        assert_component_equal(result.children, [html.H3(), None, html.Div()], keys_to_strip=STRIP_ALL)
        # We still want to test the exact H3 produced in Container.build:
        assert_component_equal(
            result["container_title_content"],
            html.H3(
                [
                    html.Div(
                        [html.Span("Title", id="container_title"), *expected_description],
                        className="inner-container-title",
                    )
                ],
                className="container-title",
                id="container_title_content",
            ),
        )

    def test_container_build_with_controls(self):
        result = vm.Container(
            id="container",
            components=[vm.Button()],
            controls=[vm.Filter(column="species", selector=vm.Dropdown(id="dropdown-id"))],
        ).build()
        assert_component_equal(
            result, dbc.Container(id="container", class_name="", fluid=True), keys_to_strip={"children"}
        )
        assert_component_equal(
            result["container-control-panel"],
            html.Div(
                id="container-control-panel",
                className="container-controls-panel",
            ),
            keys_to_strip={"children"},
        )
        assert_component_equal(result["dropdown-id"], dcc.Dropdown(), keys_to_strip=STRIP_ALL)
