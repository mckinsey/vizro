from typing import Literal

from dash import dcc, html

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


class Figure(VizroBaseModel):
    """Creates a figure-like object that can be displayed in the dashboard and is reactive to controls.

    Args:
        type (Literal["figure"]): Defaults to `"figure"`.
        figure (CapturedCallable): See [`vizro.figures`][vizro.figures].

    """

    type: Literal["figure"] = "figure"
    figure: CapturedCallable = Field(
        import_path=vf, description="Function that returns a figure-like object to be visualized in the dashboard."
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
        # pydantic discriminated union validation seems to try Figure["type"], which throws an error unless we
        # explicitly redirect it to the correct attribute.
        if self.figure:
            if arg_name == "type":
                return self.type
            return self.figure[arg_name]

    @_log_call
    def build(self):
        return dcc.Loading(
            # Optimally, we would like to provide id=self.id directly here such that we can target the CSS
            # of the children via ID as well, but the `id` doesn't seem  to be passed on to the loading component.
            # I've raised an issue on dash here: https://github.com/plotly/dash/issues/2878
            # In the meantime, we are adding an extra html.div here.
            html.Div(self.__call__(), id=self.id, className="figure-container"),
            color="grey",
            parent_className="loading-container",
            overlay_style={"visibility": "visible", "opacity": 0.3},
        )
