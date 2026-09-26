from __future__ import annotations

import warnings
from collections import deque
from collections.abc import Generator, Iterable
from typing import TYPE_CHECKING, Any, cast

from typing_extensions import TypeIs

from vizro.managers import model_manager
from vizro.managers._model_manager import FIGURE_MODELS
from vizro.models import (
    Cascader,
    Checklist,
    Container,
    DatePicker,
    DateTimePicker,
    Dropdown,
    RadioItems,
    RangeSlider,
    Slider,
    Switch,
    TimePicker,
    VizroBaseModel,
)
from vizro.models._components.form._form_utils import get_dict_options_and_value
from vizro.models._components.form.cascader import get_cascader_default_value
from vizro.models.types import ControlType, ModelID, SelectorType

if TYPE_CHECKING:
    from vizro.models import Page

SELECTORS: dict[str, tuple[type, ...]] = {
    "numerical": (RangeSlider, Slider),
    "categorical": (Checklist, Dropdown, RadioItems),
    "date": (DatePicker,),
    "datetime": (DateTimePicker,),
    "time": (TimePicker,),
    "boolean": (Switch,),
    "hierarchical": (Cascader,),
}


# Type-narrowing functions to avoid needing to cast every time we do isinstance for a selector.
def _is_numerical_or_date_selector(x: object) -> TypeIs[RangeSlider | Slider | DatePicker]:
    return isinstance(x, SELECTORS["numerical"] + SELECTORS["date"])


def _is_datetime_selector(x: object) -> TypeIs[DateTimePicker]:
    return isinstance(x, SELECTORS["datetime"])


def _is_categorical_selector(x: object) -> TypeIs[Checklist | Dropdown | RadioItems]:
    return isinstance(x, SELECTORS["categorical"])


def _is_boolean_selector(x: object) -> TypeIs[Switch]:
    return isinstance(x, SELECTORS["boolean"])


def _is_hierarchical_selector(x: object) -> TypeIs[Cascader]:
    return isinstance(x, SELECTORS["hierarchical"])


def _validate_targets(targets: list[str], root_model: VizroBaseModel) -> None:
    component_figures: Generator[VizroBaseModel] = model_manager._get_models(FIGURE_MODELS, root_model)
    component_figure_ids = [model.id for model in component_figures]
    for target in targets:
        if (target_id := target.split(".")[0]) not in component_figure_ids:
            raise ValueError(
                f"Target {target_id} not found within the {root_model.id}. A target must be a component on "
                f"{root_model.id}, or the id of another Filter or Parameter to keep in sync (which may be on a "
                f"different page). Check that '{target_id}' is spelled correctly and refers to an existing model."
            )


# TODO: Consider rewriting the model_manager._get_model_page to model_manager._get_model_parent()
#  This would make the following renaming logical: model_manager._get_models -> model_manager._get_model_children.
#  These two new methods could have the same signature.
#  Consider adding the parent_model_id to the VizroBaseModel and use that to find the parent model more easily.
def get_control_parent(control: ControlType) -> Page | Container | None:
    """Get the nearest ancestor Container or Page for the given control."""
    # Return None if the control is not part of any page.
    if (page := model_manager._get_model_page(model=control)) is None:
        return None

    nearest_ancestor_container = None
    # Find the deepest Container that contains this control (DFS pre-order in `_get_models` gives deepest match last).
    for container in model_manager._get_models(model_type=Container, root_model=page):
        if control in model_manager._get_models(model_type=type(control), root_model=container):
            nearest_ancestor_container = container

    # Fallback to the page if not nested inside any container.
    return nearest_ancestor_container or page


def extract_control_targets(control: ControlType) -> list[ModelID]:
    """Split control (Filter/Parameter) targets out of ``control.targets``, validating and returning them.

    A Filter/Parameter can target another control to keep the two in sync (see the `set_control` action). Such
    "control targets" are validated and semantically different from "figure targets", so this removes them from
    ``control.targets`` in place and returns them separately. The remaining figure targets are validated later by
    `check_control_targets`.

    A control target must be a *different* control: self-targeting would create a self-referential sync loop. The
    target may be on the same page as the control or on a different page. A same-page target's selector value is set
    directly; a different-page target is kept in sync through the internal ``vizro_controls_store`` and its value is
    applied when that page is opened (see the `set_control` action).
    """
    from vizro.models._controls import Filter, Parameter

    targeted_controls: list[ModelID] = []
    for target in control.targets.copy():
        if target not in model_manager:
            continue
        target_model = model_manager[target]
        if not isinstance(target_model, (Filter, Parameter)):
            continue

        # Forbid self-targeting: a control targeting itself would create a self-referential sync loop.
        if target == control.id:
            raise ValueError(f"Control '{control.id}' cannot target itself. Remove '{target}' from its `targets`.")

        control.targets.remove(target)
        targeted_controls.append(target)

    # Deduplicate (order-preserving) so a control listed more than once does not generate duplicate set_control
    # sync actions, using the same idiom as elsewhere in the codebase (e.g. `set_control._control_ids`).
    return list(dict.fromkeys(targeted_controls))


def warn_ignored_control_sync_targets(control: ControlType, targeted_controls: list[ModelID]) -> None:
    """Warn when control-sync targets are dropped because the selector has explicit ``actions``.

    A Filter/Parameter keeps a control target in sync by generating a default `set_control` action on its selector
    (see `build_default_control_selector_actions`). When the selector's `actions` are set explicitly, that default chain
    is not generated, so any control ids listed in `targets` are extracted and removed but never turned into a sync,
    silently doing nothing. Warn so the user knows to wire the sync themselves.
    """
    if targeted_controls:
        warnings.warn(
            f"Control '{control.id}' lists control target(s) {targeted_controls} in `targets`, but its selector has "
            f"explicit `actions`, so these targets are not kept in sync automatically. Add a `set_control` action to "
            f"the selector's `actions` for each one to sync them, and remove them from `targets`.",
            UserWarning,
        )


def build_default_control_selector_actions(
    selector: SelectorType,
    targeted_controls: list[ModelID],
    targeted_figures: list[str],
    update_targets_action_id: str,
) -> None:
    """Set a control selector's default action chain: sync the targeted controls, then refresh its targets.

    Filter and Parameter share this: on selector change they first push the new value to every control they keep in
    sync (via a single `set_control` that targets them all), then refresh their own targets (via `update_targets`).
    The `set_control` action runs first so the latest value is applied before the refresh.
    """
    # Local import to avoid a circular import between this module and vizro.actions.
    from vizro.actions import set_control, update_targets

    # One `set_control` drives every synced control at once (one callback, one notification) instead of one action
    # per control. `targeted_controls` is already de-duplicated and order-preserving (see `extract_control_targets`).
    # `value` is omitted: a selector-driven sync ignores it and propagates the selector's own live value.
    selector.actions = [
        *([set_control(control=targeted_controls)] if targeted_controls else []),
        update_targets(id=update_targets_action_id, targets=targeted_figures),
    ]


def get_sync_closure(source: ControlType) -> tuple[list[ModelID], list[ModelID]]:
    """Resolve the full control-sync mesh reachable from ``source`` into a single set of controls and figures.

    Returns ``(closure_controls, closure_figures)``:

    * ``closure_controls`` - every control transitively kept in sync with ``source`` (a cycle-safe, order-preserving
      traversal of the ``_synced_control_targets`` edges, excluding ``source`` itself). The mesh is only expanded
      through *same-page* controls; a cross-page target is included as a terminal node but its own edges are not
      followed - its sync applies when its page is opened (see the `set_control` action).
    * ``closure_figures`` - the precise union of figure targets that must be refreshed: ``source``'s own figures plus
      those of every *same-page* synced control. Parameter targets use ``"<figure>.<argument>"`` notation, so they are
      reduced to the figure id; Filter targets are already bare figure ids.

    Together these let one `set_control` set the whole mesh and one `update_targets` refresh every affected figure,
    collapsing the mesh into two HTTP requests (see `finalize_control_sync_chains`).
    """
    source_page = model_manager._get_model_page(source)

    closure_controls: list[ModelID] = []
    # Same-page subset of closure_controls, tracked during the BFS so the page lookup runs once per control (it is
    # reused below to gather figures - only same-page controls contribute figures).
    same_page_controls: list[ModelID] = []
    seen: set[ModelID] = {source.id}
    queue: deque[ModelID] = deque(source._synced_control_targets)
    while queue:
        control_id = queue.popleft()
        if control_id in seen:
            continue
        seen.add(control_id)
        closure_controls.append(control_id)
        # Only expand the mesh through same-page controls; a cross-page target is terminal (see docstring).
        target_control = cast(ControlType, model_manager[control_id])
        if model_manager._get_model_page(target_control) is source_page:
            same_page_controls.append(control_id)
            queue.extend(target_control._synced_control_targets)

    closure_figures: list[ModelID] = []

    def _add_figure_targets(control: ControlType) -> None:
        for target in control.targets:
            figure_id = cast(ModelID, target.partition(".")[0])
            if figure_id and figure_id not in closure_figures:
                closure_figures.append(figure_id)

    _add_figure_targets(source)
    for control_id in same_page_controls:
        _add_figure_targets(cast(ControlType, model_manager[control_id]))

    return closure_controls, closure_figures


def finalize_control_sync_chains() -> None:
    """Collapse every same-page control-sync mesh into two HTTP requests.

    During ``pre_build`` each synced control gets a default chain that targets only its *direct* sync targets and
    figures (`build_default_control_selector_actions`). Setting a target's value then re-fires that target's own chain,
    so a mesh cascades into many requests. This runs once after all controls are pre-built (so every control's figure
    targets and ``_synced_control_targets`` are final) and rewrites each source's chain to cover the whole transitive
    mesh at once:

    * a single ``set_control(control=<all transitively-synced controls>, _stop_implicit_actions_chaining=True)`` sets
      every mesh control and raises their guards so their own chains do not fire, and
    * a single ``update_targets(targets=<precise figure union>)`` refreshes every affected figure.

    The superseded per-control actions are removed from the model_manager first, otherwise their callbacks would still
    be registered in ``Dashboard.build`` and reusing the ``update_targets`` id would raise ``DuplicateIDError``.
    """
    from vizro.actions import set_control, update_targets
    from vizro.models import Filter, Parameter

    # Materialize before mutating: rebuilding the chains adds/removes models from the model_manager.
    sources = [
        control
        for control in cast(Iterable[ControlType], model_manager._get_models((Filter, Parameter)))
        if control._synced_control_targets
    ]

    for source in sources:
        closure_controls, closure_figures = get_sync_closure(source)

        old_set_control = next((action for action in source.selector.actions if isinstance(action, set_control)), None)
        old_update_targets = next(
            (action for action in source.selector.actions if isinstance(action, update_targets)), None
        )
        # A finalized source always has both: a non-empty `_synced_control_targets` means the default chain was built
        # with a `set_control` alongside its `update_targets`. Fail with a clear message (rather than a bare
        # StopIteration) if that coupling ever drifts.
        if old_set_control is None or old_update_targets is None:
            raise RuntimeError(
                f"Cannot collapse the control-sync mesh for '{source.id}': its selector chain is missing the expected "
                f"set_control/update_targets actions."
            )
        update_targets_action_id = old_update_targets.id
        del model_manager[old_set_control.id]
        del model_manager[old_update_targets.id]

        # Reassigning selector.actions re-runs make_actions_chain (validate_assignment) so the new chain is wired.
        build_default_control_selector_actions(
            selector=source.selector,
            targeted_controls=closure_controls,
            targeted_figures=closure_figures,
            update_targets_action_id=update_targets_action_id,
        )

        new_set_control = next(action for action in source.selector.actions if isinstance(action, set_control))
        new_set_control._stop_implicit_actions_chaining = True

        # Newly created actions must run their own pre_build (mirrors Parameter.pre_build).
        for action in source.selector.actions:
            action.pre_build()


def check_control_targets(control: ControlType) -> None:
    root_model = get_control_parent(control=control)
    # Search by using "_get_models" instead of "if control not in root_model.controls" to handle nested custom controls.
    if root_model is None or control not in model_manager._get_models(root_model=root_model.controls):
        raise ValueError(f"Control {control.id} should be defined within Page.controls or Container.controls.")

    _validate_targets(targets=control.targets, root_model=root_model)


def warn_missing_id_for_url_control(control: ControlType) -> None:
    if control.show_in_url and "id" not in control.model_fields_set:
        warnings.warn(
            "`show_in_url=True` is set but no `id` was provided. "
            "Shareable URLs might be unreliable if your dashboard configuration changes in future. "
            "If you want to ensure that links continue working, set a fixed `id`.",
            UserWarning,
        )


def get_selector_default_value(selector: SelectorType) -> Any:  # noqa: PLR0911
    """Get default value for a selector if not explicitly provided.

    This is used to set selector.value in controls so that the "Reset controls" button works. Ideally it would be
    done elsewhere, e.g. in the selector models themselves, but that is tricky to get in the right order because it
    would require running the selector.pre_build as part of Filter.pre_build.
    """
    if selector.value is not None:
        return selector.value

    if _is_numerical_or_date_selector(selector):
        is_range = isinstance(selector, RangeSlider) or getattr(selector, "range", False)
        return [selector.min, selector.max] if is_range else selector.min
    elif _is_categorical_selector(selector):
        is_multi = isinstance(selector, Checklist) or getattr(selector, "multi", False)
        _, default_value = get_dict_options_and_value(options=selector.options, value=None, multi=is_multi)
        return default_value
    elif _is_hierarchical_selector(selector):
        is_multi = getattr(selector, "multi", False)
        return get_cascader_default_value(
            selector.options, multi=is_multi, full_path=getattr(selector, "full_path", False)
        )
    elif isinstance(selector, TimePicker):
        # dmc.TimePicker needs "" rather than None to properly set originalValue for resetting control.
        return ["", ""] if selector.range else ""
    elif isinstance(selector, DateTimePicker):
        # Initial value uses date-only ISO strings (no time component) so the inline TimePicker
        # shows as cleared (--:--). The filter logic pads date-only ranges to start-of-day / end-of-day,
        # so the dashboard still shows the full date range by default — exactly matches DatePicker's
        # default behavior with the added "time can be set later" affordance.
        if selector.range:
            datetime_default: Any = (
                [f"{selector.min}", f"{selector.max}"]
                if (selector.min is not None and selector.max is not None)
                else ["", ""]
            )
        else:
            datetime_default = f"{selector.min}" if selector.min is not None else ""
        return datetime_default
    # Boolean selectors always have a default value specified so no need to handle them here.
    return None


def get_selector_parent_control(selector: SelectorType) -> ControlType:
    """Get the parent control of a selector."""
    from vizro.models import Filter, Parameter

    for candidate_parent in cast(
        Iterable[ControlType], [*model_manager._get_models(Parameter), *model_manager._get_models(Filter)]
    ):
        if selector is candidate_parent.selector:
            return candidate_parent

    raise ValueError(f"Selector {selector.id} does not have a parent control.")
