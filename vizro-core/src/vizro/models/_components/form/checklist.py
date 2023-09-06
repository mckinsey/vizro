from typing import List, Literal, Optional

from dash import dcc, html
from pydantic import Field

from vizro.models import Action, VizroBaseModel
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._components.form._form_utils import get_options_and_default
from vizro.models._models_utils import _log_call
from vizro.models.types import MultiValueType, OptionsType


class Checklist(VizroBaseModel):
    """Categorical multi-selector `Checklist` to be provided to [`Filter`][vizro.models.Filter].

    Args:
        type (Literal["checklist"]): Defaults to `"checklist"`.
        options (OptionsType): See [`OptionsType`][vizro.models.types.OptionsType]. Defaults to `[]`.
        value (Optional[MultiValueType]): See [`MultiValueType`][vizro.models.types.MultiValueType]. Defaults to `None`.
        title (Optional[str]): Title to be displayed. Defaults to `None`.
        actions (List[Action]): See [`Action`][vizro.models.Action]. Defaults to `[]`.
    """

    type: Literal["checklist"] = "checklist"
    options: OptionsType = Field([])
    value: Optional[MultiValueType] = Field(None)
    title: Optional[str] = Field(None, description="Title to be displayed")
    actions: List[Action] = []

    # validator
    set_actions = _action_validator_factory("value")  # type: ignore[pydantic-field]

    # This should be put back if we expose multi at top level of Filter.
    # It will ensure there's an explicit error message  if someone calls with multi=False.
    # multi: Literal[True] = True
    @_log_call
    def build(self):
        full_options, default_value = get_options_and_default(options=self.options, multi=True)

        return html.Div(
            [
                html.P(self.title, id="checklist_title") if self.title else None,
                dcc.Checklist(
                    id=self.id,
                    options=full_options,
                    value=self.value if self.value is not None else [default_value],
                    className="selector_body_checklist",
                    persistence=True,
                ),
            ],
            className="selector_container",
        )
