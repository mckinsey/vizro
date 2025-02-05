from typing import Annotated, Literal, Optional

import dash_bootstrap_components as dbc
from dash import html
from pydantic import AfterValidator, Field, PrivateAttr, model_validator
from pydantic.functional_serializers import PlainSerializer

from vizro.models import Action, VizroBaseModel
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._components.form._form_utils import get_options_and_default, validate_options_dict, validate_value
from vizro.models._models_utils import _log_call
from vizro.models.types import MultiValueType, OptionsType


class Checklist(VizroBaseModel):
    """Categorical multi-option selector `Checklist`.

    Can be provided to [`Filter`][vizro.models.Filter] or
    [`Parameter`][vizro.models.Parameter]. Based on the underlying
    [`dcc.Checklist`](https://dash.plotly.com/dash-core-components/checklist).

    Args:
        type (Literal["checklist"]): Defaults to `"checklist"`.
        options (OptionsType): See [`OptionsType`][vizro.models.types.OptionsType]. Defaults to `[]`.
        value (Optional[MultiValueType]): See [`MultiValueType`][vizro.models.types.MultiValueType]. Defaults to `None`.
        title (str): Title to be displayed. Defaults to `""`.
        actions (list[Action]): See [`Action`][vizro.models.Action]. Defaults to `[]`.

    """

    type: Literal["checklist"] = "checklist"
    options: OptionsType = []
    value: Annotated[
        Optional[MultiValueType], AfterValidator(validate_value), Field(default=None, validate_default=True)
    ]
    title: str = Field(default="", description="Title to be displayed")
    actions: Annotated[
        list[Action],
        AfterValidator(_action_validator_factory("value")),
        PlainSerializer(lambda x: x[0].actions),
        Field(default=[]),
    ]

    _dynamic: bool = PrivateAttr(False)

    # Component properties for actions and interactions
    _input_property: str = PrivateAttr("value")

    # Reused validators
    _validate_options = model_validator(mode="before")(validate_options_dict)

    def __call__(self, options):
        full_options, default_value = get_options_and_default(options=options, multi=True)

        return html.Fieldset(
            children=[
                html.Legend(children=self.title, className="form-label") if self.title else None,
                dbc.Checklist(
                    id=self.id,
                    options=full_options,
                    value=self.value if self.value is not None else [default_value],
                    persistence=True,
                    persistence_type="session",
                ),
            ]
        )

    def _build_dynamic_placeholder(self):
        if self.value is None:
            _, default_value = get_options_and_default(self.options, multi=True)
            self.value = [default_value]  # type: ignore[assignment]

        return self.__call__(self.options)

    @_log_call
    def build(self):
        return self._build_dynamic_placeholder() if self._dynamic else self.__call__(self.options)
