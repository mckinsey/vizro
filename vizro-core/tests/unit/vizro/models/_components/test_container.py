"""Unit tests for vizro.models.Container."""
import pytest
from asserts import assert_component_equal
from dash import html

try:
    from pydantic.v1 import ValidationError
except ImportError:  # pragma: no cov
    from pydantic import ValidationError

import vizro.models as vm


class TestContainerInstantiation:
    """Tests model instantiation and the validators run at that time."""

    def test_create_container_mandatory_only(self):
        container = vm.Container(title="Title", components=[vm.Button(), vm.Button()])
        assert isinstance(container.components[0], vm.Button) and isinstance(container.components[1], vm.Button)
        assert container.layout.grid == [[0], [1]]
        assert container.title == "Title"

    def test_create_container_mandatory_and_optional(self):
        container = vm.Container(
            title="Title",
            components=[vm.Button(), vm.Button()],
            id="my-id",
            layout=vm.Layout(grid=[[0, 1]]),
        )
        assert isinstance(container.components[0], vm.Button) and isinstance(container.components[1], vm.Button)
        assert container.layout.grid == [[0, 1]]
        assert container.title == "Title"
        assert container.id == "my-id"

    def test_mandatory_title_missing(self):
        with pytest.raises(ValidationError, match="field required"):
            vm.Container(components=[vm.Button()])

    def test_mandatory_components_missing(self):
        with pytest.raises(ValidationError, match="field required"):
            vm.Container(title="Title")


class TestContainerBuildMethod:
    def test_container_build(self):
        result = vm.Container(id="container", title="Title", components=[vm.Button()]).build()
        assert_component_equal(
            result, html.Div(className="page-component-container", id="container"), keys_to_strip={"children"}
        )
        assert_component_equal(
            result.children,
            [html.H3("Title"), html.Div([html.Div(vm.Button().build())])],
            # TODO: Previously I've ignored id, className and style as I had the helper function tested in
            # test_layout.py. With the new changes it seems like we shouldn't strip them now?
            # Shall we then need to duplicate for Page and Form as well?
            keys_to_strip={"id", "className", "style"},
        )
