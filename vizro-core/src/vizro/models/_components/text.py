from typing import Annotated, Any, Literal

from dash import dcc
from pydantic import Field
from pydantic.json_schema import SkipJsonSchema

from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models.types import _IdProperty


class Text(VizroBaseModel):
    """Creates a text component based on Markdown syntax.

    Args:
        type (Literal["text"]): Defaults to `"text"`.
        text (str): Markdown string to create text that should adhere to the CommonMark Spec.
        extra (Optional[dict[str, Any]]): Extra keyword arguments that are passed to `dcc.Markdown` and overwrite any
            defaults chosen by the Vizro team. This may have unexpected behavior.
            Visit the [dcc documentation](https://dash.plotly.com/dash-core-components/markdown/)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
            underlying component may change in the future. Defaults to `{}`.

    """

    type: Literal["text"] = "text"
    text: str = Field(
        description="Markdown string to create text that should adhere to the CommonMark Spec.",
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

    @property
    def _action_outputs(self) -> dict[str, _IdProperty]:
        return {
            "__default__": f"{self.id}.children",
            "text": f"{self.id}.children",
        }

    @_log_call
    def build(self):
        defaults = {
            "id": self.id,
            "children": self.text,
            "dangerously_allow_html": False,
        }

        return dcc.Markdown(**(defaults | self.extra))
