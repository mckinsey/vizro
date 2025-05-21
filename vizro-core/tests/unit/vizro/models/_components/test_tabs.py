"""Unit tests for vizro.models.Container."""

import dash_bootstrap_components as dbc
import pytest
from asserts import assert_component_equal
from dash import dcc, html
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
        assert tabs.title == ""
        assert tabs._action_outputs == {}

    def test_create_tabs_mandatory_and_optionsl(self, containers):
        tabs = vm.Tabs(id="tabs-id", title="Title", description="Test description", tabs=containers)

        assert all(isinstance(tab, vm.Container) for tab in tabs.tabs) and len(tabs.tabs) == 2
        assert tabs.id == "tabs-id"
        assert tabs.type == "tabs"
        assert tabs.title == "Title"
        assert isinstance(tabs.description, vm.Tooltip)
        assert tabs._action_outputs == {
            "title": f"{tabs.id}_title.children",
            "description": f"{tabs.description.id}-text.children",
        }

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
        result = vm.Tabs(id="tabs-id", title="Tabs Title", tabs=containers).build()

        # Test the outermost part first and then go down into deeper levels
        assert_component_equal(result, html.Div(className="tabs-container"), keys_to_strip={"children"})
        assert_component_equal(
            result.children,
            [
                html.H3(className="inner-tabs-title"),
                dbc.Tabs(id="tabs-id", persistence=True, persistence_type="session"),
            ],
            keys_to_strip={"children"},
        )

        # Test title and description
        assert_component_equal(result.children[0].children, [html.Span("Tabs Title", id="tabs-id_title"), None])

        # We want to test the children created in the Tabs.build but not e.g. the
        # vm.Container.build() as it's tested elsewhere already
        assert_component_equal(
            result["tabs-id"].children, [dbc.Tab(label="Title-1"), dbc.Tab(label="Title-2")], keys_to_strip={"children"}
        )
        # We still check that the html.Div for the Containers are created, but we don't need to check its content
        assert_component_equal(
            [tab.children for tab in result["tabs-id"].children],
            [
                dbc.Container(id="container-1", class_name="", fluid=True),
                dbc.Container(id="container-2", class_name="", fluid=True),
            ],
            keys_to_strip={"children"},
        )

    def test_tabs_build_with_description(self, containers):
        result = vm.Tabs(
            id="tabs-id",
            title="Tabs Title",
            description=vm.Tooltip(text="Tooltip test", icon="info", id="info"),
            tabs=containers,
        ).build()

        # Test the outermost part first and then go down into deeper levels
        assert_component_equal(result, html.Div(className="tabs-container"), keys_to_strip={"children"})
        assert_component_equal(
            result.children,
            [
                html.H3(className="inner-tabs-title"),
                dbc.Tabs(id="tabs-id", persistence=True, persistence_type="session"),
            ],
            keys_to_strip={"children"},
        )

        # Test title and description
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
            result.children[0].children, [html.Span("Tabs Title", id="tabs-id_title"), *expected_description]
        )

        # We want to test the children created in the Tabs.build but not e.g. the
        # vm.Container.build() as it's tested elsewhere already
        assert_component_equal(
            result["tabs-id"].children, [dbc.Tab(label="Title-1"), dbc.Tab(label="Title-2")], keys_to_strip={"children"}
        )
        # We still check that the html.Div for the Containers are created, but we don't need to check its content
        assert_component_equal(
            [tab.children for tab in result["tabs-id"].children],
            [
                dbc.Container(id="container-1", class_name="", fluid=True),
                dbc.Container(id="container-2", class_name="", fluid=True),
            ],
            keys_to_strip={"children"},
        )
