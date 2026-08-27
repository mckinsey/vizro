from collections.abc import Iterable
from typing import Annotated, Literal, cast

from dash import dcc, html
from pydantic import AfterValidator, Field, PrivateAttr, model_validator

from vizro._constants import PARAMETER_ACTION_PREFIX
from vizro.managers import model_manager
from vizro.models import VizroBaseModel
from vizro.models._controls._controls_utils import (
    _is_categorical_selector,
    _is_datetime_selector,
    _is_hierarchical_selector,
    _is_numerical_or_date_selector,
    build_control_sync_actions,
    check_control_targets,
    extract_control_targets,
    get_selector_default_value,
    warn_missing_id_for_url_control,
)
from vizro.models._models_utils import _log_call
from vizro.models.types import ModelID, SelectorType, _IdProperty


def check_dot_notation(target):
    if "." not in target:
        return target

    # Use the first argument segment (not the full remainder) so that nested addressing like
    # "<component>.figure.<arg>" is rejected too, not only the exact "<component>.figure".
    targeted_argument = target.split(".")[1]

    if targeted_argument == "figure":
        raise ValueError(
            f"Invalid target {target}. Targets must be supplied in the form <target_component>.<target_argument>. "
            "Arguments of the CapturedCallable function can be targeted directly, and not via <.figure.>."
        )
    return target


def check_data_frame_as_target_argument(target):
    if "." not in target:
        return target

    targeted_argument = target.split(".", 1)[1]
    if targeted_argument.startswith("data_frame") and targeted_argument.count(".") != 1:
        raise ValueError(
            f"Invalid target {target}. 'data_frame' target must be supplied in the form "
            "<target_component>.data_frame.<dynamic_data_argument>"
        )
    # TODO: Add validation: Make sure the target data_frame is _DynamicData.

    return target


def check_duplicate_parameter_target(targets):
    # Only figure-argument targets (in "<component>.<argument>" dot notation) must be unique across parameters. Bare
    # ids are control-sync targets (another control kept in sync) that multiple parameters may legitimately share, so
    # they are excluded from the duplicate check.
    all_targets = [target for target in targets if "." in target]
    for param in cast(Iterable[Parameter], model_manager._get_models(Parameter)):
        all_targets.extend(target for target in param.targets if "." in target)
    duplicate_targets = {item for item in all_targets if all_targets.count(item) > 1}
    if duplicate_targets:
        raise ValueError(f"Duplicate parameter targets {duplicate_targets} found.")
    return targets


class Parameter(VizroBaseModel):
    """Alter the arguments supplied to any `targets`.

    Abstract: Usage documentation
        [How to use parameters](../user-guides/parameters.md)

    Example:
        ```python
        import vizro.models as vm

        vm.Parameter(targets=["scatter.x"], selector=vm.Slider(min=0, max=1, default=0.8, title="Bubble opacity"))
        ```

    """

    type: Literal["parameter"] = "parameter"
    targets: Annotated[  # TODO[MS]: check if the double annotation is the best way to do this
        list[
            Annotated[
                str,
                AfterValidator(check_dot_notation),
                AfterValidator(check_data_frame_as_target_argument),
                Field(description="Targets in the form of `<target_component>.<target_argument>`."),
            ]
        ],
        AfterValidator(check_duplicate_parameter_target),
    ]
    selector: SelectorType
    show_in_url: bool = Field(
        default=False,
        description=(
            "Whether the parameter should be included in the URL query string. "
            "Useful for bookmarking or sharing dashboards with specific parameter values pre-set."
        ),
    )
    visible: bool = Field(
        default=True,
        description="Whether the parameter should be visible.",
    )

    _selector_properties: set[str] = PrivateAttr(set())

    @model_validator(mode="after")
    def check_id_set_for_url_control(self):
        """Check that the parameter has an `id` set if it is shown in the URL."""
        # If the parameter is shown in the URL, it should have an `id` set to ensure stable and readable URLs.
        warn_missing_id_for_url_control(control=self)
        return self

    @property
    def _action_outputs(self) -> dict[str, _IdProperty]:
        return {
            "selector": f"{self.id}.children",
            **self.selector._action_outputs,
            **(
                {selector_prop: f"{self.selector.id}.{selector_prop}" for selector_prop in self._selector_properties}
                if self._selector_properties
                else {}
            ),
        }

    @property
    def _action_triggers(self) -> dict[str, _IdProperty]:
        return self.selector._action_triggers

    @property
    def _action_inputs(self) -> dict[str, _IdProperty]:
        return {
            **self.selector._action_inputs,
            **(
                {selector_prop: f"{self.selector.id}.{selector_prop}" for selector_prop in self._selector_properties}
                if self._selector_properties
                else {}
            ),
        }

    @_log_call
    def pre_build(self):
        # Split control targets (used to sync this parameter with another control) out of self.targets; they are
        # validated and handled differently to the figure-argument targets that remain.
        targeted_controls = extract_control_targets(control=self)

        # Every remaining (figure) target must use the "<target_component>.<target_argument>" dot notation. This is
        # only checked now (not in the check_dot_notation validator) because that validator has to let bare control
        # ids through so they can be recognized as control targets above.
        for target in self.targets:
            if "." not in target:
                raise ValueError(
                    f"Invalid target {target}. Targets must be supplied in the form "
                    f"<target_component>.<target_argument>"
                )

        # A Parameter must have at least one figure target: its value is applied to figures only through its
        # "<target_component>.<target_argument>" targets, so a Parameter with no figure target has no argument to
        # apply its value to and cannot work. This mirrors the pre-syncing behavior where such a target was rejected
        # by check_dot_notation; it is enforced here because control targets (which are now allowed and extracted
        # above) could otherwise leave a Parameter with only control targets and no figure target.
        if not self.targets:
            raise ValueError(
                f"Parameter '{self.id}' must have at least one target in the form "
                f"<target_component>.<target_argument>. A Parameter that targets only other controls has no argument "
                f"to apply its value to."
            )

        check_control_targets(control=self)

        if (_is_numerical_or_date_selector(self.selector) or _is_datetime_selector(self.selector)) and (
            self.selector.min is None or self.selector.max is None
        ):
            raise TypeError(f"{self.selector.type} requires the arguments 'min' and 'max' when used within Parameter.")
        elif (
            _is_categorical_selector(self.selector) or _is_hierarchical_selector(self.selector)
        ) and not self.selector.options:
            raise TypeError(f"{self.selector.type} requires the argument 'options' when used within Parameter.")

        self.selector.value = get_selector_default_value(self.selector)

        if not self.selector.title:
            self.selector.title = ", ".join({target.rsplit(".")[-1] for target in self.targets})

        # A set of properties unique to selector (inner object) that are not present in html.Div (outer build wrapper).
        # Creates _action_outputs and _action_inputs for forwarding properties to the underlying selector.
        # Example: "parameter-id.options" is forwarded to "checklist.options".
        # Note: Added in pre_build for consistency with Filter, but could move to the initialization phase.
        if selector_inner_component_properties := getattr(self.selector, "_inner_component_properties", None):
            self._selector_properties = set(selector_inner_component_properties) - set(html.Div().available_properties)

        # Check model_fields_set (not falsiness) so an explicit `selector=X(actions=None)` or `selector=X(actions=[])`
        # is honored as "do nothing on selector change" rather than being replaced by the default. The parameter
        # value is still applied whenever its targets are refreshed by something else (e.g. a Button running
        # update_targets).
        if "actions" not in self.selector.model_fields_set:
            from vizro.models import Filter

            page_dynamic_filters = [
                filter
                for filter in cast(
                    Iterable[Filter], model_manager._get_models(Filter, root_model=model_manager._get_model_page(self))
                )
                if filter._dynamic
            ]

            filter_targets: set[ModelID] = set()

            # Extend parameter targets with dynamic filters linked to the same figure.
            # Also, include dynamic filter targets to ensure that the new filter options are correctly calculated. This
            # also ensures that the dynamic filter target is updated which is necessary if the filter value changes.
            for figure in self.targets:
                figure_id, figure_arg = figure.split(".", 1)
                if figure_arg.startswith("data_frame"):
                    for filter in page_dynamic_filters:
                        if figure_id in filter.targets:
                            filter_targets.add(filter.id)
                            filter_targets |= set(filter.targets)

            # Extending `self.targets` with `filter_targets` instead of redefining it to avoid triggering the
            # pydantic validator like `check_dot_notation` on the `self.targets` again.
            # We do the update to ensure that `self.targets` is consistent with the target ids passed to update_targets.
            self.targets.extend(list(filter_targets))
            targets_ids = [target.partition(".")[0] for target in self.targets]

            build_control_sync_actions(
                selector=self.selector,
                targeted_controls=targeted_controls,
                update_targets_id=f"{PARAMETER_ACTION_PREFIX}_{self.id}",
                update_targets=targets_ids,
            )

    @_log_call
    def build(self):
        # Wrap the selector in a Div so that the "guard" component can be added.
        selector_build_obj = html.Div(children=[self.selector.build()])

        # Add the guard component and set it to False. Let clientside callbacks to update it to True when needed.
        # For example when the parameter value comes from the URL or when reset button is clicked.
        selector_build_obj.children.append(dcc.Store(id=f"{self.selector.id}_guard_actions_chain", data=False))

        return html.Div(id=self.id, children=selector_build_obj, hidden=not self.visible)
