from __future__ import annotations

import logging
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, List, Literal, TypedDict

import dash
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash import ClientsideFunction, Input, Output, clientside_callback, get_relative_path, html

try:
    from pydantic.v1 import Field, validator
except ImportError:  # pragma: no cov
    from pydantic import Field, validator

from dash.development.base_component import Component

import vizro
from vizro._constants import MODULE_PAGE_404, STATIC_URL_PREFIX
from vizro.actions._action_loop._action_loop import ActionLoop
from vizro.models import Navigation, VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models._navigation._navigation_utils import _NavBuildType

if TYPE_CHECKING:
    from vizro.models import Page
    from vizro.models._page import _PageBuildType

logger = logging.getLogger(__name__)


def _all_hidden(components: List[Component]):
    """Returns True if all components are either None and/or have hidden=True."""
    return all(component is None or getattr(component, "hidden", False) for component in components)


# This is just used for type checking. Ideally it would inherit from some dash.development.base_component.Component
# (e.g. html.Div) as well as TypedDict, but that's not possible, and Dash does not have typing support anyway. When
# this type is used, the object is actually still a dash.development.base_component.Component, but this makes it easier
# to see what contract the component fulfills by making the expected keys explicit.
_PageDivsType = TypedDict(
    "_PageDivsType",
    {
        "dashboard-title": html.Div,
        "settings": html.Div,
        "page-title": html.H2,
        "nav-bar": html.Div,
        "nav-panel": html.Div,
        "control-panel": html.Div,
        "components": html.Div,
    },
)


class Dashboard(VizroBaseModel):
    """Vizro Dashboard to be used within [`Vizro`][vizro._vizro.Vizro.build].

    Args:
        pages (List[Page]): See [`Page`][vizro.models.Page].
        theme (Literal["vizro_dark", "vizro_light"]): Layout theme to be applied across dashboard.
            Defaults to `vizro_dark`.
        navigation (Navigation): See [`Navigation`][vizro.models.Navigation]. Defaults to `None`.
        title (str): Dashboard title to appear on every page on top left-side. Defaults to `""`.
    """

    pages: List[Page]
    theme: Literal["vizro_dark", "vizro_light"] = Field(
        "vizro_dark", description="Layout theme to be applied across dashboard. Defaults to `vizro_dark`"
    )
    navigation: Navigation = None  # type: ignore[assignment]
    title: str = Field("", description="Dashboard title to appear on every page on top left-side.")

    @validator("pages", always=True)
    def validate_pages(cls, pages):
        if not pages:
            raise ValueError("Ensure this value has at least 1 item.")
        return pages

    @validator("navigation", always=True)
    def set_navigation_pages(cls, navigation, values):
        if "pages" not in values:
            return navigation

        navigation = navigation or Navigation()
        navigation.pages = navigation.pages or [page.id for page in values["pages"]]
        return navigation

    @_log_call
    def pre_build(self):
        meta_image = self._infer_image("app") or self._infer_image("logo")

        # Setting order here ensures that the pages in dash.page_registry preserves the order of the List[Page].
        # For now the homepage (path /) corresponds to self.pages[0].
        # Note redirect_from=["/"] doesn't work and so the / route must be defined separately.
        for order, page in enumerate(self.pages):
            dash.register_page(
                module=page.id,
                name=page.title,
                description=page.description,
                image=meta_image,
                title=f"{self.title}: {page.title}" if self.title else page.title,
                path=page.path if order else "/",
                order=order,
                layout=partial(self._make_page_layout, page),
            )
        dash.register_page(module=MODULE_PAGE_404, layout=self._make_page_404_layout())

    @_log_call
    def build(self):
        for page in self.pages:
            page.build()  # TODO: ideally remove, but necessary to register slider callbacks

        clientside_callback(
            ClientsideFunction(namespace="clientside", function_name="update_dashboard_theme"),
            Output("dashboard_container_outer", "className"),
            Input("theme_selector", "on"),
        )

        return html.Div(
            id="dashboard_container_outer",
            children=[
                html.Div(vizro.__version__, id="vizro_version", hidden=True),
                ActionLoop._create_app_callbacks(),
                dash.page_container,
            ],
            className=self.theme,
        )

    def _get_page_divs(self, page: Page) -> _PageDivsType:
        # Identical across pages
        dashboard_title = (
            html.H2(self.title, id="dashboard-title") if self.title else html.H2(hidden=True, id="dashboard-title")
        )

        settings = html.Div(
            daq.BooleanSwitch(
                id="theme_selector", on=self.theme == "vizro_dark", persistence=True, persistence_type="session"
            ),
            id="settings",
        )

        # Shared across pages but slightly differ in content. These could possibly be done by a clientside
        # callback instead.
        page_title = html.H2(page.title, id="page-title")
        navigation: _NavBuildType = self.navigation.build(active_page_id=page.id)
        nav_bar = navigation["nav-bar"]
        nav_panel = navigation["nav-panel"]

        # Different across pages
        page_content: _PageBuildType = page.build()
        control_panel = page_content["control-panel"]
        components = page_content["components"]
        return html.Div([dashboard_title, settings, page_title, nav_bar, nav_panel, control_panel, components])

    def _arrange_page_divs(self, page_divs: _PageDivsType):
        left_header_divs = [page_divs["dashboard-title"]]
        left_sidebar_divs = [page_divs["nav-bar"]]
        left_main_divs = [
            html.Div(left_header_divs, id="left-header", hidden=_all_hidden(left_header_divs)),
            page_divs["nav-panel"],
            page_divs["control-panel"],
        ]

        left_sidebar = html.Div(left_sidebar_divs, id="left-sidebar", hidden=_all_hidden(left_sidebar_divs))
        left_main = html.Div(left_main_divs, id="left-main", hidden=_all_hidden(left_main_divs))
        left_side = html.Div([left_sidebar, left_main], id="left-side")

        right_header = html.Div([page_divs["page-title"], page_divs["settings"]], id="right-header")
        right_main = page_divs["components"]
        right_side = html.Div([right_header, right_main], id="right-side")

        return html.Div([left_side, right_side], id="page-container")

    def _make_page_layout(self, page: Page):
        page_divs = self._get_page_divs(page=page)
        return self._arrange_page_divs(page_divs=page_divs)

    @staticmethod
    def _make_page_404_layout():
        return html.Div(
            [
                html.Img(src=get_relative_path(f"/{STATIC_URL_PREFIX}/images/errors/error_404.svg")),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3("This page could not be found.", className="heading-3-600"),
                                html.P("Make sure the URL you entered is correct."),
                            ],
                            className="error_text_container",
                        ),
                        dbc.Button("Take me home", href=get_relative_path("/"), className="button_primary"),
                    ],
                    className="error_content_container",
                ),
            ],
            className="page_error_container",
        )

    def _infer_image(self, filename: str):
        valid_extensions = [".apng", ".avif", ".gif", ".jpeg", ".jpg", ".png", ".svg", ".webp"]
        assets_folder = Path(dash.get_app().config.assets_folder)
        if assets_folder.is_dir():
            for path in Path(assets_folder).rglob(f"{filename}.*"):
                if path.suffix in valid_extensions:
                    return str(path.relative_to(assets_folder))
