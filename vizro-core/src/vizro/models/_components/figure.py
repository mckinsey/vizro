from typing import Annotated, Literal

from dash import dcc, html
from pydantic import AfterValidator, Field, JsonValue, field_validator, model_validator
from pydantic.json_schema import SkipJsonSchema

from vizro.managers import data_manager
from vizro.models import VizroBaseModel
from vizro.models._components._components_utils import _process_callable_data_frame
from vizro.models._models_utils import _log_call, make_actions_chain
from vizro.models.types import ActionsType, CapturedCallable, _IdProperty, _validate_captured_callable


class Figure(VizroBaseModel):
    """Object that is reactive to controls, for example a KPI card.

    Abstract: Usage documentation
        [How to use figures](../user-guides/figure.md)

    """

    type: Literal["figure"] = "figure"
    figure: Annotated[
        SkipJsonSchema[CapturedCallable],
        AfterValidator(_process_callable_data_frame),
        Field(
            json_schema_extra={"mode": "figure", "import_path": "vizro.figures"},
            description="Function that returns a figure-like object.",
        ),
    ]
    actions: ActionsType = []

    # _validate_figure = field_validator("figure", mode="before")(_validate_captured_callable)

    @model_validator(mode="after")
    def _make_actions_chain(self):
        return make_actions_chain(self)

    @property
    def _action_triggers(self) -> dict[str, _IdProperty]:
        return {"__default__": f"{self.id}.n_clicks"}

    @property
    def _action_outputs(self) -> dict[str, _IdProperty]:
        return {
            "__default__": f"{self.id}.children",
            "figure": f"{self.id}.children",
        }

    @staticmethod
    def _get_value_from_trigger(value: JsonValue, trigger: int) -> JsonValue:
        """Return the given `value` without modification."""
        return value

    def __call__(self, **kwargs):
        # This default value is not actually used anywhere at the moment since __call__ is always used with data_frame
        # specified. It's here since we want to use __call__ without arguments more in future.
        # If the functionality of process_callable_data_frame moves to CapturedCallable then this would move there too.
        if "data_frame" not in kwargs:
            kwargs["data_frame"] = data_manager[self["data_frame"]].load()
        figure = self.figure(**kwargs)
        return figure

    def __getitem__(self, arg_name: str):
        # pydantic discriminated union validation seems to try Figure["type"], which throws an error unless we
        # explicitly redirect it to the correct attribute.
        if self.figure:
            if arg_name == "type":
                return self.type
            return self.figure[arg_name]

    @_log_call
    def build(self):
        return dcc.Loading(
            # Refer to the vm.AgGrid build method for details on why we return the
            # html.Div(id=self.id) instead of actual figure object with the original data_frame.
            # Optimally, we would like to provide id=self.id directly here such that we can target the CSS
            # of the children via ID as well, but the `id` doesn't seem to be passed on to the loading component.
            # This limitation is handled with this PR -> https://github.com/plotly/dash/pull/2888.
            # The PR is merged but is not released yet. Once it is released, we can try to refactor the following code.
            # In the meantime, we are adding an extra html.div here.
            html.Div(id=self.id, className="figure-container is-clickable" if self.actions else "figure-container"),
            color="grey",
            parent_className="loading-container",
            overlay_style={"visibility": "visible", "opacity": 0.3},
        )
