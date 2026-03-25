from __future__ import annotations

from typing import Annotated, Any, Literal

import dash_bootstrap_components as dbc
from dash import html
from pydantic import AfterValidator, BeforeValidator, Field, conlist
from pydantic.json_schema import SkipJsonSchema

from vizro.models import Tooltip, VizroBaseModel
from vizro.models._models_utils import (
    _all_hidden,
    _log_call,
    warn_description_without_title,
)
from vizro.models._tooltip import coerce_str_to_tooltip
from vizro.models.types import ControlType, _IdProperty


class ControlGroup(VizroBaseModel):
    """Container to group together a set of controls.

    Abstract: Usage documentation
        [How to use ControlGroup](../user-guides/controls.md/#add-controlgroup)

    Example:
        ```python
        import vizro.models as vm

        (
            vm.ControlGroup(
                title="Control group title",
                controls=[vm.Filter(column="species"), vm.Filter(column="sepal_length")],
            ),
        )
        ```

    """

    type: Literal["control_group"] = "control_group"
    controls: conlist(ControlType, min_length=1)  # type: ignore[valid-type]
    title: str = Field(default="", description="Title of the control group.")
    # TODO: ideally description would have json_schema_input_type=str | Tooltip attached to the BeforeValidator,
    #  but this requires pydantic >= 2.9.
    description: Annotated[
        Tooltip | None,
        BeforeValidator(coerce_str_to_tooltip),
        AfterValidator(warn_description_without_title),
        Field(
            default=None,
            description="""Optional markdown string that adds an icon next to the title.
            Hovering over the icon shows a tooltip with the provided description.""",
        ),
    ]
    extra: SkipJsonSchema[
        Annotated[
            dict[str, Any],
            Field(
                default={},
                description="""Extra keyword arguments that are passed to `dbc.Container` and overwrite any
    defaults chosen by the Vizro team. This may have unexpected behavior.
    Visit the [dbc documentation](https://www.dash-bootstrap-components.com/docs/components/layout/)
    to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
    underlying component may change in the future.""",
            ),
        ]
    ]

    @property
    def _action_outputs(self) -> dict[str, _IdProperty]:
        return {
            **({"title": f"{self.id}_title.children"} if self.title else {}),
            **({"description": f"{self.description.id}-text.children"} if self.description else {}),
        }

    @_log_call
    def build(self):
        defaults = {
            "id": self.id,
            "children": [
                self._build_container_title() if self.title else None,
                self._build_control_panel(),
            ],
            "fluid": True,
            "className": "control-group-panel",
        }

        return dbc.Container(**(defaults | self.extra))

    def _build_container_title(self):
        """Builds and returns the control group title."""
        description = self.description.build().children if self.description is not None else [None]

        title_content = [
            html.Div(
                [html.Span(id=f"{self.id}_title", children=self.title), *description], className="inner-container-title"
            )
        ]

        return html.H3(
            children=title_content,
            className="control-group-title",
            id=f"{self.id}_title_content",
        )

    def _build_control_panel(self):
        controls_content = [control.build() for control in self.controls]
        return html.Div(
            id=f"{self.id}-control-panel",
            children=controls_content,
            className="control-group",
            hidden=_all_hidden(controls_content),
        )
