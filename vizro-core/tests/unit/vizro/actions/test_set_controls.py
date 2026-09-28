"""Unit tests for the set_controls action and the deprecated set_control alias.

End-to-end behavior (pre_build validation, callback function, cross-page sync, drill-through) is exercised through the
deprecated `set_control` alias in test_legacy_set_control.py, which delegates to the same set_controls implementation,
and through the Filter/Parameter default-action tests. These tests focus on the canonical set_controls API surface,
plus the same-page control-sync mesh finalization that collapses a mesh into one set_controls + one update_targets.
"""

import pytest
from pydantic import ValidationError

import vizro.actions as va
import vizro.models as vm
from vizro import Vizro
from vizro.actions import set_controls, update_targets
from vizro.managers import model_manager


class TestSetControlsInstantiation:
    def test_defaults(self):
        action = va.set_controls(controls=["filter_1"])
        assert action.type == "set_controls"
        assert action.controls == ["filter_1"]
        assert action.value is None

    def test_controls_is_required(self):
        # `controls` has no default: omitting it fails validation immediately rather than only at pre_build, so the
        # generated schema does not advertise an unrunnable `set_controls()` configuration.
        with pytest.raises(ValidationError, match="controls"):
            va.set_controls()

    def test_multiple_controls_and_value(self):
        action = va.set_controls(controls=["filter_1", "filter_2"], value="species")
        assert action.controls == ["filter_1", "filter_2"]
        assert action.value == "species"

    def test_single_control_id_coerced_to_list(self):
        # A single id string is accepted and normalized to a list immediately.
        action = va.set_controls(controls="filter_1")
        assert action.controls == ["filter_1"]
        assert action._control_ids == ["filter_1"]

    def test_control_ids_dedupe_preserves_order(self):
        assert va.set_controls(controls=["a", "a", "b", "a"])._control_ids == ["a", "b"]


class TestSetControlDeprecatedAlias:
    def test_set_control_is_subclass_of_set_controls(self):
        assert issubclass(va.set_control, va.set_controls)

    def test_set_control_emits_deprecation_warning(self):
        with pytest.warns(FutureWarning, match="`set_control` is deprecated"):
            va.set_control(control="filter_1")

    @pytest.mark.filterwarnings("ignore:`set_control` is deprecated:FutureWarning")
    def test_single_control_maps_to_controls_list(self):
        action = va.set_control(control="filter_1")
        assert action.type == "set_control"
        assert action.controls == ["filter_1"]

    @pytest.mark.filterwarnings("ignore:`set_control` is deprecated:FutureWarning")
    def test_list_control_maps_to_controls(self):
        action = va.set_control(control=["filter_1", "filter_2"])
        assert action.controls == ["filter_1", "filter_2"]


@pytest.fixture
def managers_control_sync_mesh(standard_px_chart):
    """A same-page control-sync mesh: mutual sync f1<->f2, plus f2->f3 (transitive)."""
    vm.Page(
        id="mesh-page",
        title="mesh-page",
        components=[
            vm.Graph(id="mesh_g1", figure=standard_px_chart),
            vm.Graph(id="mesh_g2", figure=standard_px_chart),
            vm.Graph(id="mesh_g3", figure=standard_px_chart),
        ],
        controls=[
            vm.Filter(id="mesh_f1", column="continent", targets=["mesh_g1", "mesh_f2"]),
            vm.Filter(id="mesh_f2", column="continent", targets=["mesh_g2", "mesh_f1", "mesh_f3"]),
            vm.Filter(id="mesh_f3", column="continent", targets=["mesh_g3"]),
        ],
    )
    Vizro._pre_build()


@pytest.fixture
def managers_control_sync_cross_page(standard_px_chart):
    """A cross-page sync (cf1->cf2) plus a same-page sync on the target page (cf2->cf3)."""
    vm.Page(
        id="cp-page-1",
        title="cp-page-1",
        components=[vm.Graph(id="cp_g1", figure=standard_px_chart)],
        controls=[vm.Filter(id="cf1", column="continent", targets=["cp_g1", "cf2"])],
    )
    vm.Page(
        id="cp-page-2",
        title="cp-page-2",
        components=[
            vm.Graph(id="cp_g2", figure=standard_px_chart),
            vm.Graph(id="cp_g3", figure=standard_px_chart),
        ],
        controls=[
            vm.Filter(id="cf2", column="continent", targets=["cp_g2", "cf3"]),
            vm.Filter(id="cf3", column="continent", targets=["cp_g3"]),
        ],
    )
    Vizro._pre_build()


@pytest.mark.usefixtures("managers_control_sync_mesh")
class TestControlSyncMeshFinalization:
    """Tests that a same-page control-sync mesh is collapsed into a single set_controls + update_targets."""

    def test_transitive_closure_and_cycle(self):
        # mesh_f1 syncs mesh_f2 directly and mesh_f3 transitively (via mesh_f2). The mutual f1<->f2 edge does not loop:
        # f2->f1 points back at the source, which is excluded.
        set_controls_action, update_targets_action = model_manager["mesh_f1"].selector.actions
        # The collapsed mesh action is the canonical (non-deprecated) `set_controls`, regardless of how the sync was
        # declared - the internal machinery never emits the deprecated `set_control`.
        assert isinstance(set_controls_action, set_controls)
        assert set_controls_action.controls == ["mesh_f2", "mesh_f3"]
        # The flag suppresses each synced control's own chain (via its guard), so the mesh resolves in two requests.
        assert set_controls_action._stop_implicit_actions_chaining is True
        # Precise figure union: f1's own figure plus every same-page synced control's figures.
        assert isinstance(update_targets_action, update_targets)
        assert update_targets_action.id == "__filter_action_mesh_f1"
        assert update_targets_action.targets == ["mesh_g1", "mesh_g2", "mesh_g3"]

    def test_symmetric_source(self):
        # From mesh_f2 the closure is mesh_f1 (direct) and mesh_f3 (direct); mesh_f1 back-edge to f2 is the source.
        set_controls_action, update_targets_action = model_manager["mesh_f2"].selector.actions
        assert set_controls_action.controls == ["mesh_f1", "mesh_f3"]
        assert set_controls_action._stop_implicit_actions_chaining is True
        assert set(update_targets_action.targets) == {"mesh_g1", "mesh_g2", "mesh_g3"}

    def test_non_synced_control_unchanged(self):
        # mesh_f3 syncs nothing, so it keeps its plain single-action chain (no set_controls, no flag) and refreshes only
        # its own figure. A direct change to it is a single request, exactly as before.
        [update_targets_action] = model_manager["mesh_f3"].selector.actions
        assert isinstance(update_targets_action, update_targets)
        assert update_targets_action.targets == ["mesh_g3"]

    def test_no_stale_actions_left_in_model_manager(self):
        # Finalization deletes the per-control actions it supersedes, so only the two collapsed set_controls remain.
        set_controls_ids = [action.id for action in model_manager._get_models(set_controls)]
        assert len(set_controls_ids) == 2


@pytest.mark.usefixtures("managers_control_sync_cross_page")
class TestControlSyncCrossPageFinalization:
    """Tests that transitive expansion stops at a page boundary but same-page meshes still collapse per page."""

    def test_cross_page_target_is_terminal(self):
        # cf1 (page 1) syncs cf2 (page 2). cf2 is cross-page, so its own edge to cf3 is NOT followed, and its figures
        # (on page 2) are not refreshed by cf1. cf1 therefore only sets cf2 and refreshes its own figure.
        set_controls_action, update_targets_action = model_manager["cf1"].selector.actions
        assert set_controls_action.controls == ["cf2"]
        assert set_controls_action._stop_implicit_actions_chaining is True
        assert update_targets_action.targets == ["cp_g1"]

    def test_same_page_transitive_on_target_page(self):
        # On page 2, cf2 -> cf3 is a normal same-page sync and collapses independently.
        set_controls_action, update_targets_action = model_manager["cf2"].selector.actions
        assert set_controls_action.controls == ["cf3"]
        assert set_controls_action._stop_implicit_actions_chaining is True
        assert update_targets_action.targets == ["cp_g2", "cp_g3"]


@pytest.fixture
def managers_control_sync_mixed_filter_parameter(standard_px_chart):
    """A same-page mesh mixing a Filter and a Parameter that sync each other.

    The Parameter targets a figure *argument* (``mix_g2.x``), so the collapsed ``update_targets`` must reduce that to
    the bare figure id ``mix_g2`` - the same notation Filters use - when it unions the mesh's figures.
    """
    vm.Page(
        id="mix-page",
        title="mix-page",
        components=[
            vm.Graph(id="mix_g1", figure=standard_px_chart),
            vm.Graph(id="mix_g2", figure=standard_px_chart),
        ],
        controls=[
            vm.Filter(id="mix_f1", column="continent", targets=["mix_g1", "mix_p1"]),
            vm.Parameter(
                id="mix_p1",
                targets=["mix_g2.x", "mix_f1"],
                selector=vm.Dropdown(options=["lifeExp", "gdpPercap"], value="lifeExp"),
            ),
        ],
    )
    Vizro._pre_build()


@pytest.mark.usefixtures("managers_control_sync_mixed_filter_parameter")
class TestControlSyncMixedFilterParameterFinalization:
    """A Filter<->Parameter mesh collapses like any other, reducing the Parameter's `figure.arg` to a figure id."""

    def test_filter_source_reduces_parameter_figure_argument(self):
        # From the Filter: it syncs the Parameter, and the union is the Filter's own figure (mix_g1) plus the
        # Parameter's figure - reduced from "mix_g2.x" to "mix_g2".
        set_controls_action, update_targets_action = model_manager["mix_f1"].selector.actions
        assert set_controls_action.controls == ["mix_p1"]
        assert set_controls_action._stop_implicit_actions_chaining is True
        assert update_targets_action.targets == ["mix_g1", "mix_g2"]

    def test_parameter_source_reduces_own_figure_argument(self):
        # From the Parameter: it syncs the Filter, and the union is the Parameter's own figure ("mix_g2.x" -> "mix_g2")
        # plus the Filter's figure (mix_g1).
        set_controls_action, update_targets_action = model_manager["mix_p1"].selector.actions
        assert set_controls_action.controls == ["mix_f1"]
        assert set_controls_action._stop_implicit_actions_chaining is True
        assert update_targets_action.targets == ["mix_g2", "mix_g1"]


@pytest.fixture
def managers_control_sync_explicit_action_targets(standard_px_chart):
    """A default source syncing two same-page targets that have explicit selector actions.

    ``expl_deferred`` opts out with ``actions=[]`` and ``expl_custom`` runs a custom chain. Neither runs the generated
    default chain, so finalization must keep them as plain sync targets: their values are set, but they are not guarded
    and their figures are not folded into the source's collapsed ``update_targets``.
    """
    vm.Page(
        id="expl-page",
        title="expl-page",
        components=[
            vm.Graph(id="expl_g_source", figure=standard_px_chart),
            vm.Graph(id="expl_g_deferred", figure=standard_px_chart),
            vm.Graph(id="expl_g_custom", figure=standard_px_chart),
        ],
        controls=[
            vm.Filter(id="expl_source", column="continent", targets=["expl_g_source", "expl_deferred", "expl_custom"]),
            vm.Filter(
                id="expl_deferred",
                column="continent",
                targets=["expl_g_deferred"],
                selector=vm.Checklist(actions=[]),
            ),
            vm.Filter(
                id="expl_custom",
                column="continent",
                targets=["expl_g_custom"],
                selector=vm.Checklist(actions=[update_targets(targets=["expl_g_custom"])]),
            ),
        ],
    )
    Vizro._pre_build()


@pytest.mark.usefixtures("managers_control_sync_explicit_action_targets")
class TestControlSyncExplicitActionTargetsPreserved:
    """Targets with explicit actions (custom or `[]`) are synced but neither guarded nor subsumed into the union."""

    def test_source_sets_but_does_not_subsume_explicit_targets(self):
        # The source still sets both explicit-action targets (sync must happen), but its collapsed update_targets
        # refreshes only its OWN figure - the targets' figures are left to their own chains.
        set_controls_action, update_targets_action = model_manager["expl_source"].selector.actions
        assert set_controls_action.controls == ["expl_deferred", "expl_custom"]
        assert set_controls_action._stop_implicit_actions_chaining is True
        assert update_targets_action.targets == ["expl_g_source"]

    def test_no_guards_raised_for_explicit_targets(self):
        # Neither explicit-action target is guarded, so its own chain still runs (or, for actions=[], stays inert).
        set_controls_action = model_manager["expl_source"].selector.actions[0]
        assert set_controls_action._guardable_same_page_controls == []
        assert set_controls_action.outputs == ["expl_deferred", "expl_custom"]

    def test_explicit_targets_keep_their_own_chains(self):
        # The targets are not sources (no default chain), so finalization leaves their selector actions untouched.
        assert model_manager["expl_deferred"].selector.actions == []
        [custom_action] = model_manager["expl_custom"].selector.actions
        assert isinstance(custom_action, update_targets)
        assert custom_action.targets == ["expl_g_custom"]
