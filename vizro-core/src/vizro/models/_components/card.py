import logging
from typing import Literal, Optional

import dash_bootstrap_components as dbc
from dash import dcc, get_relative_path, html
from pydantic import Field, PrivateAttr, validator

from vizro.managers import data_manager
from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models.types import CapturedCallable

logger = logging.getLogger(__name__)


class Card(VizroBaseModel):
    """Creates a card utilizing `dcc.Markdown` as title and text component.

    Args:
        type (Literal["card"]): Defaults to `"card"`.
        text (str): Markdown string to create card title/text that should adhere to the CommonMark Spec.
        href (Optional[str]): URL (relative or absolute) to navigate to. If not provided the Card serves as a text card
            only. Defaults to None.
    """

    type: Literal["card"] = "card"
    text: CapturedCallable = Field(
        ..., description="Markdown string to create card title/text that should adhere to the CommonMark Spec."
    )
    href: Optional[str] = Field(
        None,
        description="URL (relative or absolute) to navigate to. If not provided the Card serves as a text card only.",
    )

    _output_property = PrivateAttr("children")

    def __call__(self, **kwargs):
        kwargs.setdefault("data_frame", data_manager._get_component_data(self.id))  # type: ignore[arg-type]
        return self.text(**kwargs)

    @validator("text")
    def process_component_data_frame(cls, text, values):
        data_frame = text["data_frame"]

        # Enable running "iris" from the Python API and specification of "data_frame": "iris" through JSON.
        # In these cases, data already exists in the data manager and just needs to be linked to the component.
        if isinstance(data_frame, str):
            data_manager._add_component(values["id"], data_frame)
            return text

        # Standard case for df: pd.DataFrame.
        # Extract dataframe from the captured function and put it into the data manager.
        dataset_name = str(id(data_frame))

        logger.debug("Adding data to data manager for text with id %s", values["id"])
        # If the dataset already exists in the data manager then it's not a problem, it just means that we don't need
        # to duplicate it. Just log the exception for debugging purposes.
        try:
            data_manager[dataset_name] = data_frame
        except ValueError as exc:
            logger.debug(exc)

        data_manager._add_component(values["id"], dataset_name)

        # No need to keep the data in the captured function any more so remove it to save memory.
        del text["data_frame"]
        return text

    @_log_call
    def build(self):
        text = dcc.Markdown(self(), className="card_text",
                            dangerously_allow_html=False, id=self.id)
        button = (
            html.Div(
                dbc.Button(
                    href=get_relative_path(self.href) if self.href.startswith("/") else self.href,
                    className="card_button",
                ),
                className="button_container",
            )
            if self.href
            else None
        )
        card_container = "nav_card_container" if self.href else "card_container"

        return html.Div(
            [text, button],
            className=card_container,
            id=f"{self.id}_outer",
        )
