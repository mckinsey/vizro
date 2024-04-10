from typing import List, Literal

import dash_bootstrap_components as dbc
from dash import html

try:
    from pydantic.v1 import Field
except ImportError:  # pragma: no cov
    from pydantic import Field

from vizro.models import Action, VizroBaseModel
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._models_utils import _log_call


class TextArea(VizroBaseModel):
    """Multi-line text input component `TextArea`.

    Based on the underlying [`dcc.TextArea`](https://dash.plotly.com/dash-core-components/textarea).

    Args:
        type (Literal["text_area"]): Defaults to `"text_area"`.
        title (str): Title to be displayed. Defaults to `""`.
        placeholder (str): Default text to display in input field. Defaults to `""`.
        actions (Optional[List[Action]]): Defaults to `[]`.

    """

    type: Literal["text_area"] = "text_area"
    # TODO: before making public consider naming this field (or giving an alias) label instead of title
    title: str = Field("", description="Title to be displayed")
    placeholder: str = Field("", description="Default text to display in input field")
    actions: List[Action] = []

    # Re-used validators
    # TODO: Before making public, consider how actions should be triggered and what the default property should be
    # See comment thread: https://github.com/mckinsey/vizro/pull/298#discussion_r1478137654
    _set_actions = _action_validator_factory("value")

    @_log_call
    def build(self):
        return html.Div(
            [
                dbc.Label(self.title, html_for=self.id) if self.title else None,
                dbc.Textarea(
                    id=self.id,
                    placeholder=self.placeholder,
                    persistence=True,
                    persistence_type="session",
                    debounce=True,
                    className="text-area",
                ),
            ],
            className="input-container",
            id=f"{self.id}_outer",
        )
