"""Contains custom components used inside the dashboard."""

from typing import Annotated, Literal, cast

import dash_bootstrap_components as dbc
import vizro.models as vm
from dash import Input, Output, clientside_callback, html
from pydantic import BeforeValidator, conlist
from vizro.models import Layout, VizroBaseModel
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
        clientside_callback(
            """
            (n_clicks) => {
                if (!n_clicks) {
                    return dash_clientside.no_update;
                }

                const isOpen = n_clicks % 2 === 1;
                const style = {
                    transform: isOpen ? "rotate(180deg)" : "rotate(0deg)",
                    transition: "transform 0.35s ease-in-out"
                };

                return [isOpen, style];
            }
            """,
            [Output(self.id, "is_open"), Output(f"{self.id}_icon", "style")],
            Input(f"{self.id}_title", "n_clicks"),
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
                ),
            ],
            fluid=True,
            className="bg-container",
        )
