from typing import Literal, Optional

import pandas as pd
from dash import dcc, html

try:
    from pydantic.v1 import Field, PrivateAttr, validator
except ImportError:  # pragma: no cov
    from pydantic import Field, PrivateAttr, validator

import vizro.figures as vc
from vizro.managers import data_manager
from vizro.models import VizroBaseModel
from vizro.models._components._components_utils import _callable_mode_validator_factory, _process_callable_data_frame
from vizro.models._models_utils import _log_call
from vizro.models.types import CapturedCallable

# components, dynamic components, reactive components, reactive
# ReactiveComponent, Reactive, Figure, ReactiveFigure, ReactiveObject, ReactiveHTML, ReactiveDiv

class Figure(VizroBaseModel):
    """Creates a card object to be displayed on dashboard.

    Args:
        type (Literal["card"]): Defaults to `"card"`.
        figure (CapturedCallable): Card like object to be displayed. Defaults to `None`. For more information see
            available card callables in [`vizro.figures`](vizro.figures).

    """
    type: Literal["figure"] = "figure"
    figure: Optional[CapturedCallable] = Field(
        None, import_path=vf, description="Dynamic card function to be visualized on dashboard."
    )

    # Component properties for actions and interactions
    _output_component_property: str = PrivateAttr("children")

    # Validators
    _validate_callable_mode = _callable_mode_validator_factory("reactive_figure")
    _validate_callable = validator("figure", allow_reuse=True, always=True)(_process_callable_data_frame)

    def __call__(self, **kwargs):
        kwargs.setdefault("data_frame", data_manager[self["data_frame"]].load())
        figure = self.figure(**kwargs)
        return figure

    def __getitem__(self, arg_name: str):
        # pydantic discriminated union validation seems to try Graph["type"], which throws an error unless we
        # explicitly redirect it to the correct attribute.
        if self.figure:
            if arg_name == "type":
                return self.type
            return self.figure[arg_name]

    @_log_call
    def build(self):
        return dcc.Loading(
            self.__call__(),
            color="grey",
            parent_className="loading-container",
            overlay_style={"visibility": "visible", "opacity": 0.3},
            id=self.id
        )
