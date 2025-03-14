"""Unit tests for vizro.models.Container."""

import dash_bootstrap_components as dbc
import pytest
from asserts import STRIP_ALL, assert_component_equal
from dash import html
from pydantic import ValidationError

import vizro.models as vm


class TestContainerInstantiation:
    """Tests model instantiation and the validators run at that time."""

    def test_create_container_mandatory_only(self):
        container = vm.Container(title="Title", components=[vm.Button(), vm.Button()])
        assert isinstance(container.components[0], vm.Button) and isinstance(container.components[1], vm.Button)
        assert container.layout.grid == [[0], [1]]
        assert container.title == "Title"
        assert container.variant == "plain"

    @pytest.mark.parametrize("variant", ["plain", "filled", "outlined"])
    def test_create_container_mandatory_and_optional(self, variant):
        container = vm.Container(
            id="my-id",
            title="Title",
            components=[vm.Button(), vm.Button()],
            layout=vm.Layout(grid=[[0, 1]]),
            variant=variant,
        )
        assert container.id == "my-id"
        assert isinstance(container.components[0], vm.Button) and isinstance(container.components[1], vm.Button)
        assert container.layout.grid == [[0, 1]]
        assert container.title == "Title"
        assert container.variant == variant

    def test_mandatory_title_missing(self):
        with pytest.raises(ValidationError, match="Field required"):
            vm.Container(components=[vm.Button()])

    def test_mandatory_components_missing(self):
        with pytest.raises(ValidationError, match="Field required"):
            vm.Container(title="Title")

    def test_invalid_variant(self):
        with pytest.raises(ValidationError, match="Input should be 'plain', 'filled' or 'outlined'."):
            vm.Container(title="Title", components=[vm.Button()], variant="test")


class TestContainerBuildMethod:
    def test_container_build(self):
        result = vm.Container(
            id="container", title="Title", components=[vm.Button()], layout=vm.Layout(id="layout_id", grid=[[0]])
        ).build()
        assert_component_equal(
            result, dbc.Container(id="container", class_name="", fluid=True), keys_to_strip={"children"}
        )
        assert_component_equal(result.children, [html.H3(), html.Div()], keys_to_strip=STRIP_ALL)
        # We still want to test the exact H3 produced in Container.build:
        assert_component_equal(result.children[0], html.H3("Title", className="container-title", id="container_title"))
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
