from typing import Annotated, Any, Literal

from dash import dcc
from pydantic import Field
from pydantic.json_schema import SkipJsonSchema

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call


class Markdown(VizroBaseModel):
    type: Literal["markdown"] = "markdown"
    text: str = Field(
        description="Markdown string to create card title/text that should adhere to the CommonMark Spec."
    )
    extra: SkipJsonSchema[
        Annotated[
            dict[str, Any],
            Field(
                default={},
                description="""Extra keyword arguments that are passed to `dcc.Markdown` and overwrite any
            defaults chosen by the Vizro team. This may have unexpected behavior.
            Visit the [dcc documentation](https://dash.plotly.com/dash-core-components/markdown/)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
            underlying component may change in the future. Defaults to `{}`.""",
            ),
        ]
    ]

    @_log_call
    def build(self):
        """Returns a markdown component with an optional classname."""
        defaults = {
            "id": self.id,
            "children": self.text,
            "dangerously_allow_html": False
        }

        return dcc.Markdown(**(defaults | self.extra))
