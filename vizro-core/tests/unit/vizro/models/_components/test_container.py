"""Unit tests for vizro.models.Container."""

import dash_bootstrap_components as dbc
import pytest
from asserts import STRIP_ALL, assert_component_equal
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
            id="my-id", title="Title", components=[vm.Button(), vm.Button()], layout=vm.Layout(grid=[[0, 1]])
        )
        assert container.id == "my-id"
        assert isinstance(container.components[0], vm.Button) and isinstance(container.components[1], vm.Button)
        assert container.layout.grid == [[0, 1]]
        assert container.title == "Title"

    def test_mandatory_title_missing(self):
        with pytest.raises(ValidationError, match="field required"):
            vm.Container(components=[vm.Button()])

    def test_mandatory_components_missing(self):
        with pytest.raises(ValidationError, match="field required"):
            vm.Container(title="Title")


class TestContainerBuildMethod:
    def test_container_build(self):
        result = vm.Container(
            id="container", title="Title", components=[vm.Button()], layout=vm.Layout(id="layout_id", grid=[[0]])
        ).build()
        assert_component_equal(
            result, html.Div(id="container", className="page-component-container"), keys_to_strip={"children"}
        )
        assert_component_equal(result.children, [html.H3(), html.Div()], keys_to_strip=STRIP_ALL)
        # We still want to test the exact H3 produced in Container.build:
        assert_component_equal(result.children[0], html.H3("Title", className="container__title"))
        # And also that a button has been inserted in the right place:
        assert_component_equal(result["layout_id_0"].children, dbc.Button(), keys_to_strip=STRIP_ALL)
