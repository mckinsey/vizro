from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Annotated, Any, Optional, TypedDict, Union, cast

from dash import dcc, html
from pydantic import BeforeValidator, Field, conlist, model_validator, validator

# except ImportError:  # pragma: no cov
#     from pydantic import Field, validator
from vizro._constants import ON_PAGE_LOAD_ACTION_PREFIX
from vizro.actions import _on_page_load
from vizro.managers import model_manager
from vizro.managers._model_manager import FIGURE_MODELS, DuplicateIDError
from vizro.models import Action, Filter, Layout, VizroBaseModel
from vizro.models._action._actions_chain import ActionsChain, Trigger
from vizro.models._layout import set_layout
from vizro.models._models_utils import _log_call, check_captured_callable

from .types import ComponentType, ControlType

# This is just used for type checking. Ideally it would inherit from some dash.development.base_component.Component
# (e.g. html.Div) as well as TypedDict, but that's not possible, and Dash does not have typing support anyway. When
# this type is used, the object is actually still a dash.development.base_component.Component, but this makes it easier
# to see what contract the component fulfills by making the expected keys explicit.
_PageBuildType = TypedDict("_PageBuildType", {"control-panel": html.Div, "page-components": html.Div})


class Page(VizroBaseModel):
    """A page in [`Dashboard`][vizro.models.Dashboard] with its own URL path and place in the `Navigation`.

    Args:
        components (list[ComponentType]): See [ComponentType][vizro.models.types.ComponentType]. At least one component
            has to be provided.
        title (str): Title to be displayed.
        description (str): Description for meta tags.
        layout (Layout): Layout to place components in. Defaults to `None`.
        controls (list[ControlType]): See [ControlType][vizro.models.types.ControlType]. Defaults to `[]`.
        path (str): Path to navigate to page. Defaults to `""`.

    """

    components: conlist(
        Annotated[ComponentType, BeforeValidator(check_captured_callable), Field(...)], min_length=1
    )  # since no default, can skip validate_default
    title: str = Field(..., description="Title to be displayed.")
    description: str = Field("", description="Description for meta tags.")
    layout: Optional[Layout] = None
    controls: list[ControlType] = []
    path: str = Field("", description="Path to navigate to page.")

    # TODO: Remove default on page load action if possible
    actions: list[ActionsChain] = []

    # Re-used validators
    _validate_layout = validator("layout", allow_reuse=True, always=True)(set_layout)

    @model_validator(mode="before")
    @classmethod
    def set_id(cls, values):
        if "title" not in values:
            return values

        values.setdefault("id", values["title"])
        return values

    # TODO[pydantic]: We couldn't refactor the `validator`, please replace it by `field_validator` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-validators for more information.
    @validator("path", always=True)
    def set_path(cls, path, values) -> str:
        # Based on how Github generates anchor links - see:
        # https://stackoverflow.com/questions/72536973/how-are-github-markdown-anchor-links-constructed.
        def clean_path(path: str, allowed_characters: str) -> str:
            path = path.strip().lower().replace(" ", "-")
            path = "".join(character for character in path if character.isalnum() or character in allowed_characters)
            return path if path.startswith("/") else "/" + path

        # Allow "/" in path if provided by user, otherwise turn page id into suitable URL path (not allowing "/")
        if path:
            return clean_path(path, "-_/")
        return clean_path(values["id"], "-_")

    def __init__(self, **data):
        """Adds the model instance to the model manager."""
        try:
            super().__init__(**data)
        except DuplicateIDError as exc:
            raise ValueError(
                f"Page with id={self.id} already exists. Page id is automatically set to the same "
                f"as the page title. If you have multiple pages with the same title then you must assign a unique id."
            ) from exc

    def __vizro_exclude_fields__(self) -> Optional[Union[set[str], Mapping[str, Any]]]:
        return {"id"} if self.id == self.title else None

    @_log_call
    def pre_build(self):
        figure_targets = [
            model.id for model in cast(Iterable[VizroBaseModel], model_manager._get_models(FIGURE_MODELS, page=self))
        ]
        filter_targets = [
            filter.id
            for filter in cast(Iterable[Filter], model_manager._get_models(Filter, page=self))
            if filter._dynamic
        ]
        targets = figure_targets + filter_targets

        if targets:
            self.actions = [
                ActionsChain(
                    id=f"{ON_PAGE_LOAD_ACTION_PREFIX}_{self.id}",
                    trigger=Trigger(
                        component_id=f"{ON_PAGE_LOAD_ACTION_PREFIX}_trigger_{self.id}", component_property="data"
                    ),
                    actions=[
                        Action(
                            id=f"{ON_PAGE_LOAD_ACTION_PREFIX}_action_{self.id}", function=_on_page_load(targets=targets)
                        )
                    ],
                )
            ]

    @_log_call
    def build(self) -> _PageBuildType:
        controls_content = [control.build() for control in self.controls]
        control_panel = html.Div(id="control-panel", children=controls_content, hidden=not controls_content)

        components_container = self.layout.build()
        for component_idx, component in enumerate(self.components):
            components_container[f"{self.layout.id}_{component_idx}"].children = component.build()

        # Page specific CSS ID and Stores
        components_container.children.append(dcc.Store(id=f"{ON_PAGE_LOAD_ACTION_PREFIX}_trigger_{self.id}"))
        components_container.id = "page-components"
        return html.Div([control_panel, components_container])
