from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Literal, Optional, cast

import dash_bootstrap_components as dbc
from dash import html
from pydantic import AfterValidator, BeforeValidator, Field, conlist

from vizro.models import VizroBaseModel
from vizro.models._layout import set_layout
from vizro.models._models_utils import _log_call, check_captured_callable_model
from vizro.models.types import ComponentType

if TYPE_CHECKING:
    from vizro.models import Layout


class Container(VizroBaseModel):
    """Container to group together a set of components on a page.

    Args:
        type (Literal["container"]): Defaults to `"container"`.
        components (list[ComponentType]): See [ComponentType][vizro.models.types.ComponentType]. At least one component
            has to be provided.
        title (str): Title to be displayed.
        layout (Optional[Layout]): Layout to place components in. Defaults to `None`.
        variant (Literal["filled", "outlined", "plain"]): Predefined styles to choose from. Options are `filled`,
            `outlined` or `plain`. Defaults to `plain`.

    """

    type: Literal["container"] = "container"
    # TODO[mypy], see: https://github.com/pydantic/pydantic/issues/156 for components field
    components: conlist(  # type: ignore[valid-type]
        Annotated[ComponentType, BeforeValidator(check_captured_callable_model)],
        min_length=1,
    )
    title: str = Field(description="Title to be displayed.")
    layout: Annotated[Optional[Layout], AfterValidator(set_layout), Field(default=None, validate_default=True)]
    variant: Literal["filled", "outlined", "plain"] = Field(
        default="plain",
        description="Predefined styles to choose from. Options are `filled`, `outlined` or `plain`. "
        "Defaults to `plain`.",
    )

    @_log_call
    def build(self):
        # TODO: TBD on how to encode 'elevated', as box-shadows are not visible on a dark theme
        # It needs to be properly designed and tested out (margins have to be added etc.).
        # Below corresponds to bootstrap utility classnames, while 'bg-container' is introduced by us.
        # See: https://getbootstrap.com/docs/4.0/utilities
        variants = {"outlined": "border p-3", "filled": "bg-container p-3", "plain": ""}

        return dbc.Container(
            id=self.id,
            children=[
                html.H3(children=self.title, className="container-title", id=f"{self.id}_title"),
                self._build_inner_layout(),
            ],
            fluid=True,
            className=variants[self.variant],
        )

    def _build_inner_layout(self):
        """Builds inner layout and assigns components to grid position."""
        # Title is not displayed if Container is inside Tabs using CSS combinators (only applies to outer container)
        # Other options we might want to consider in the future to hide the title:
        # 1) Argument inside Container.build that flags if used inside Tabs, then sets hidden attribute for the heading
        # or just doesn't supply the element at all
        # 2) Logic inside Tabs.build that sets hidden=True for the heading or uses del to remove the heading via
        # providing an ID to the heading and accessing it in the component tree
        # 3) New field in Container like short_title to allow tab label to be set independently
        from vizro.models import Layout

        self.layout = cast(
            Layout,  # cannot actually be None if you check components and layout field together
            self.layout,
        )
        components_container = self.layout.build()
        for component_idx, component in enumerate(self.components):
            components_container[f"{self.layout.id}_{component_idx}"].children = component.build()

        return components_container
