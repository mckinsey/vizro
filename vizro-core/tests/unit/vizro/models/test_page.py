import re

import pytest
from pydantic import ValidationError

import vizro.models as vm
from vizro._constants import ON_PAGE_LOAD_ACTION_PREFIX
from vizro.actions._on_page_load import _on_page_load


class TestPageInstantiation:
    """Tests model instantiation and the validators run at that time."""

    def test_create_page_mandatory_only(self):
        page = vm.Page(title="Page 1", components=[vm.Button(), vm.Button()])
        assert isinstance(page.components[0], vm.Button) and isinstance(page.components[1], vm.Button)
        assert page.layout.grid == [[0], [1]]
        assert page.controls == []
        assert page.title == "Page 1"
        assert page.path == "/page-1"
        assert page.actions == []
        assert page._action_outputs == {"title": f"{page.id}_title.children"}
        assert page._action_triggers == {"__default__": f"{ON_PAGE_LOAD_ACTION_PREFIX}_trigger_{page.id}.data"}

    def test_create_page_mandatory_and_optional(self):
        page = vm.Page(
            id="my-id",
            title="Page 1",
            components=[vm.Button(), vm.Button()],
            layout=vm.Grid(grid=[[0, 1]]),
            path="my-path",
            description=vm.Tooltip(id="tooltip-id", text="Test description", icon="info"),
        )
        assert isinstance(page.components[0], vm.Button) and isinstance(page.components[1], vm.Button)
        assert isinstance(page.description, vm.Tooltip)
        assert page.id == "my-id"
        assert page.layout.grid == [[0, 1]]
        assert page.controls == []
        assert page.title == "Page 1"
        assert page.path == "/my-path"
        assert page.actions == []
        assert page._action_outputs == {
            "title": "my-id_title.children",
            "description": "tooltip-id-text.children",
        }
        assert page._action_triggers == {"__default__": f"{ON_PAGE_LOAD_ACTION_PREFIX}_trigger_my-id.data"}

    def test_create_page_mandatory_and_optional_legacy_layout(self):
        with pytest.warns(FutureWarning, match="The `Layout` model has been renamed"):
            page = vm.Page(
                id="my-id",
                title="Page 1",
                components=[vm.Button(), vm.Button()],
                layout=vm.Layout(grid=[[0, 1]]),
                path="my-path",
            )
        assert isinstance(page.components[0], vm.Button) and isinstance(page.components[1], vm.Button)
        assert page.id == "my-id"
        assert page.layout.grid == [[0, 1]]
        assert page.controls == []
        assert page.title == "Page 1"
        assert page.path == "/my-path"
        assert page.actions == []

    def test_mandatory_title_missing(self):
        with pytest.raises(ValidationError, match="Field required"):
            vm.Page(id="my-id", components=[vm.Button()])

    def test_mandatory_components_missing(self):
        with pytest.raises(ValidationError, match="Field required"):
            vm.Page(title="Page 1")

    def test_set_id_duplicate_title_valid(self):
        vm.Page(id="my-id-1", title="Page 1", components=[vm.Button()])
        vm.Page(id="my-id-2", title="Page 1", components=[vm.Button()])

    @pytest.mark.parametrize(
        "test_path, expected",
        [
            ("Title", "/title"),
            ("this-path-works", "/this-path-works"),
            ("2147abc", "/2147abc"),
            ("this_path_works", "/this_path_works"),
            ("this/path/works", "/this/path/works"),
            ("", "/page-12"),
        ],
    )
    def test_set_path_valid(self, test_path, expected):
        page = vm.Page(title="Page 1/2", components=[vm.Button()], path=test_path)
        assert page.path == expected

    @pytest.mark.parametrize(
        "test_path", ["this needs? fixing*", " this needs fixing", "THIS NEEDS FIXING", "this-needs!@#$%^&*()+=-fixing"]
    )
    def test_set_path_invalid(self, test_path):
        page = vm.Page(title="Page 1", components=[vm.Button()], path=test_path)
        assert page.path == "/this-needs-fixing"

    def test_check_for_valid_control_types(self):
        with pytest.raises(
            ValidationError, match=re.escape("'type' does not match any of the expected tags: 'filter', 'parameter'")
        ):
            vm.Page(title="Page Title", components=[vm.Button()], controls=[vm.Button()])


class TestPagePreBuildMethod:
    def test_page_default_action(self, standard_px_chart):
        page = vm.Page(title="Page 1", components=[vm.Graph(id="scatter_chart", figure=standard_px_chart)])
        page.pre_build()
        [default_action] = page.actions

        assert isinstance(default_action, _on_page_load)
        assert default_action.id == f"{ON_PAGE_LOAD_ACTION_PREFIX}_{page.id}"
        assert default_action.targets == ["scatter_chart"]
        assert default_action._trigger == f"{ON_PAGE_LOAD_ACTION_PREFIX}_trigger_{page.id}.data"
        assert default_action._prevent_initial_call_of_guard is False


class TestPageBuildMethod:
    def test_page_build_returns_correct_structure(self):
        page = vm.Page(id="test-page", title="Test Page", components=[vm.Button()])
        page.pre_build()
        result = page.build()

        # Page build should return html.Div containing control-panel and page-components
        assert result.__class__.__name__ == "Div"
        # Check that children contains exactly two elements (control-panel and page-components)
        assert len(result.children) == 2

    def test_page_build_control_panel_hidden_when_no_controls(self):
        page = vm.Page(id="test-page", title="Test Page", components=[vm.Button()])
        page.pre_build()
        result = page.build()

        control_panel = result.children[0]
        assert control_panel.id == "control-panel"
        assert control_panel.hidden is True

    def test_page_build_control_panel_visible_when_controls_present(self, standard_px_chart):
        page = vm.Page(
            id="test-page",
            title="Test Page",
            components=[vm.Graph(id="graph", figure=standard_px_chart)],
            controls=[vm.Filter(column="continent")],
        )
        page.pre_build()
        result = page.build()

        control_panel = result.children[0]
        assert control_panel.id == "control-panel"
        assert control_panel.hidden is False
        # Control panel should contain the built filter
        assert len(control_panel.children) == 1

    def test_page_build_page_components_container(self):
        page = vm.Page(id="test-page", title="Test Page", components=[vm.Button()])
        page.pre_build()
        result = page.build()

        page_components = result.children[1]
        assert page_components.id == "page-components"

    def test_page_build_includes_on_page_load_trigger_store(self):
        page = vm.Page(id="test-page", title="Test Page", components=[vm.Button()])
        page.pre_build()
        result = page.build()

        page_components = result.children[1]
        # Find dcc.Store with on_page_load trigger id
        stores = [
            child for child in page_components.children if hasattr(child, "id") and "on_page_load" in str(child.id)
        ]
        assert len(stores) >= 1

    def test_page_build_includes_download_component(self):
        page = vm.Page(id="test-page", title="Test Page", components=[vm.Button()])
        page.pre_build()
        result = page.build()

        page_components = result.children[1]
        # Find dcc.Download component
        downloads = [
            child
            for child in page_components.children
            if child.__class__.__name__ == "Download" and child.id == "vizro_download"
        ]
        assert len(downloads) == 1

    def test_page_build_includes_location_component(self):
        page = vm.Page(id="test-page", title="Test Page", components=[vm.Button()])
        page.pre_build()
        result = page.build()

        page_components = result.children[1]
        # Find dcc.Location component
        locations = [
            child
            for child in page_components.children
            if child.__class__.__name__ == "Location" and child.id == "vizro_url"
        ]
        assert len(locations) == 1

    def test_page_build_includes_notification_container(self):
        page = vm.Page(id="test-page", title="Test Page", components=[vm.Button()])
        page.pre_build()
        result = page.build()

        page_components = result.children[1]
        # Find NotificationContainer component
        notifications = [
            child
            for child in page_components.children
            if child.__class__.__name__ == "NotificationContainer" and child.id == "vizro-notifications"
        ]
        assert len(notifications) == 1

    def test_page_build_with_multiple_components(self):
        page = vm.Page(
            id="test-page",
            title="Test Page",
            components=[vm.Button(id="btn1"), vm.Button(id="btn2"), vm.Card(id="card1", text="Card")],
            layout=vm.Grid(grid=[[0, 1], [2, 2]]),
        )
        page.pre_build()
        result = page.build()

        page_components = result.children[1]
        assert page_components.id == "page-components"

    def test_page_build_with_graph_component(self, standard_px_chart):
        page = vm.Page(
            id="test-page",
            title="Test Page",
            components=[vm.Graph(id="test-graph", figure=standard_px_chart)],
        )
        page.pre_build()
        result = page.build()

        page_components = result.children[1]
        assert page_components.id == "page-components"
