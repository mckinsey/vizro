from __future__ import annotations

from typing import Annotated, Any, Literal, Optional

import dash_bootstrap_components as dbc
from dash import html
from pydantic import AfterValidator, BeforeValidator, Field, conlist
from pydantic.json_schema import SkipJsonSchema

from vizro.models import VizroBaseModel
from vizro.models._grid import set_layout
from vizro.models._models_utils import _build_inner_layout, _log_call, check_captured_callable_model
from vizro.models.types import ComponentType, LayoutType


class Container(VizroBaseModel):
    """Container to group together a set of components on a page.

    Args:
        type (Literal["container"]): Defaults to `"container"`.
        components (list[ComponentType]): See [ComponentType][vizro.models.types.ComponentType]. At least one component
            has to be provided.
        title (str): Title of the `Container`. Defaults to `""`.
        layout (Optional[LayoutType]): Layout to place components in. Defaults to `None`.
        variant (Literal["plain", "filled", "outlined"]): Predefined styles to choose from. Options are `plain`,
            `filled` or `outlined`. Defaults to `plain`.
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
    variant: Literal["plain", "filled", "outlined"] = Field(
        default="plain",
        description="Predefined styles to choose from. Options are `plain`, `filled` or `outlined`."
        "Defaults to `plain`.",
    )
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
        variants = {"plain": "", "filled": "bg-container p-3", "outlined": "border p-3"}

        defaults = {
            "id": self.id,
            "children": [
                html.H3(children=self.title, className="container-title", id=f"{self.id}_title")
                if self.title
                else None,
                _build_inner_layout(self.layout, self.components),
            ],
            "fluid": True,
            "class_name": variants[self.variant],
        }

        return dbc.Container(**(defaults | self.extra))
