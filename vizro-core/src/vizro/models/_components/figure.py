from typing import Literal, Optional

from dash import dcc

try:
    from pydantic.v1 import Field, PrivateAttr, validator
except ImportError:  # pragma: no cov
    from pydantic import Field, PrivateAttr, validator

import vizro.figures as vf
from vizro.managers import data_manager
from vizro.models import VizroBaseModel
from vizro.models._components._components_utils import _callable_mode_validator_factory, _process_callable_data_frame
from vizro.models._models_utils import _log_call
from vizro.models.types import CapturedCallable


# TODO: Align on naming - really difficult one:
# ReactiveComponent, Reactive, Figure, ReactiveFigure, ReactiveObject, ReactiveHTML, ReactiveDiv, any other ideas?
class Figure(VizroBaseModel):
    """Creates a figure-like object that can be displayed in the dashboard and is reactive to controls.

    Args:
        type (Literal["figure"]): Defaults to `"figure"`.
        figure (CapturedCallable): Figure like object to be displayed. Defaults to `None`. For more information see
            available figure callables in [`vizro.figures`](vizro.figures).

    """

    type: Literal["figure"] = "figure"
    figure: Optional[CapturedCallable] = Field(
        None,
        import_path=vf,
        description="Function that returns a figure-like object to be visualized in the dashboard.",
    )

    # Component properties for actions and interactions
    _output_component_property: str = PrivateAttr("children")

    # Validators
    _validate_callable_mode = _callable_mode_validator_factory("figure")
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
            id=self.id,
        )
