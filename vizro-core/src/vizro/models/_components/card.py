from typing import Literal, Optional

import pandas as pd
from dash import dcc

try:
    from pydantic.v1 import Field, PrivateAttr, validator
except ImportError:  # pragma: no cov
    from pydantic import Field, PrivateAttr, validator

import vizro.cards as vc
from vizro.managers import data_manager
from vizro.models import VizroBaseModel
from vizro.models._components._components_utils import _callable_mode_validator_factory, _process_callable_data_frame
from vizro.models._models_utils import _log_call
from vizro.models.types import CapturedCallable


class Card(VizroBaseModel):
    """Creates a card object to be displayed on dashboard.

    Args:
        type (Literal["card"]): Defaults to `"card"`.
        text (str): Markdown string to create card title/text that should adhere to the CommonMark Spec.
        href (str): URL (relative or absolute) to navigate to. If not provided the Card serves as a text card
            only. Defaults to `""`.
        figure (CapturedCallable): Card like object to be displayed. Defaults to `None`. For more information see
            available card callables in [`vizro.cards`](vizro.cards).

    """

    type: Literal["card"] = "card"
    text: str = Field("", description="Markdown string to create card text that should adhere to the CommonMark Spec.")
    href: str = Field(
        "",
        description="URL (relative or absolute) to navigate to. If not provided the Card serves as a text card only.",
    )
    figure: Optional[CapturedCallable] = Field(
        None, import_path=vc, description="Dynamic card function to be visualized on dashboard."
    )

    # Component properties for actions and interactions
    _output_component_property: str = PrivateAttr("children")

    # Validators
    @validator("figure")
    def validate_figure(cls, figure, values):
        if figure is None:
            return (
                vc.nav_card(text=values["text"], href=values["href"], data_frame=pd.DataFrame(), id=values["id"])
                if values["href"]
                else vc.text_card(text=values["text"], data_frame=pd.DataFrame(), id=values["id"])
            )
        return figure

    _validate_callable_mode = _callable_mode_validator_factory("card")
    _validate_callable = validator("figure", allow_reuse=True, always=True)(_process_callable_data_frame)

    def __call__(self, **kwargs):
        kwargs.setdefault("data_frame", data_manager[self["data_frame"]].load())
        figure = self.figure(**kwargs) if self.figure else None
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
        # LQ: Normally we insert the self.id in the outer html.Div. In the context of the card, it doesn't make sense
        # to have the id on the outer div, as it's not the responsive sub-component. Instead the id needs to be passed
        # on through the child. But this now requires an `id` argument in the CapturedCallable which is not ideal.
        # Any ideas on how to solve this?
        return dcc.Loading(self.__call__(id=self.id), color="grey", parent_className="loading-container")
