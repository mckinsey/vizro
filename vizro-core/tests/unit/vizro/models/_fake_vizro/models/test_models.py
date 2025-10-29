"""Tests for fake Vizro models to verify custom component handling."""

from typing import Union

import pytest
from pydantic import ValidationError

from vizro.models._fake_vizro.models import Action, Card, Component, Dashboard, Graph, Page, VizroBaseModel

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
        graph = Graph(figure="test_figure", actions=[Action(action="a")])
        page = Page(title="Test Page", components=[graph])
        dashboard = Dashboard(pages=[page])
        dashboard = Dashboard.model_validate(dashboard)

        assert type(dashboard.pages[0]) is Page
        assert type(dashboard.pages[0].components[0]) is Graph

    def test_yaml_dict_instantiation(self):
        """Test normal YAML/dict instantiation."""
        graph_dict = {"figure": "test_figure", "type": "graph", "actions": [{"action": "a"}]}
        page_dict = {"title": "Test Page", "components": [graph_dict]}
        dashboard_dict = {"pages": [page_dict]}
        dashboard = Dashboard.model_validate(dashboard_dict)

        assert type(dashboard.pages[0]) is Page
        assert type(dashboard.pages[0].components[0]) is Graph


class TestFakeVizroCustomComponentSubclassSpecificModel:
    """Test custom components that subclass specific models (Page, Graph)."""

    def test_custom_page_in_normal_field(self):
        """Test custom component (subclass of Page) in normal field (pages)."""
        custom_page = CustomPage(title=456, components=[Graph(figure="test_figure", actions=[Action(action="a")])])
        dashboard = Dashboard(pages=[custom_page])
        dashboard = Dashboard.model_validate(dashboard)

        assert type(dashboard.pages[0]) is CustomPage

    def test_custom_graph_in_discriminated_union_field(self):
        """Test custom component (subclass of Graph) in discriminated union field (components)."""
        custom_graph = CustomGraph(figure=123, actions=[Action(action="a")])
        page = Page(title="Test Page", components=[custom_graph])
        dashboard = Dashboard(pages=[page])
        dashboard = Dashboard.model_validate(dashboard)

        assert type(dashboard.pages[0].components[0]) is CustomGraph

    def test_custom_graph_no_type_in_discriminated_union_field(self):
        """Test custom component (subclass of Graph) in discriminated union field (components) without type."""
        custom_graph_no_type = CustomGraphNoType(figure=999, actions=[Action(action="a")])
        # If user does not specify type EVEN ON INHERITANCE, then it will fail, as model will take class name as type
        # which doesn't fit
        with pytest.raises(ValidationError, match="Input tag 'custom_graph_no_type' found"):
            Page(title="Test Page", components=[custom_graph_no_type])

    def test_multiple_custom_components_in_discriminated_union_field(self):
        """Test multiple custom components in discriminated union field (components)."""
        custom_graph_1 = CustomGraph(figure=123, actions=[Action(action="a")])
        custom_graph_2 = CustomGraph2(figure=456, actions=[Action(action="a")])
        page = Page(title="Test Page", components=[custom_graph_1, custom_graph_2])
        dashboard = Dashboard(pages=[page])
        dashboard = Dashboard.model_validate(dashboard)

        assert type(dashboard.pages[0].components[0]) is CustomGraph
        assert type(dashboard.pages[0].components[1]) is CustomGraph2


class TestFakeVizroCustomComponentSubclassVizroBaseModel:
    """Test custom components that directly subclass VizroBaseModel."""

    def test_custom_page_base_in_normal_field(self):
        """Test custom component (subclass of VizroBaseModel) in normal field (pages)."""
        custom_page_base = CustomPageBase(
            title=789, components=[Graph(figure="test_figure", actions=[Action(action="a")])]
        )
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
        graph = Graph(figure="a", actions=[Action(action="a")])

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
        graph = Graph(figure="a", actions=[Action(action="a")])
        assert graph.type == "graph"
        with pytest.raises(ValidationError):
            Graph(figure="a", type="custom_component")

    def test_literal_type_custom_model(self):
        """Test understanding of Literal errors for custom models."""
        custom_graph = CustomGraph(figure=3, type="custom_component", actions=[Action(action="a")])
        assert custom_graph.type == "custom_component"

        with pytest.raises(ValidationError):
            CustomGraph(figure=3, type="graph")

    def test_literal_type_custom_model_no_type(self):
        """Test understanding of Literal errors for custom models without type."""
        custom_graph_no_type = CustomGraphNoType(figure=3, actions=[Action(action="a")])
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


@pytest.fixture
def dashboard_with_graph_and_action_revalidated(dashboard_with_graph_and_action):
    """Fixture for a dashboard with a graph and an action that has been revalidated."""
    return Dashboard.model_validate(dashboard_with_graph_and_action)


@pytest.fixture
def dashboard_with_graph_and_action_revalidated_with_tree(dashboard_with_graph_and_action):
    """Fixture for a dashboard with a graph and an action that has been revalidated with tree."""
    return Dashboard.model_validate(dashboard_with_graph_and_action, context={"build_tree": True})


@pytest.fixture
def dashboard_with_graph_and_action_revalidated_with_tree_revalidated(
    dashboard_with_graph_and_action_revalidated_with_tree,
):
    """Fixture for a dashboard with a graph and an action that has been revalidated with tree that has been revalidated."""
    return Dashboard.model_validate(dashboard_with_graph_and_action_revalidated_with_tree)


@pytest.fixture
def dashboard(request):
    """Parametrized fixture that returns the requested dashboard fixture."""
    return request.getfixturevalue(request.param)


@pytest.fixture
def dashboard_with_tree(request):
    """Fixture for a dashboard with tree."""
    return request.getfixturevalue(request.param)


# Fixture name constants for parametrization
DASHBOARDS_WITHOUT_TREE = [
    "dashboard_with_graph_and_action",
    "dashboard_with_graph_and_action_revalidated",
]

DASHBOARDS_WITH_TREE = [
    "dashboard_with_graph_and_action_revalidated_with_tree",
    "dashboard_with_graph_and_action_revalidated_with_tree_revalidated",
]


class TestDashboardTreeCreation:
    """Test tree creation using the validator approach."""

    @pytest.mark.parametrize("dashboard", DASHBOARDS_WITHOUT_TREE, indirect=True)
    def test_tree_creation_not_triggered(self, dashboard):
        """Test tree creation is not triggered."""
        assert dashboard._tree is None

    @pytest.mark.parametrize("dashboard_with_tree", DASHBOARDS_WITH_TREE, indirect=True)
    def test_tree_creation_triggered(self, dashboard_with_tree):
        """Test tree creation is triggered."""

        assert dashboard_with_tree._tree is not None

        # 0. Check trees are the same everywhere
        assert dashboard_with_tree._tree is dashboard_with_tree.pages[0]._tree

        # 1. Check root exists and has correct structure
        assert dashboard_with_tree._tree.name == "Root"

        # 2. Check node count matches expected hierarchy
        # Dashboard -> Page -> Graph -> Action = 4 nodes total
        assert len(dashboard_with_tree._tree) == 4

        # 3. Check tree depth
        assert dashboard_with_tree._tree.calc_height() == 4  # Root -> Dashboard -> Page -> Graph -> Action

        # 4. Verify node kinds are correct (field names)
        kind_checks = [
            (dashboard_with_tree.pages[0].id, "pages"),
            (dashboard_with_tree.pages[0].components[0].id, "components"),
            (dashboard_with_tree.pages[0].components[0].actions[0].id, "actions"),
        ]
        for model_id, expected_kind in kind_checks:
            assert dashboard_with_tree._tree[model_id].kind == expected_kind

        # 5. Check all nodes have valid data and correspond to real model objects
        models_to_check = [
            dashboard_with_tree,
            dashboard_with_tree.pages[0],
            dashboard_with_tree.pages[0].components[0],
            dashboard_with_tree.pages[0].components[0].actions[0],
        ]
        for model in models_to_check:
            node = dashboard_with_tree._tree[model.id]
            assert isinstance(node.data, VizroBaseModel)
            assert hasattr(node.data, "id")
            assert node.data is model

    @pytest.mark.parametrize("dashboard", DASHBOARDS_WITHOUT_TREE, indirect=True)
    def test_private_attribute_parent_model(self, dashboard):
        """Test private attribute _parent_model."""
        assert dashboard.pages[0].components[0].actions[0]._parent_model is not None


@pytest.fixture
def dashboard_with_component_for_pre_build():
    """Fixture for a dashboard with a component for pre-build."""
    return Dashboard(pages=[Page(title="Test Page", components=[Component(x="c1")])])


class TestPreBuildTreeAddition:
    """Test adding models via pre-build."""

    def test_pre_build_tree_addition(self, dashboard_with_component_for_pre_build):
        """Test adding models via pre-build."""
        dashboard = Dashboard.model_validate(dashboard_with_component_for_pre_build, context={"build_tree": True})

        for page in dashboard.pages:
            page.pre_build()

        # Check component was changed by pre-build
        new_component = dashboard.pages[0].components[0]
        assert isinstance(new_component, Component)
        assert new_component.x == "new c1!!!"

        # Check all tree nodes have valid data and correspond to real model objects
        models_to_check = [
            dashboard,
            dashboard.pages[0],
            new_component,
        ]
        for model in models_to_check:
            node = dashboard._tree[model.id]
            assert isinstance(node.data, VizroBaseModel)
            assert hasattr(node.data, "id")
            assert node.data is model
