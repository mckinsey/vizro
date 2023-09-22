from __future__ import annotations

from typing import List, Optional

import dash_bootstrap_components as dbc
import dash_daq as daq
from dash import Input, Output, Patch, callback, dcc, html
from pydantic import Field, root_validator, validator

import vizro._themes as themes
from vizro._constants import ON_PAGE_LOAD_ACTION_PREFIX
from vizro.actions import _on_page_load
from vizro.managers import model_manager
from vizro.managers._model_manager import DuplicateIDError
from vizro.models import Action, Dashboard, Graph, Layout, VizroBaseModel
from vizro.models._action._actions_chain import ActionsChain, Trigger
from vizro.models._models_utils import _log_call, get_unique_grid_component_ids

from .types import ComponentType, ControlType


class Page(VizroBaseModel):
    """A page in [`Dashboard`][vizro.models.Dashboard] with its own URL path and place in the `Navigation`.

    Args:
        components (List[ComponentType]): See [ComponentType][vizro.models.types.ComponentType]. At least one component
            has to be provided.
        title (str): Title to be displayed.
        layout (Optional[Layout]): Layout to place components in. Defaults to `None`.
        controls (List[ControlType]): See [ControlType][vizro.models.types.ControlType]. Defaults to `[]`.
        path (Optional[str]): Path to navigate to page. Defaults to `None`.

    Raises:
        ValueError: If number of page and grid components is not the same
    """

    components: List[ComponentType]
    title: str = Field(..., description="Title to be displayed.")
    layout: Optional[Layout]
    controls: List[ControlType] = []
    path: Optional[str] = Field(None, description="Path to navigate to page.")

    # TODO: Remove default on page load action if possible
    actions: List[ActionsChain] = []

    @root_validator(pre=True)
    def set_id(cls, values):
        if "title" not in values:
            return values

        values.setdefault("id", values["title"])
        return values

    @validator("components", always=True)
    def set_components(cls, components):
        if not components:
            raise ValueError("Ensure this value has at least 1 item.")
        return components

    @validator("layout", always=True)
    def set_layout(cls, layout, values) -> Layout:
        if "components" not in values:
            return layout

        if layout is None:
            grid = [[i] for i in range(len(values["components"]))]
            return Layout(grid=grid)

        unique_grid_idx = get_unique_grid_component_ids(layout.grid)
        if len(unique_grid_idx) != len(values["components"]):
            raise ValueError("Number of page and grid components need to be the same.")
        return layout

    @validator("path", always=True)
    def set_path(cls, path, values) -> str:
        # Based on how Github generates anchor links - see:
        # https://stackoverflow.com/questions/72536973/how-are-github-markdown-anchor-links-constructed.
        def clean_path(path, allowed_characters):
            path = path.strip().lower().replace(" ", "-")
            path = "".join(character for character in path if character.isalnum() or character in allowed_characters)
            return "/" + path

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

    @_log_call
    def pre_build(self):
        # TODO: Remove default on page load action if possible
        if any(isinstance(component, Graph) for component in self.components):
            self.actions = [
                ActionsChain(
                    id=f"{ON_PAGE_LOAD_ACTION_PREFIX}_{self.id}",
                    trigger=Trigger(
                        component_id=f"{ON_PAGE_LOAD_ACTION_PREFIX}_trigger_{self.id}",
                        component_property="data",
                    ),
                    actions=[
                        Action(
                            id=f"{ON_PAGE_LOAD_ACTION_PREFIX}_action_{self.id}", function=_on_page_load(page_id=self.id)
                        )
                    ],
                )
            ]

    @_log_call
    def build(self):
        self._update_graph_theme()
        controls_content = [control.build() for control in self.controls]
        components_content = [
            html.Div(
                component.build(),
                style={
                    "gridColumn": f"{grid_coord.col_start}/{grid_coord.col_end}",
                    "gridRow": f"{grid_coord.row_start}/{grid_coord.row_end}",
                },
            )
            for component, grid_coord in zip(
                self.components, self.layout.component_grid_lines  # type: ignore[union-attr]
            )
        ]
        return self._make_page_layout(controls_content, components_content)

    def _update_graph_theme(self):
        outputs = [
            Output(component.id, "figure", allow_duplicate=True)
            for component in self.components
            if isinstance(component, Graph)
        ]
        if outputs:

            @callback(
                outputs,
                Input("theme_selector", "on"),
                prevent_initial_call="initial_duplicate",
            )
            def update_graph_theme(theme_selector_on: bool):
                patched_figure = Patch()
                patched_figure["layout"]["template"] = themes.dark if theme_selector_on else themes.light
                return [patched_figure] * len(outputs)

    @staticmethod
    def _create_theme_switch():
        _, dashboard = next(model_manager._items_with_type(Dashboard))
        theme_switch = daq.BooleanSwitch(
            id="theme_selector", on=True if dashboard.theme == "vizro_dark" else False, persistence=True
        )
        return theme_switch

    @staticmethod
    def _create_control_panel(controls_content):
        keyline = html.Div(className="keyline")
        control_panel = html.Div(
            children=[*controls_content, keyline],
            className="control_panel",
        )
        return control_panel if controls_content else None

    def _create_nav_panel(self):
        from vizro.models._navigation._accordion import Accordion

        _, dashboard = next(model_manager._items_with_type(Dashboard))
        if dashboard.navigation:
            return dashboard.navigation.build()

        return Accordion().build()

    def _create_component_container(self, components_content):
        component_container = html.Div(
            children=html.Div(
                components_content,
                style={
                    "gridRowGap": self.layout.row_gap,  # type: ignore[union-attr]
                    "gridColumnGap": self.layout.col_gap,  # type: ignore[union-attr]
                    "gridTemplateColumns": f"repeat({len(self.layout.grid[0])},"  # type: ignore[union-attr]
                    f"minmax({self.layout.col_min_width}, 1fr))",
                    "gridTemplateRows": f"repeat({len(self.layout.grid)},"  # type: ignore[union-attr]
                    f"minmax({self.layout.row_min_height}, 1fr))",
                },
                className="component_container_grid",
            ),
            className="component_container",
        )
        return component_container

    @staticmethod
    def _arrange_containers(page_title, theme_switch, nav_panel, control_panel, component_container):
        """Defines div container arrangement on page.

        To change arrangement, one has to change the order in the header, left_side and/or right_side_elements.
        """
        _, dashboard = next(model_manager._items_with_type(Dashboard))
        dashboard_title = (
            html.Div(
                children=[html.H2(dashboard.title), html.Div(className="keyline")], className="dashboard_title_outer"
            )
            if dashboard.title
            else None
        )

        header_elements = [page_title, theme_switch]
        left_side_elements = [dashboard_title, nav_panel, control_panel]
        header = html.Div(
            children=header_elements,
            className="header",
        )
        left_side = html.Div(
            children=left_side_elements,
            className="left_side",
        )
        right_side_elements = [header, component_container]
        right_side = html.Div(
            children=right_side_elements,
            className="right_side",
        )
        return left_side, right_side

    def _make_page_layout(self, controls_content, components_content):
        # Create dashboard containers/elements
        page_title = html.H2(children=self.title)
        theme_switch = self._create_theme_switch()
        nav_panel = self._create_nav_panel()
        control_panel = self._create_control_panel(controls_content)
        component_container = self._create_component_container(components_content)

        # Arrange dashboard containers
        left_side, right_side = self._arrange_containers(
            page_title=page_title,
            theme_switch=theme_switch,
            nav_panel=nav_panel,
            control_panel=control_panel,
            component_container=component_container,
        )

        return dbc.Container(
            id=self.id,
            children=[dcc.Store(id=f"{ON_PAGE_LOAD_ACTION_PREFIX}_trigger_{self.id}"), left_side, right_side],
            className="page_container",
        )
