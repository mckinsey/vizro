"""Contains custom components used inside the dashboard."""

from typing import Annotated, Literal

import dash_bootstrap_components as dbc
import vizro.models as vm
from dash import Input, Output, State, clientside_callback, html
from pydantic import BeforeValidator, conlist
from vizro.models import VizroBaseModel
from vizro.models._models_utils import _log_call, check_captured_callable_model
from vizro.models.types import ComponentType


class FlexContainer(VizroBaseModel):
    """Container to group together a set of components on a page.

    Args:
        type (Literal["container"]): Defaults to `"container"`.
        components (list[ComponentType]): See [ComponentType][vizro.models.types.ComponentType]. At least one component
            has to be provided.
        title (str): Title to be displayed.

    """

    type: Literal["flex_container"] = "flex_container"
    # TODO[mypy], see: https://github.com/pydantic/pydantic/issues/156 for components field
    components: conlist(  # type: ignore[valid-type]
        Annotated[ComponentType, BeforeValidator(check_captured_callable_model)],
        min_length=1,
    )

    @_log_call
    def build(self):
        """Returns custom flex container."""
        return html.Div(
            id=self.id, children=[component.build() for component in self.components], className="flex-container"
        )


class CollapsibleContainer(vm.Container):
    """Container to group together a set of components on a page.

    Args:
        type (Literal["collapse_container"]): Defaults to `"collapse_container"`.

    """

    type: Literal["collapse_container"] = "collapse_container"
    is_open: bool = True

    @_log_call
    def build(self):
        """Returns custom collapsible container."""
        clientside_callback(
            """
            (n_clicks, is_open) => {
                if (!n_clicks) {
                    if (is_open) {
                        return [is_open, { transform: "rotate(180deg)", transition: "transform 0.35s ease-in-out"}];
                    }

                    return dash_clientside.no_update;
                }

                return [
                    !is_open,
                    { transform: !is_open ? "rotate(180deg)" : "rotate(0deg)",
                     transition: "transform 0.35s ease-in-out" }
                ];
            }
            """,
            [Output(self.id, "is_open"), Output(f"{self.id}_icon", "style")],
            [Input(f"{self.id}_title", "n_clicks")],
            [State(self.id, "is_open")],
        )

        return dbc.Container(
            children=[
                html.Div(
                    id=f"{self.id}_title",
                    children=[
                        html.H3(self.title, className="container-title"),
                        html.Span("keyboard_arrow_up", className="material-symbols-outlined", id=f"{self.id}_icon"),
                    ],
                    className="collapsible-container-header",
                ),
                dbc.Collapse(
                    id=self.id,
                    children=self._build_inner_layout(),
                    is_open=self.is_open,
                    className="collapsible-container",
                ),
            ],
            fluid=True,
            className="bg-container",
        )
