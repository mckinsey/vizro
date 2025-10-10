from __future__ import annotations

from collections.abc import Iterable
from itertools import chain
from typing import Annotated, Optional, cast

from dash import ClientsideFunction, Input, Output, State, clientside_callback, dcc, html
from pydantic import (
    AfterValidator,
    BeforeValidator,
    Field,
    conlist,
    model_validator,
)
from typing_extensions import TypedDict

from vizro._constants import ON_PAGE_LOAD_ACTION_PREFIX
from vizro.actions._on_page_load import _on_page_load
from vizro.managers import model_manager
from vizro.managers._model_manager import FIGURE_MODELS
from vizro.models import Filter, Parameter, Tooltip, VizroBaseModel
from vizro.models._grid import set_layout
from vizro.models._models_utils import (
    _all_hidden,
    _build_inner_layout,
    _log_call,
    check_captured_callable_model,
    make_actions_chain,
    warn_description_without_title,
)
from vizro.models.types import ActionsType, _IdProperty

from ._action._action import _BaseAction
from ._tooltip import coerce_str_to_tooltip
from .types import ComponentType, ControlType, FigureType, LayoutType

# This is just used for type checking. Ideally it would inherit from some dash.development.base_component.Component
# (e.g. html.Div) as well as TypedDict, but that's not possible, and Dash does not have typing support anyway. When
# this type is used, the object is actually still a dash.development.base_component.Component, but this makes it easier
# to see what contract the component fulfills by making the expected keys explicit.
_PageBuildType = TypedDict("_PageBuildType", {"control-panel": html.Div, "page-components": html.Div})


# Based on how Github generates anchor links - see:
# https://stackoverflow.com/questions/72536973/how-are-github-markdown-anchor-links-constructed.
def clean_path(path: str, allowed_characters: str) -> str:
    path = path.strip().lower().replace(" ", "-")
    path = "".join(character for character in path if character.isalnum() or character in allowed_characters)
    return path if path.startswith("/") else "/" + path


class Page(VizroBaseModel):
    """A page in [`Dashboard`][vizro.models.Dashboard] with its own URL path and place in the `Navigation`.

    Abstract: Usage documentation
        [How to make dashboard pages](../user-guides/pages.md)

    Args:
        components (list[ComponentType]): See [ComponentType][vizro.models.types.ComponentType]. At least one component
            has to be provided.
        title (str): Title of the `Page`.
        layout (Optional[LayoutType]): Layout to place components in. Defaults to `None`.
        description (Optional[Tooltip]): Optional markdown string that adds an icon next to the title.
            Hovering over the icon shows a tooltip with the provided description. This also sets the page's meta
            tags. Defaults to `None`.
        controls (list[ControlType]): See [ControlType][vizro.models.types.ControlType]. Defaults to `[]`.
        path (str): Path to navigate to page. Defaults to `""`.
        actions (ActionsType): See [`ActionsType`][vizro.models.types.ActionsType].
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
    path: Annotated[str, Field(default="", description="Path to navigate to page.")]
    actions: ActionsType = []

    @model_validator(mode="after")
    def _make_actions_chain(self):
        return make_actions_chain(self)

    # This should ideally be a field validator, but we need access to the model_fields_set
    @model_validator(mode="after")
    def validate_path(self):
        if self.path:
            new_path = clean_path(self.path, "-_/")
        elif "id" in self.model_fields_set:
            new_path = clean_path(self.id, "-_")
        else:
            new_path = clean_path(self.title, "-_")

        # Check for duplicate path - will move to pre_build in next PR
        for page in cast(Iterable[Page], model_manager._get_models(Page)):
            # Need to check for id equality to avoid checking the same page against itself
            if not self.id == page.id and new_path == page.path:
                raise ValueError(f"Path {new_path} cannot be used by more than one page.")

        # We should do self.path = new_path but this leads to a recursion error. The below is a workaround
        # until the pydantic bug is fixed. See https://github.com/pydantic/pydantic/issues/6597.
        self.__dict__["path"] = new_path

        return self

    @property
    def _action_triggers(self) -> dict[str, _IdProperty]:
        return {"__default__": f"{ON_PAGE_LOAD_ACTION_PREFIX}_trigger_{self.id}.data"}

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
            self.actions = [_on_page_load(id=f"{ON_PAGE_LOAD_ACTION_PREFIX}_{self.id}", targets=targets)]

        controls = cast(
            Iterable[ControlType],
            [*model_manager._get_models(Parameter, self), *model_manager._get_models(Filter, self)],
        )

        if controls:
            # TODO-AV2 D: Think about merging this with the URL callback when start working on cross-page actions.
            # Selector values as outputs to be reset.
            selector_outputs = [Output(control.selector.id, "value", allow_duplicate=True) for control in controls]

            # Selector guard is set to True when selector value is reset to prevent actions chain from running.
            selector_guard_outputs = [
                Output(f"{control.selector.id}_guard_actions_chain", "data", allow_duplicate=True)
                for control in controls
            ]

            clientside_callback(
                ClientsideFunction(namespace="page", function_name="reset_controls"),
                Output(f"{ON_PAGE_LOAD_ACTION_PREFIX}_trigger_{self.id}", "data", allow_duplicate=True),
                *selector_outputs,
                *selector_guard_outputs,
                Input(f"{self.id}_reset_button", "n_clicks"),
                State("vizro_controls_store", "data"),
                State(self.id, "id"),  # Assigned to outermost Div in Dashboard._make_page_layout.
                prevent_initial_call=True,
            )

        # Define a clientside callback that syncs the URL query parameters with controls that have show_in_url=True.
        url_controls = [control for control in controls if control.show_in_url]

        if url_controls:
            selector_values_inputs = [Input(control.selector.id, "value") for control in url_controls]
            # Note the id is the control's id rather than the underlying selector's. This means a user doesn't
            # need to specify vm.Filter(selector=vm.Dropdown(id=...)) when they set show_in_url = True.
            control_ids_states = [State(control.id, "id") for control in url_controls]
            # `control_selector_ids_states` holds metadata needed for setting selector values
            # and their selector guard component via a clientside callback (`dash_clientside.set_props`).
            # SetProps is used to avoid sending selector values as callback outputs, which can cause unpredictable
            # triggering of the guard-actions-chain callback.
            control_selector_ids_states = [State(control.selector.id, "id") for control in url_controls]

            # The URL is updated in the clientside callback with the `history.replaceState`, instead of using a
            # dcc.Location as a callback Output. Do it because the dcc.Location uses `history.pushState` under the hood
            # which causes destroying the history. With `history.replaceState`, we partially maintain the history.
            # Similarly, we read the URL query parameters in the clientside callback with the window.location.pathname,
            # instead of using dcc.Location as a callback Input. Do it to align the behavior with the outputs and to
            # simplify the function inputs handling.
            clientside_callback(
                ClientsideFunction(namespace="page", function_name="sync_url_query_params_and_controls"),
                Output(f"{ON_PAGE_LOAD_ACTION_PREFIX}_trigger_{self.id}", "data"),
                Input(f"{ON_PAGE_LOAD_ACTION_PREFIX}_trigger_{self.id}", "data"),
                *selector_values_inputs,
                *control_ids_states,
                *control_selector_ids_states,
            )

    @_log_call
    def build(self) -> _PageBuildType:
        # Build control panel
        controls_content = [control.build() for control in self.controls]
        control_panel = html.Div(
            id="control-panel", children=controls_content, hidden=not controls_content or _all_hidden(controls_content)
        )

        # Build layout with components
        components_container = _build_inner_layout(self.layout, self.components)
        components_container.id = "page-components"

        # These components are recreated on every page rather than going at the global dashboard level so that we do
        # not accidentally trigger callbacks (workaround for Dash prevent_initial_call=True behavior).
        action_components = list(
            chain.from_iterable(
                action._dash_components
                for action in cast(Iterable[_BaseAction], model_manager._get_models(_BaseAction, root_model=self))
            )
        )

        # Keep these components in components_container, moving them outside make them not work properly.
        components_container.children.extend(
            [
                *action_components,
                dcc.Store(id=f"{ON_PAGE_LOAD_ACTION_PREFIX}_trigger_{self.id}"),
                dcc.Download(id="vizro_download"),
                dcc.Location(id="vizro_url", refresh="callback-nav"),
            ]
        )

        return html.Div([control_panel, components_container])
