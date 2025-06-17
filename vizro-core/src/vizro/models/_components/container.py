from __future__ import annotations

from typing import Annotated, Any, Literal, Optional

import dash_bootstrap_components as dbc
from dash import ClientsideFunction, Input, Output, State, clientside_callback, html
from pydantic import AfterValidator, BeforeValidator, Field, conlist, model_validator
from pydantic.json_schema import SkipJsonSchema
from pydantic_core.core_schema import ValidationInfo

from vizro.models import Tooltip, VizroBaseModel
from vizro.models._grid import set_layout
from vizro.models._models_utils import _build_inner_layout, _log_call, check_captured_callable_model
from vizro.models._tooltip import coerce_str_to_tooltip
from vizro.models.types import ComponentType, ControlType, LayoutType, _IdProperty


# TODO: this could be done with default_factory once we bump to pydantic>=2.10.0.
def set_variant(variant: Optional[Literal["plain", "filled", "outlined"]], info: ValidationInfo):
    if variant is not None:
        return variant
    return "plain" if info.data["collapsed"] is None else "outlined"


class Container(VizroBaseModel):
    """Container to group together a set of components on a page.

    Args:
        type (Literal["container"]): Defaults to `"container"`.
        components (list[ComponentType]): See [ComponentType][vizro.models.types.ComponentType]. At least one component
            has to be provided.
        title (str): Title of the `Container`. Defaults to `""`.
        layout (Optional[LayoutType]): Layout to place components in. Defaults to `None`.
        collapsed (Optional[bool]): Boolean flag that determines whether the container is collapsed on initial load.
            Set to `True` for a collapsed state, `False` for an expanded state. Defaults to `None`, meaning the
            container is not collapsible.
        variant (Optional[Literal["plain", "filled", "outlined"]]): Predefined styles to choose from. Options are
            `plain`, `filled` or `outlined`. Defaults to `plain` (or `outlined` for collapsible container).
        description (Optional[Tooltip]): Optional markdown string that adds an icon next to the title.
            Hovering over the icon shows a tooltip with the provided description. Defaults to `None`.
        controls (list[ControlType]): See [ControlType][vizro.models.types.ControlType]. Defaults to `[]`.
        extra (Optional[dict[str, Any]]): Extra keyword arguments that are passed to `dbc.Container` and overwrite any
            defaults chosen by the Vizro team. This may have unexpected behavior.
            Visit the [dbc documentation](https://dash-bootstrap-components.opensource.faculty.ai/docs/components/layout/)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
            underlying component may change in the future. Defaults to `{}`.


    """

    type: Literal["container"] = "container"
    # TODO[mypy], see: https://github.com/pydantic/pydantic/issues/156 for components field
    components: conlist(  # type: ignore[valid-type]
        Annotated[ComponentType, BeforeValidator(check_captured_callable_model)],
        min_length=1,
    )
    title: str = Field(default="", description="Title of the `Container`")
    layout: Annotated[Optional[LayoutType], AfterValidator(set_layout), Field(default=None, validate_default=True)]
    collapsed: Optional[bool] = Field(
        default=None,
        description="Boolean flag that determines whether the container is collapsed on initial load. "
        "Set to `True` for a collapsed state, `False` for an expanded state. "
        "Defaults to `None`, meaning the container is not collapsible.",
    )
    variant: Annotated[
        Optional[Literal["plain", "filled", "outlined"]],
        AfterValidator(set_variant),
        Field(
            default=None,
            description="Predefined styles to choose from. Options are `plain`, `filled` or `outlined`."
            "Defaults to `plain` (or `outlined` for collapsible container).",
            validate_default=True,
        ),
    ]
    # TODO: ideally description would have json_schema_input_type=Union[str, Tooltip] attached to the BeforeValidator,
    #  but this requires pydantic >= 2.9.
    description: Annotated[
        Optional[Tooltip],
        BeforeValidator(coerce_str_to_tooltip),
        Field(
            default=None,
            description="""Optional markdown string that adds an icon next to the title.
            Hovering over the icon shows a tooltip with the provided description. Defaults to `None`.""",
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
            Visit the [dbc documentation](https://dash-bootstrap-components.opensource.faculty.ai/docs/components/layout/)
            to see all available arguments. [Not part of the official Vizro schema](../explanation/schema.md) and the
            underlying component may change in the future. Defaults to `{}`.""",
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
    def build(self):
        # TODO: TBD on how to encode 'elevated', as box-shadows are not visible on a dark theme
        # It needs to be properly designed and tested out (margins have to be added etc.).
        # Below corresponds to bootstrap utility classnames, while 'bg-container' is introduced by us.
        # See: https://getbootstrap.com/docs/4.0/utilities
        # Title is not displayed if Container is inside Tabs using CSS combinators (only applies to outer container)
        # Other options we might want to consider in the future to hide the title:
        # 1) Argument inside Container.build that flags if used inside Tabs, then sets hidden attribute for the heading
        # or just doesn't supply the element at all
        # 2) Logic inside Tabs.build that sets hidden=True for the heading or uses del to remove the heading via
        # providing an ID to the heading and accessing it in the component tree
        # 3) New field in Container like short_title to allow tab label to be set independently
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
        if self.collapsed is None:
            return _build_inner_layout(self.layout, self.components)

        return dbc.Collapse(
            id=f"{self.id}_collapse",
            children=_build_inner_layout(self.layout, self.components),
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
        return html.Div(
            id=f"{self.id}-control-panel",
            children=[control.build() for control in self.controls],
            className="container-controls-panel",
        )
