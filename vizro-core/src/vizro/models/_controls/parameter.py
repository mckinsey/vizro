from typing import List, Literal

try:
    from pydantic.v1 import Field, validator
except ImportError:  # pragma: no cov
    from pydantic import Field, validator

from vizro._constants import PARAMETER_ACTION_PREFIX
from vizro.actions import _parameter
from vizro.managers import model_manager
from vizro.models import Action, VizroBaseModel
from vizro.models._components.form import Checklist, DatePicker, Dropdown, RadioItems, RangeSlider, Slider
from vizro.models._models_utils import _log_call
from vizro.models.types import SelectorType


class Parameter(VizroBaseModel):
    """Alter the arguments supplied to any `targets` on the [`Page`][vizro.models.Page].

    Examples:
        >>> print(repr(Parameter(
        >>>    targets=["scatter.x"], selector=Slider(min=0, max=1, default=0.8, title="Bubble opacity"))))

    Args:
        type (Literal["parameter"]): Defaults to `"parameter"`.
        targets (List[str]): Targets in the form of `<target_component>.<target_argument>`.
        selector (SelectorType): See [SelectorType][vizro.models.types.SelectorType]. Converts selector value
            `"NONE"` into `None` to allow optional parameters.

    """

    type: Literal["parameter"] = "parameter"
    targets: List[str] = Field(..., description="Targets in the form of `<target_component>.<target_argument>`.")
    selector: SelectorType

    @validator("targets", each_item=True)
    def check_dot_notation(cls, target):
        if "." not in target:
            raise ValueError(
                f"Invalid target {target}. Targets must be supplied in the from of "
                "<target_component>.<target_argument>"
            )
        return target

    @validator("targets", each_item=True)
    def check_target_present(cls, target):
        target_id = target.split(".")[0]
        if target_id not in model_manager:
            raise ValueError(f"Target {target_id} not found in model_manager.")
        return target

    @validator("targets")
    def check_duplicate_parameter_target(cls, targets):
        all_targets = targets.copy()
        for _, param in model_manager._items_with_type(Parameter):
            all_targets.extend(param.targets)
        duplicate_targets = {item for item in all_targets if all_targets.count(item) > 1}
        if duplicate_targets:
            raise ValueError(f"Duplicate parameter targets {duplicate_targets} found.")
        return targets

    @_log_call
    def pre_build(self):
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
        if not self.selector.actions:
            self.selector.actions = [
                Action(id=f"{PARAMETER_ACTION_PREFIX}_{self.id}", function=_parameter(targets=self.targets))
            ]
