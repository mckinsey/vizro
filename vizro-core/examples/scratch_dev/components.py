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
    # TODO[mypy], see: https://github.com/pydantic/pydantic/issues/156 for components field

    @_log_call
    def build(self):
        self.layout = cast(
            Layout,  # cannot actually be None if you check components and layout field together
            self.layout,
        )

        components_container = self.layout.build()
        for component_idx, component in enumerate(self.components):
            components_container[f"{self.layout.id}_{component_idx}"].children = component.build()

        clientside_callback(
            """
            (n_clicks) => {
               if (n_clicks % 2 === 1) {
                return [true, {transform: "rotate(180deg)", transition: "transform 0.35s ease-in-out"}];
            } else return [false, {transform: "rotate(0deg)", transition: "transform 0.35s ease-in-out"}];
            }
            """,
            [Output(self.id, "is_open"), Output(f"{self.id}_icon", "style")],
            Input(f"{self.id}_title", "n_clicks"),
        )

        return html.Div(
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
                    children=components_container,
                    is_open=True,
                ),
            ],
            className="bg-container",
        )
