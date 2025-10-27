"""Tests for fake Vizro models to verify custom component handling."""

from typing import Union

import pytest
from pydantic import ValidationError

from vizro.models._fake_vizro.models import Card, Dashboard, Graph, Page, VizroBaseModel


# Custom component classes for testing
class CustomPage(Page):
    """Custom page that accepts int for title instead of str."""

    title: int


class CustomPageBase(VizroBaseModel):
    """Custom page component directly subclassing VizroBaseModel."""

    title: int
    components: list[Union[Graph, Card]]


class CustomGraph(Graph):
    """Custom graph that accepts int for figure instead of str."""

    figure: int


class CustomGraphBase(VizroBaseModel):
    """Custom graph component directly subclassing VizroBaseModel."""

    figure: int


class TestFakeVizroNormalInstantiation:
    """Test normal (non-custom) component instantiation."""

    def test_python_instantiation(self):
        """Test normal Python instantiation with model objects."""
        graph = Graph(figure="test_figure")
        page = Page(title="Test Page", components=[graph])
        dashboard = Dashboard(pages=[page])
        dashboard = Dashboard.model_validate(dashboard)

        assert type(dashboard.pages[0]) is Page
        assert type(dashboard.pages[0].components[0]) is Graph

    def test_yaml_dict_instantiation(self):
        """Test normal YAML/dict instantiation."""
        graph_dict = {"figure": "test_figure", "type": "graph"}
        page_dict = {"title": "Test Page", "components": [graph_dict]}
        dashboard_dict = {"pages": [page_dict]}
        dashboard = Dashboard.model_validate(dashboard_dict)

        assert type(dashboard.pages[0]) is Page
        assert type(dashboard.pages[0].components[0]) is Graph


class TestFakeVizroCustomComponentSubclassSpecificModel:
    """Test custom components that subclass specific models (Page, Graph)."""

    def test_custom_page_in_normal_field(self):
        """Test custom component (subclass of Page) in normal field (pages)."""
        custom_page = CustomPage(title=456, components=[Graph(figure="test_figure")])
        dashboard = Dashboard(pages=[custom_page])
        dashboard = Dashboard.model_validate(dashboard)

        assert type(dashboard.pages[0]) is CustomPage

    def test_custom_graph_in_discriminated_union_field(self):
        """Test custom component (subclass of Graph) in discriminated union field (components)."""
        custom_graph = CustomGraph(figure=123)
        page = Page(title="Test Page", components=[custom_graph])
        dashboard = Dashboard(pages=[page])
        dashboard = Dashboard.model_validate(dashboard)

        assert type(dashboard.pages[0].components[0]) is CustomGraph


class TestFakeVizroCustomComponentSubclassVizroBaseModel:
    """Test custom components that directly subclass VizroBaseModel."""

    def test_custom_page_base_in_normal_field(self):
        """Test custom component (subclass of VizroBaseModel) in normal field (pages)."""
        custom_page_base = CustomPageBase(title=789, components=[Graph(figure="test_figure")])
        dashboard = Dashboard(pages=[custom_page_base])
        dashboard = Dashboard.model_validate(dashboard)

        assert type(dashboard.pages[0]) is CustomPageBase

    def test_custom_graph_base_in_discriminated_union_field(self):
        """Test custom component (subclass of VizroBaseModel) in discriminated union field (components)."""
        custom_graph_base = CustomGraphBase(figure=999)
        page = Page(title="Test Page", components=[custom_graph_base])
        dashboard = Dashboard(pages=[page])
        dashboard = Dashboard.model_validate(dashboard)

        assert type(dashboard.pages[0].components[0]) is CustomGraphBase


class TestFakeVizroYAMLWithCustomComponent:
    """Test that YAML/dict instantiation with custom components does not work."""

    def test_yaml_with_custom_component_should_fail(self):
        """Test that YAML with custom component type fails validation."""
        custom_graph_dict = {"figure": 123, "type": "custom_graph"}
        page_dict = {"title": "Test Page", "components": [custom_graph_dict]}
        dashboard_dict = {"pages": [page_dict]}

        with pytest.raises(ValidationError):
            Dashboard.model_validate(dashboard_dict)


class TestFakeVizroValidationErrors:
    """Test that invalid configurations raise validation errors."""

    @pytest.mark.xfail(reason="Known limitation: Any type in discriminated union allows wrong types to pass validation")
    def test_wrong_model_in_pages_field_python(self):
        """Test that using Graph instead of Page raises validation error in Python."""
        graph = Graph(figure="a")

        with pytest.raises(ValidationError):
            Dashboard(pages=[graph])

    def test_wrong_model_in_pages_field_yaml(self):
        """Test that using Graph instead of Page raises validation error in YAML/dict."""
        graph_dict = {"figure": "a", "type": "graph"}  # Graph is not a Page
        dashboard_dict = {"pages": [graph_dict]}

        with pytest.raises(ValidationError):
            Dashboard.model_validate(dashboard_dict)
