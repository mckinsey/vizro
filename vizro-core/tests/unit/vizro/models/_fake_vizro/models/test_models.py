"""Tests for fake Vizro models to verify custom component handling."""

from typing import Union

import pytest
from pydantic import ValidationError

from vizro.models._fake_vizro.models import Action, Card, Dashboard, Graph, Page, VizroBaseModel

# Custom component classes for testing


######## Page ############
class CustomPage(Page):
    """Custom page that accepts int for title instead of str."""

    type: str = "custom_component"
    title: int


class CustomPageBase(VizroBaseModel):
    """Custom page component directly subclassing VizroBaseModel."""

    type: str = "custom_component"
    title: int
    components: list[Union[Graph, Card]]


######### Graph ############
class CustomGraph(Graph):
    """Custom graph that accepts int for figure instead of str."""

    type: str = "custom_component"
    figure: int


class CustomGraph2(Graph):
    """Custom graph that accepts int for figure instead of str."""

    type: str = "custom_component"
    figure: int


class CustomGraphNoType(Graph):
    """Custom graph that accepts int for figure instead of str."""

    figure: int


class CustomGraphBase(VizroBaseModel):
    """Custom graph component directly subclassing VizroBaseModel."""

    type: str = "custom_component"
    figure: int


class CustomGraphBaseNoType(VizroBaseModel):
    """Custom graph component directly subclassing VizroBaseModel but without type."""

    figure: int


# Tests
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

    def test_custom_graph_no_type_in_discriminated_union_field(self):
        """Test custom component (subclass of Graph) in discriminated union field (components) without type."""
        custom_graph_no_type = CustomGraphNoType(figure=999)
        # If user does not specify type EVEN ON INHERITANCE, then it will fail, as model will take class name as type
        # which doesn't fit
        with pytest.raises(ValidationError, match="Input tag 'custom_graph_no_type' found"):
            Page(title="Test Page", components=[custom_graph_no_type])

    def test_multiple_custom_components_in_discriminated_union_field(self):
        """Test multiple custom components in discriminated union field (components)."""
        custom_graph_1 = CustomGraph(figure=123)
        custom_graph_2 = CustomGraph2(figure=456)
        page = Page(title="Test Page", components=[custom_graph_1, custom_graph_2])
        dashboard = Dashboard(pages=[page])
        dashboard = Dashboard.model_validate(dashboard)

        assert type(dashboard.pages[0].components[0]) is CustomGraph
        assert type(dashboard.pages[0].components[1]) is CustomGraph2


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

    def test_custom_graph_base_no_type_in_discriminated_union_field(self):
        """Test custom component (subclass of VizroBaseModel) in discriminated union field (components) without type."""
        custom_graph_base_no_type = CustomGraphBaseNoType(figure=999)
        # If user does not specify type, then it will fail, as model take class name as type which doesn't fit
        with pytest.raises(ValidationError, match="Input tag 'custom_graph_base_no_type' found"):
            Page(title="Test Page", components=[custom_graph_base_no_type])


# What is still missing
# Multiple custom components


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


class TestFakeVizroLiteralType:
    """Test understanding of Literal errors."""

    def test_literal_type_builtin_model(self):
        """Test understanding of Literal errors."""
        graph = Graph(figure="a")
        assert graph.type == "graph"
        with pytest.raises(ValidationError):
            Graph(figure="a", type="custom_component")

    def test_literal_type_custom_model(self):
        """Test understanding of Literal errors for custom models."""
        custom_graph = CustomGraph(figure=3, type="custom_component")
        assert custom_graph.type == "custom_component"

        with pytest.raises(ValidationError):
            CustomGraph(figure=3, type="graph")

    def test_literal_type_custom_model_no_type(self):
        """Test understanding of Literal errors for custom models without type."""
        custom_graph_no_type = CustomGraphNoType(figure=3)
        assert custom_graph_no_type.type == "custom_graph_no_type"
        with pytest.raises(ValidationError):
            CustomGraphNoType(figure=3, type="graph")

    def test_literal_type_custom_model_base(self):
        """Test understanding of Literal errors for custom model bases."""
        custom_graph_base = CustomGraphBase(figure=3)
        assert custom_graph_base.type == "custom_component"
        with pytest.raises(ValidationError):
            CustomGraphBase(figure=3, type="graph")

    def test_literal_type_custom_model_base_no_type(self):
        """Test understanding of Literal errors for custom model bases without type."""
        custom_graph_base_no_type = CustomGraphBaseNoType(figure=3)
        assert custom_graph_base_no_type.type == "custom_graph_base_no_type"
        with pytest.raises(ValidationError):
            CustomGraphBaseNoType(figure=3, type="graph")

        with pytest.raises(ValidationError):
            CustomGraphBaseNoType(figure=3, type="custom_component")


@pytest.fixture
def dashboard_with_graph_and_action():
    """Fixture for a dashboard with a graph and an action."""
    return Dashboard(pages=[Page(title="Test Page", components=[Graph(figure="a", actions=[Action(action="a")])])])


class TestTreeCreation:
    """Test tree creation."""

    def test_tree_creation_not_triggered(self, dashboard_with_graph_and_action):
        """Test tree creation is not triggered."""
        dashboard = Dashboard.model_validate(dashboard_with_graph_and_action)
        assert dashboard._tree is None

    def test_tree_creation_triggered(self, dashboard_with_graph_and_action):
        """Test tree creation is triggered."""
        dashboard = Dashboard.model_validate(dashboard_with_graph_and_action, context={"build_tree": True})
        assert dashboard._tree is not None

        # 0. Check trees are the same everywhere
        assert dashboard._tree is dashboard.pages[0]._tree

        # 1. Check root exists and has correct structure
        assert dashboard._tree.name == "Root"

        # 2. Check node count matches expected hierarchy
        # Dashboard -> Page -> Graph -> Action = 4 nodes total
        assert len(dashboard._tree) == 4

        # 3. Check tree depth
        assert dashboard._tree.calc_height() == 4  # Root -> Dashboard -> Page -> Graph -> Action

        # 4. Verify  node kinds are correct (field names)
        assert dashboard._tree[dashboard.pages[0].id].kind == "pages"
        assert dashboard._tree[dashboard.pages[0].components[0].id].kind == "components"
        assert dashboard._tree[dashboard.pages[0].components[0].actions[0].id].kind == "actions"

        # 5. Verify tree navigation works
        assert next(iter(dashboard._tree.children)).data == dashboard

        # 6. Check all nodes have valid data (not SimpleNamespace placeholders)
        for node in dashboard._tree:
            if node is not dashboard._tree:  # Skip the root tree node itself
                assert isinstance(node.data, VizroBaseModel)
                assert hasattr(node.data, "id")
