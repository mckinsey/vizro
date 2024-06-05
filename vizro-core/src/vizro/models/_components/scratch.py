from typing import Literal, Optional

import dash_bootstrap_components as dbc
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

CLASSNAME_LOOKUP = {
    "text_card": "",
    "nav_card": "card-nav",
    "kpi_card": "kpi-card",
    "kpi_card_ref": "kpi-card-ref",
}


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
                vc.nav_card(text=values["text"], href=values["href"], data_frame=pd.DataFrame())
                if values["href"]
                else vc.text_card(text=values["text"], data_frame=pd.DataFrame())
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
        # LQ: Don't really like this - is there a better way to do this? I need to provide different classNames to the outer
        # dbc.Card based on the CapturedCallable provided. This is a bit hacky.
        function_name = self.figure._function.__name__

        # LQ: Previously discussed to insert dbc.Card directly here and provide self.id to the outer container.
        # However, this can affect several custom actions that rely on the id being previously provided to the inner
        # text component instead of the outer card component. Shall we keep as is or pass the id through the relevant inner
        # components? The last would require to provide an id argument to each CapturedCallable, which is also not optimal.
        return dcc.Loading(
            dbc.Card(self.__call__(), id=self.id, className=CLASSNAME_LOOKUP[function_name]),
            color="grey",
            parent_className="loading-container",
        )
