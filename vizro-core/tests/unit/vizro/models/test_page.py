import re

import pytest
from pydantic import ValidationError

import vizro.actions as va
import vizro.models as vm
from vizro import Vizro
from vizro._constants import ON_PAGE_LOAD_ACTION_PREFIX, RESET_CONTROLS_ACTION_PREFIX
from vizro.actions._on_page_load import _on_page_load
from vizro.managers import model_manager


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

    def test_page_user_actions_replace_default_action(self, standard_px_chart):
        page = vm.Page(
            title="Page 1",
            components=[vm.Graph(id="scatter_chart", figure=standard_px_chart)],
            actions=[va.update_targets(), va.show_notification(text="Welcome!")],
        )
        page.pre_build()

        # User-provided actions are respected instead of being overwritten by the automatic on-page-load action.
        assert not any(isinstance(action, _on_page_load) for action in page.actions)
        refresh_action, notification_action = page.actions
        assert isinstance(refresh_action, va.update_targets)
        assert isinstance(notification_action, va.show_notification)

        # The first action in the chain runs after the page load; subsequent actions run when the previous one finishes.
        assert refresh_action._trigger == f"{ON_PAGE_LOAD_ACTION_PREFIX}_trigger_{page.id}.data"
        assert refresh_action._prevent_initial_call_of_guard is False
        assert notification_action._trigger == f"{refresh_action.id}_finished.data"
        assert notification_action._prevent_initial_call_of_guard is True

    def test_page_empty_actions_disables_on_page_load(self, standard_px_chart):
        page = vm.Page(
            title="Page 1",
            components=[vm.Graph(id="scatter_chart", figure=standard_px_chart)],
            actions=[],
        )
        page.pre_build()

        # Explicitly setting actions=[] disables the automatic on-page-load refresh.
        assert page.actions == []


class TestPageResetControlsAction:
    """Tests the dedicated reset-controls action that backs the "Reset all" button.

    A full build is used (rather than calling `pre_build` directly) because the reset action is only created when the
    page has controls, and controls require their selectors to be built first.
    """

    @pytest.mark.parametrize(
        "actions, expected_page_actions",
        [
            ("UNSET", [_on_page_load]),  # default: on-page-load refresh kept
            ([va.show_notification(text="Hi")], [va.show_notification]),  # customized page-load actions
            (None, []),  # on-page-load disabled
            ([], []),  # on-page-load disabled
        ],
    )
    def test_reset_controls_action_created(self, actions, expected_page_actions, standard_px_chart):
        actions_kwarg = {} if actions == "UNSET" else {"actions": actions}
        filter = vm.Filter(id="continent_filter", column="continent")
        page = vm.Page(
            title="Page 1",
            components=[vm.Graph(id="scatter_chart", figure=standard_px_chart)],
            controls=[filter],
            **actions_kwarg,
        )
        filter.pre_build()
        page.pre_build()

        # The reset action is created independently of Page.actions.
        assert [type(action) for action in page.actions] == expected_page_actions

        reset_action = page._reset_controls_action
        # It is a plain update_targets (not the _on_page_load subclass) refreshing all figures and dynamic filters.
        assert type(reset_action) is va.update_targets
        assert reset_action.id == f"{RESET_CONTROLS_ACTION_PREFIX}_{page.id}"
        assert reset_action.targets == ["scatter_chart"]
        assert reset_action._trigger == f"{RESET_CONTROLS_ACTION_PREFIX}_trigger_{page.id}.data"
        assert reset_action._first_in_chain_trigger == reset_action._trigger
        # Reset only runs on the "Reset all" click, never on the initial page render.
        assert reset_action._prevent_initial_call_of_guard is True
        # The reset action lives outside the page's model tree but its page is still resolvable via _parent_model.
        assert model_manager._get_model_page(reset_action) is page

    def test_no_reset_controls_action_without_controls(self, standard_px_chart):
        page = vm.Page(title="Page 1", components=[vm.Graph(id="scatter_chart", figure=standard_px_chart)])
        page.pre_build()

        assert page._reset_controls_action is None

    def test_reset_button_wired_to_reset_trigger_not_on_page_load(self, standard_px_chart):
        """The "Reset all" clientside callback must write to the reset trigger, not the on-page-load trigger.

        This guards against a regression that re-points reset back at the on-page-load trigger, which would make
        resetting controls re-run `Page.actions` instead of the dedicated refresh. Dash's global callback map is
        populated at build time and cleared by `Vizro._reset()` (which the autouse fixture runs), so it only contains
        this dashboard's callbacks.
        """
        from dash._callback import GLOBAL_CALLBACK_MAP

        page = vm.Page(
            id="mypage",
            title="Page 1",
            components=[vm.Graph(id="scatter_chart", figure=standard_px_chart)],
            controls=[vm.Filter(id="continent_filter", column="continent")],
            actions=[va.show_notification(text="Hi")],  # customized so reset must not re-run the page chain
        )
        Vizro().build(vm.Dashboard(pages=[page]))

        # Collect the output component ids of every callback triggered by the "Reset all" button.
        reset_button_output_ids = set()
        for callback in GLOBAL_CALLBACK_MAP.values():
            if not any(input["id"] == "reset-button" for input in callback["inputs"]):
                continue
            outputs = callback["output"] if isinstance(callback["output"], list) else [callback["output"]]
            reset_button_output_ids |= {output.component_id for output in outputs}

        assert f"{RESET_CONTROLS_ACTION_PREFIX}_trigger_{page.id}" in reset_button_output_ids
        assert f"{ON_PAGE_LOAD_ACTION_PREFIX}_trigger_{page.id}" not in reset_button_output_ids


# TODO: Add unit tests for page build method
# TODO: Add unit tests for private methods in page build
