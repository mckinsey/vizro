from collections.abc import Iterable
from typing import Annotated, Literal, cast

from pydantic import AfterValidator, Field

from vizro._constants import PARAMETER_ACTION_PREFIX
from vizro.actions._parameter_action import _parameter
from vizro.managers import model_manager
from vizro.models import VizroBaseModel
from vizro.models._components.form import Checklist, DatePicker, Dropdown, RadioItems, RangeSlider, Slider
from vizro.models._controls._controls_utils import check_control_targets, set_container_control_default
from vizro.models._models_utils import _log_call
from vizro.models.types import ModelID, SelectorType


def check_dot_notation(target):
    if "." not in target:
        raise ValueError(
            f"Invalid target {target}. Targets must be supplied in the form <target_component>.<target_argument>"
        )
    elif target.split(".")[1] == "figure":
        raise ValueError(
            f"Invalid target {target}. Targets must be supplied in the form <target_component>.<target_argument>. "
            "Arguments of the CapturedCallable function can be targeted directly, and not via <.figure.>."
        )
    return target


def check_data_frame_as_target_argument(target):
    targeted_argument = target.split(".", 1)[1]
    if targeted_argument.startswith("data_frame") and targeted_argument.count(".") != 1:
        raise ValueError(
            f"Invalid target {target}. 'data_frame' target must be supplied in the form "
            "<target_component>.data_frame.<dynamic_data_argument>"
        )
    # TODO: Add validation: Make sure the target data_frame is _DynamicData.
    return target


def check_duplicate_parameter_target(targets):
    all_targets = targets.copy()
    for param in cast(Iterable[Parameter], model_manager._get_models(Parameter)):
        all_targets.extend(param.targets)
    duplicate_targets = {item for item in all_targets if all_targets.count(item) > 1}
    if duplicate_targets:
        raise ValueError(f"Duplicate parameter targets {duplicate_targets} found.")
    return targets


class Parameter(VizroBaseModel):
    """Alter the arguments supplied to any `targets` on the [`Page`][vizro.models.Page].

    Examples:
        >>> Parameter(targets=["scatter.x"], selector=Slider(min=0, max=1, default=0.8, title="Bubble opacity"))

    Args:
        type (Literal["parameter"]): Defaults to `"parameter"`.
        targets (list[str]): Targets in the form of `<target_component>.<target_argument>`.
        selector (SelectorType): See [SelectorType][vizro.models.types.SelectorType]. Converts selector value
            `"NONE"` into `None` to allow optional parameters.

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

    @_log_call
    def pre_build(self):
        check_control_targets(control=self)
        set_container_control_default(control=self)
        self._check_numerical_and_temporal_selectors_values()
        self._check_categorical_selectors_options()
        self._set_selector_title()
        self._set_actions()

    @_log_call
    def build(self):
        return self.selector.build()

    def _check_numerical_and_temporal_selectors_values(self):
        if isinstance(self.selector, (Slider, RangeSlider, DatePicker)):
            if self.selector.min is None or self.selector.max is None:
                raise TypeError(
                    f"{self.selector.type} requires the arguments 'min' and 'max' when used within Parameter."
                )

    def _check_categorical_selectors_options(self):
        if isinstance(self.selector, (Checklist, Dropdown, RadioItems)) and not self.selector.options:
            raise TypeError(f"{self.selector.type} requires the argument 'options' when used within Parameter.")

    def _set_selector_title(self):
        if not self.selector.title:
            self.selector.title = ", ".join({target.rsplit(".")[-1] for target in self.targets})

    def _set_actions(self):
        from vizro.models import Filter

        if not self.selector.actions:
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
            # We do the update to ensure that `self.targets` is consistent with the targets passed to `_parameter`.
            self.targets.extend(list(filter_targets))

            self.selector.actions = [_parameter(id=f"{PARAMETER_ACTION_PREFIX}_{self.id}", targets=self.targets)]
