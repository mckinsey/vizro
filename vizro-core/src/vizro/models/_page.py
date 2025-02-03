from __future__ import annotations

from collections.abc import Iterable
from typing import Annotated, Optional, TypedDict, cast

from dash import dcc, html
from pydantic import (
    AfterValidator,
    BeforeValidator,
    Field,
    FieldSerializationInfo,
    SerializerFunctionWrapHandler,
    ValidationInfo,
    conlist,
    model_serializer,
    model_validator,
)

from vizro._constants import ON_PAGE_LOAD_ACTION_PREFIX
from vizro.actions import _on_page_load
from vizro.managers import model_manager
from vizro.managers._model_manager import FIGURE_MODELS, DuplicateIDError
from vizro.models import Action, Filter, Layout, VizroBaseModel
from vizro.models._action._actions_chain import ActionsChain, Trigger
from vizro.models._layout import set_layout
from vizro.models._models_utils import _log_call, check_captured_callable_model

from .types import ComponentType, ControlType

# This is just used for type checking. Ideally it would inherit from some dash.development.base_component.Component
# (e.g. html.Div) as well as TypedDict, but that's not possible, and Dash does not have typing support anyway. When
# this type is used, the object is actually still a dash.development.base_component.Component, but this makes it easier
# to see what contract the component fulfills by making the expected keys explicit.
_PageBuildType = TypedDict("_PageBuildType", {"control-panel": html.Div, "page-components": html.Div})


def set_path(path: str, info: ValidationInfo) -> str:
    # Based on how Github generates anchor links - see:
    # https://stackoverflow.com/questions/72536973/how-are-github-markdown-anchor-links-constructed.
    def clean_path(path: str, allowed_characters: str) -> str:
        path = path.strip().lower().replace(" ", "-")
        path = "".join(character for character in path if character.isalnum() or character in allowed_characters)
        return path if path.startswith("/") else "/" + path

    # Allow "/" in path if provided by user, otherwise turn page id into suitable URL path (not allowing "/")
    if path:
        return clean_path(path, "-_/")
    return clean_path(info.data["id"], "-_")


class Page(VizroBaseModel):
    """A page in [`Dashboard`][vizro.models.Dashboard] with its own URL path and place in the `Navigation`.

    Args:
        components (list[ComponentType]): See [ComponentType][vizro.models.types.ComponentType]. At least one component
            has to be provided.
        title (str): Title to be displayed.
        description (str): Description for meta tags.
        layout (Optional[Layout]): Layout to place components in. Defaults to `None`.
        controls (list[ControlType]): See [ControlType][vizro.models.types.ControlType]. Defaults to `[]`.
        path (str): Path to navigate to page. Defaults to `""`.

    """

    # TODO[mypy], see: https://github.com/pydantic/pydantic/issues/156 for components field
    components: conlist(Annotated[ComponentType, BeforeValidator(check_captured_callable_model)], min_length=1)  # type: ignore[valid-type]
    title: str = Field(description="Title to be displayed.")
    description: str = Field(default="", description="Description for meta tags.")
    layout: Annotated[Optional[Layout], AfterValidator(set_layout), Field(default=None, validate_default=True)]
    controls: list[ControlType] = []
    path: Annotated[
        str, AfterValidator(set_path), Field(default="", description="Path to navigate to page.", validate_default=True)
    ]

    # TODO: Remove default on page load action if possible
    actions: list[ActionsChain] = []

    @model_validator(mode="before")
    @classmethod
    def set_id(cls, values):
        if "title" not in values:
            return values

        values.setdefault("id", values["title"])
        return values

    def __init__(self, **data):
        """Adds the model instance to the model manager."""
        try:
            super().__init__(**data)
        except DuplicateIDError as exc:
            raise ValueError(
                f"Page with id={self.id} already exists. Page id is automatically set to the same "
                f"as the page title. If you have multiple pages with the same title then you must assign a unique id."
            ) from exc

    # This is a modification of the original `model_serializer` decorator that allows for the `context` to be passed
    # It allows skipping the `id` serialization if it is the same as the `title`
    @model_serializer(mode="wrap")  # type: ignore[type-var]
    def _serialize_id(self, handler: SerializerFunctionWrapHandler, info: FieldSerializationInfo):
        result = handler(self)
        if info.context is not None and info.context.get("add_name", False):
            result["__vizro_model__"] = self.__class__.__name__
        if self.title == self.id:
            result.pop("id", None)
            return result
        return result

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

        self.layout = cast(
            Layout,
            self.layout,  # cannot actually be None if you check components and layout field together
        )
        components_container = self.layout.build()
        for component_idx, component in enumerate(self.components):
            components_container[f"{self.layout.id}_{component_idx}"].children = component.build()

        # Page specific CSS ID and Stores
        components_container.children.append(dcc.Store(id=f"{ON_PAGE_LOAD_ACTION_PREFIX}_trigger_{self.id}"))
        components_container.id = "page-components"
        return html.Div([control_panel, components_container])
