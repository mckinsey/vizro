from typing import List, Literal, Optional

from dash import dcc, html
from pydantic import Field, PrivateAttr, root_validator, validator

from vizro.models import Action, VizroBaseModel
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._components.form._form_utils import get_options_and_default, validate_options_dict, validate_value
from vizro.models._models_utils import _log_call
from vizro.models.types import OptionsType, SingleValueType


class RadioItems(VizroBaseModel):
    """Categorical single-selector `RadioItems` to be provided to `Filter`.

    Args:
        type (Literal["radio_items"]): Defaults to `"radio_items"`.
        options (OptionsType): See [`OptionsType`][vizro.models.types.OptionsType]. Defaults to `[]`.
        value (Optional[SingleValueType]): See [`SingleValueType`][vizro.models.types.SingleValueType].
            Defaults to `None`.
        title (Optional[str]): Title to be displayed. Defaults to `None`.
        actions (List[Action]): See [`Action`][vizro.models.Action]. Defaults to `[]`.
    """

    type: Literal["radio_items"] = "radio_items"
    options: OptionsType = []  # type: ignore[assignment]
    value: Optional[SingleValueType] = None
    title: Optional[str] = Field(None, description="Title to be displayed")
    actions: List[Action] = []

    # Component properties for actions and interactions
    _input_property: str = PrivateAttr("value")

    # Re-used validators
    _set_actions = _action_validator_factory("value")
    _validate_options = root_validator(allow_reuse=True, pre=True)(validate_options_dict)
    _validate_value = validator("value", allow_reuse=True, always=True)(validate_value)

    @_log_call
    def build(self):
        full_options, default_value = get_options_and_default(options=self.options, multi=False)

        return html.Div(
            [
                html.P(self.title) if self.title else html.Div(hidden=True),
                dcc.RadioItems(
                    id=self.id,
                    options=full_options,
                    value=self.value if self.value is not None else default_value,
                    persistence=True,
                    className="selector_body_radio_items",
                ),
            ],
            className="selector_container",
            id=f"{self.id}_outer",
        )
