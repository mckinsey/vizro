from __future__ import annotations

from collections.abc import Iterable
from typing import Annotated, Any, Literal, cast

import dash_bootstrap_components as dbc
from dash import ClientsideFunction, Input, Output, State, clientside_callback, html
from pydantic import AfterValidator, BeforeValidator, Field, conlist, model_validator
from pydantic.json_schema import SkipJsonSchema
from pydantic_core.core_schema import ValidationInfo

from vizro.managers import model_manager
from vizro.models import Tooltip, VizroBaseModel
from vizro.models._grid import set_layout
from vizro.models._models_utils import (
    _all_hidden,
    _build_inner_layout,
    _log_call,
    check_captured_callable_model,
    warn_description_without_title,
)
from vizro.models._tooltip import coerce_str_to_tooltip
from vizro.models.types import ComponentType, ControlType, LayoutType, _IdProperty


# TODO: this could be done with default_factory once we bump to pydantic>=2.10.0.
def set_variant(variant: Literal["plain", "filled", "outlined"] | None, info: ValidationInfo):
    if variant is not None:
        return variant
    return "plain" if info.data["collapsed"] is None else "outlined"


class ControlGroup(VizroBaseModel):
    """Container to group together a set of controls.

    Abstract: Usage documentation
        [How to use containers](../user-guides/container.md)

    """

    type: Literal["control_group"] = "control_group"
    title: str = Field(default="", description="Title of the `Container`")
    collapsed: bool | None = Field(
        default=None,
        description="Boolean flag that determines whether the container is collapsed on initial load. "
        "Set to `True` for a collapsed state, `False` for an expanded state. "
        "Defaults to `None`, meaning the container is not collapsible.",
    )
    variant: Annotated[
        Literal["plain", "filled", "outlined"] | None,
        AfterValidator(set_variant),
        Field(
            default=None,
            description="Predefined styles to choose from. Options are `plain`, `filled` or `outlined`."
            "Defaults to `plain` (or `outlined` for collapsible container). ",
            validate_default=True,
        ),
    ]
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
    controls: list[ControlType] = []
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

    @model_validator(mode="after")
    def _validate_title_if_collapsed(self):
        if self.collapsed is not None and not self.title:
            raise ValueError("`Container` must have a `title` explicitly set when `collapsed` is not None.")
        return self

    @property
    def _action_outputs(self) -> dict[str, _IdProperty]:
        return {
            **({"title": f"{self.id}_title.children"} if self.title else {}),
            **({"description": f"{self.description.id}-text.children"} if self.description else {}),
        }

    @_log_call
    def pre_build(self):
        from vizro.models import Filter, Parameter

        # Mark controls under this container as `_in_container`. Note this relies on the fact that filters are pre-built
        # upfront in Vizro._pre_build. Otherwise, control.selector might not be set.
        # Use "_get_models" instead of "for control in self.controls" to handle nested custom controls.
        # Use root_model=self.controls so only its own self.controls are marked, not these nested under self.components.
        for control in cast(
            Iterable[ControlType], model_manager._get_models(model_type=(Filter, Parameter), root_model=self.controls)
        ):
            control.selector._in_container = True

    @_log_call
    def build(self):
        if self.collapsed is not None:
            clientside_callback(
                ClientsideFunction(namespace="container", function_name="collapse_container"),
                output=[
                    Output(f"{self.id}_collapse", "is_open"),
                    Output(f"{self.id}_icon", "style"),
                    Output(f"{self.id}_tooltip", "children"),
                ],
                inputs=[Input(f"{self.id}_title_content", "n_clicks"), State(f"{self.id}_collapse", "is_open")],
                prevent_initial_call=True,
                hidden=True,
            )

        variants = {"plain": "", "filled": "bg-container p-3", "outlined": "border p-3"}

        defaults = {
            "id": self.id,
            "children": [
                self._build_container_title() if self.title else None,
                self._build_control_panel() if self.controls else None,
                self._build_container(),
            ],
            "fluid": True,
            "class_name": variants[self.variant],  # type: ignore[index]
        }

        return dbc.Container(**(defaults | self.extra))

    def _build_container(self):
        """Returns a collapsible container based on the `collapsed` state.

        If `collapsed` is `None`, returns a non-collapsible container.
        Otherwise, returns a collapsible container with visibility controlled by the `collapsed` flag.
        """
        container = html.Div(children=[])
        if self.collapsed is None:
            return container

        return dbc.Collapse(
            id=f"{self.id}_collapse",
            children=container,
            is_open=not self.collapsed,
            className="collapsible-container",
            key=self.id,
        )

    def _build_container_title(self):
        """Builds and returns the container title, including an optional icon and tooltip if collapsed."""
        description = self.description.build().children if self.description is not None else [None]

        title_content = [
            html.Div(
                [html.Span(id=f"{self.id}_title", children=self.title), *description], className="inner-container-title"
            )
        ]

        if self.collapsed is not None:
            # collapse_container is not run when page is initially loaded, so we set the content correctly conditional
            # on self.collapsed upfront. This prevents the up/down arrow rotating on in initial load.
            title_content.extend(
                [
                    html.Span(
                        "keyboard_arrow_down" if self.collapsed else "keyboard_arrow_up",
                        className="material-symbols-outlined",
                        id=f"{self.id}_icon",
                    ),
                    dbc.Tooltip(
                        id=f"{self.id}_tooltip",
                        children="Show Content" if self.collapsed else "Hide Content",
                        target=f"{self.id}_icon",
                    ),
                ]
            )

        return html.H3(
            children=title_content,
            className="container-title-collapse" if self.collapsed is not None else "container-title",
            id=f"{self.id}_title_content",
        )

    def _build_control_panel(self):
        controls_content = [control.build() for control in self.controls]
        return html.Div(
            id=f"{self.id}-control-panel",
            children=controls_content,
            className="container-controls-panel",
            hidden=_all_hidden(controls_content),
        )
