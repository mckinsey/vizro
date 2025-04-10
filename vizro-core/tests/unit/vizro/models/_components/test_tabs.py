"""Unit tests for vizro.models.Container."""

import dash_bootstrap_components as dbc
import pytest
from asserts import assert_component_equal
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
        with pytest.raises(ValidationError, match="Field required"):
            vm.Tabs()

    def test_minimum_tabs_length(self):
        with pytest.raises(ValidationError, match="List should have at least 1 item after validation."):
            vm.Tabs(tabs=[])

    def test_incorrect_tabs_type(self):
        with pytest.raises(ValidationError, match="Input should be a valid dictionary or instance of Container."):
            vm.Tabs(tabs=[vm.Button()])

    def test_tab_has_title(self):
        with pytest.raises(
            ValidationError, match="`Container` must have a `title` explicitly set when used inside `Tabs`."
        ):
            vm.Tabs(tabs=[vm.Container(components=[vm.Button()])])


class TestTabsBuildMethod:
    def test_tabs_build(self, containers):
        result = vm.Tabs(id="tabs-id", tabs=containers).build()
        # We want to test the component itself but not all its children
        assert_component_equal(
            result,
            dbc.Tabs(id="tabs-id", persistence=True, persistence_type="session"),
            keys_to_strip={"children"},
        )
        # We want to test the children created in the Tabs.build but not e.g. the
        # vm.Container.build() as it's tested elsewhere already
        assert_component_equal(
            result.children, [dbc.Tab(label="Title-1"), dbc.Tab(label="Title-2")], keys_to_strip={"children"}
        )
        # We still check that the html.Div for the Containers are created, but we don't need to check its content
        assert_component_equal(
            [tab.children for tab in result.children],
            [
                dbc.Container(id="container-1", class_name="", fluid=True),
                dbc.Container(id="container-2", class_name="", fluid=True),
            ],
            keys_to_strip={"children"},
        )
