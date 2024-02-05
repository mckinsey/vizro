"""Unit tests for vizro.models.Container."""

import dash_mantine_components as dmc
import pytest
from asserts import assert_component_equal
from dash import html

try:
    from pydantic.v1 import ValidationError
except ImportError:  # pragma: no cov
    from pydantic import ValidationError

import vizro.models as vm


@pytest.fixture
def containers():
    return [
        vm.Container(id="container-1", title="Title-1", components=[vm.Button()]),
        vm.Container(id="container-2", title="Title-2", components=[vm.Button()]),
    ]


class TestTabsInstantiation:
    """Tests model instantiation and the validators run at that time."""

    def test_create_tabs_mandatory_only(self, containers):
        tabs = vm.Tabs(id="tabs-id", tabs=containers)
        assert all(isinstance(tab, vm.Container) for tab in tabs.tabs) and len(tabs.tabs) == 2
        assert tabs.id == "tabs-id"
        assert tabs.type == "tabs"

    def test_mandatory_tabs_missing(self):
        with pytest.raises(ValidationError, match="field required"):
            vm.Tabs(id="tabs-id")


class TestTabsBuildMethod:
    def test_tabs_build(self, containers):
        result = vm.Tabs(id="tabs-id", tabs=containers).build()
        # We want to test the component itself but not all its children
        assert_component_equal(
            result,
            dmc.Tabs(id="tabs-id", value="container-1", persistence=True, persistence_type="session", className="tabs"),
            keys_to_strip={"children"},
        )
        # We want to test the children created in the Tabs.build but not e.g. the
        # vm.Container.build() as it's tested elsewhere already
        assert_component_equal(
            result.children,
            [dmc.TabsList(), dmc.TabsPanel(value="container-1"), dmc.TabsPanel(value="container-2")],
            keys_to_strip={"children", "className"},
        )
        # So we go down the tree and ignore the children selectively
        assert_component_equal(
            result.children[0],
            dmc.TabsList(
                children=[
                    dmc.Tab(value="container-1", children="Title-1", className="tab__title"),
                    dmc.Tab(value="container-2", children="Title-2", className="tab__title"),
                ],
                className="tabs__list",
            ),
        )
        # This one removes the need for duplication of tests as the output is similar
        assert_component_equal(
            result.children[1:],
            [
                dmc.TabsPanel(className="tabs__panel", value="container-1"),
                dmc.TabsPanel(className="tabs__panel", value="container-2"),
            ],
            keys_to_strip={"children"},
        )
        # We still check that the html.Div for the Containers are created, but we don't need to check its content
        assert_component_equal(
            [tab.children.children for tab in result.children[1:]],
            [
                [html.Div(id="container-1", className="page-component-container")],
                [html.Div(id="container-2", className="page-component-container")],
            ],
            keys_to_strip={"children"},
        )
