from __future__ import annotations

from collections.abc import Iterable
from typing import Annotated, Any, Optional, cast

from dash import ClientsideFunction, Input, Output, State, clientside_callback, dcc, html
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
from typing_extensions import TypedDict

from vizro._constants import ON_PAGE_LOAD_ACTION_PREFIX
from vizro.actions._on_page_load import _on_page_load
from vizro.managers import model_manager
from vizro.managers._model_manager import FIGURE_MODELS, DuplicateIDError
from vizro.models import Filter, Parameter, Tooltip, VizroBaseModel
from vizro.models._action._actions_chain import ActionsChain, Trigger
from vizro.models._grid import set_layout
from vizro.models._models_utils import (
    _build_inner_layout,
    _log_call,
    check_captured_callable_model,
    warn_description_without_title,
)
from vizro.models.types import _IdProperty

from ._tooltip import coerce_str_to_tooltip
from .types import ComponentType, ControlType, FigureType, LayoutType

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
        title (str): Title of the `Page`.
        description (Optional[Tooltip]): Optional markdown string that adds an icon next to the title.
            Hovering over the icon shows a tooltip with the provided description. This also sets the page's meta
            tags. Defaults to `None`.
        layout (Optional[LayoutType]): Layout to place components in. Defaults to `None`.
        controls (list[ControlType]): See [ControlType][vizro.models.types.ControlType]. Defaults to `[]`.
        path (str): Path to navigate to page. Defaults to `""`.

    """

    # TODO[mypy], see: https://github.com/pydantic/pydantic/issues/156 for components field
    components: conlist(Annotated[ComponentType, BeforeValidator(check_captured_callable_model)], min_length=1)  # type: ignore[valid-type]
    title: str = Field(description="Title of the `Page`")
    layout: Annotated[Optional[LayoutType], AfterValidator(set_layout), Field(default=None, validate_default=True)]
    # TODO: ideally description would have json_schema_input_type=Union[str, Tooltip] attached to the BeforeValidator,
    #  but this requires pydantic >= 2.9.
    description: Annotated[
        Optional[Tooltip],
        BeforeValidator(coerce_str_to_tooltip),
        AfterValidator(warn_description_without_title),
        Field(
            default=None,
            description="""Optional markdown string that adds an icon next to the title.
            Hovering over the icon shows a tooltip with the provided description. This also sets the page's meta
            tags. Defaults to `None`.""",
        ),
    ]
    controls: list[ControlType] = []
    path: Annotated[
        str, AfterValidator(set_path), Field(default="", description="Path to navigate to page.", validate_default=True)
    ]
    actions: list[ActionsChain] = []

    @model_validator(mode="before")
    @classmethod
    def set_id(cls, values):
        if "title" not in values:
            return values

        values.setdefault("id", values["title"])
        return values

    def model_post_init(self, context: Any) -> None:
        """Adds the model instance to the model manager."""
        try:
            super().model_post_init(context)
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

    @property
    def _action_outputs(self) -> dict[str, _IdProperty]:
        return {
            "title": f"{self.id}_title.children",
            **({"description": f"{self.description.id}-text.children"} if self.description else {}),
        }

    @_log_call
    def pre_build(self):
        # TODO-AV2 A 4: work out the best place to put this logic. It could feasibly go in _on_page_load instead.
        #  Probably it's better where it is now since it avoid navigating up the model hierarchy
        #  (action -> page -> figures) and instead just looks down (page -> figures).
        #  Should there be validation inside _on_page_load to check that targets exist and are
        #  on the page and target-able components (i.e. are dynamic and hence have _action_outputs)?
        #  It's not needed urgently since we always calculate the targets ourselves so we know they are valid.
        #  Similar comments apply to filter and parameter. Note that export_data has this logic built into the action
        #  itself since the user specifies the target. In future we'll probably have a helper function like
        #  get_all_targets_on_page() that's used in many actions. So maybe it makes sense to put it in the action for
        #  on_page_load/filter/parameter too.
        figure_targets = [
            model.id for model in cast(Iterable[FigureType], model_manager._get_models(FIGURE_MODELS, root_model=self))
        ]
        filter_targets = [
            filter.id
            for filter in cast(Iterable[Filter], model_manager._get_models(Filter, root_model=self))
            if filter._dynamic
        ]
        targets = figure_targets + filter_targets

        if targets:
            # TODO-AV2 A 3: can we simplify this to not use ActionsChain, just like we do for filters and parameters?
            # See https://github.com/mckinsey/vizro/pull/363#discussion_r2021020062.
            self.actions = [
                ActionsChain(
                    id=f"{ON_PAGE_LOAD_ACTION_PREFIX}_{self.id}",
                    trigger=Trigger(
                        component_id=f"{ON_PAGE_LOAD_ACTION_PREFIX}_trigger_{self.id}", component_property="data"
                    ),
                    actions=[
                        _on_page_load(
                            id=f"{ON_PAGE_LOAD_ACTION_PREFIX}_action_{self.id}",
                            targets=targets,
                        )
                    ],
                )
            ]

        # Define a clientside callback that syncs the URL query parameters with controls that have show_in_url=True.
        url_controls = [
            control
            for control in cast(
                Iterable[ControlType],
                [*model_manager._get_models(Parameter, self), *model_manager._get_models(Filter, self)],
            )
            if control.show_in_url
        ]

        if url_controls:
            selector_values_outputs = [Output(control.selector.id, "value") for control in url_controls]
            selector_values_inputs = [Input(control.selector.id, "value") for control in url_controls]
            # Note the id is the control's id rather than the underlying selector's. This means a user doesn't
            # need to specify vm.Filter(selector=vm.Dropdown(id=...)) when they set show_in_url = True.
            control_ids_states = [State(control.id, "id") for control in url_controls]

            # The URL is updated in the clientside callback with the `history.replaceState`, instead of using a
            # dcc.Location as a callback Output. Do it because the dcc.Location uses `history.pushState` under the hood
            # which causes destroying the history. With `history.replaceState`, we partially maintain the history.
            # Similarly, we read the URL query parameters in the clientside callback with the window.location.pathname,
            # instead of using dcc.Location as a callback Input. Do it to align the behavior with the outputs and to
            # simplify the function inputs handling.
            clientside_callback(
                ClientsideFunction(namespace="page", function_name="sync_url_query_params_and_controls"),
                Output(f"{ON_PAGE_LOAD_ACTION_PREFIX}_trigger_{self.id}", "data"),
                *selector_values_outputs,
                *selector_values_inputs,
                *control_ids_states,
            )

    @_log_call
    def build(self) -> _PageBuildType:
        # Build control panel
        controls_content = [control.build() for control in self.controls]
        control_panel = html.Div(id="control-panel", children=controls_content, hidden=not controls_content)

        # Build layout with components
        components_container = _build_inner_layout(self.layout, self.components)
        components_container.id = "page-components"

        # Keep these components in components_container, moving them outside make them not work properly.
        components_container.children.extend(
            [
                dcc.Store(id=f"{ON_PAGE_LOAD_ACTION_PREFIX}_trigger_{self.id}"),
                dcc.Download(id="vizro_download"),
                dcc.Location(id="vizro_url", refresh="callback-nav"),
            ]
        )

        return html.Div([control_panel, components_container])
