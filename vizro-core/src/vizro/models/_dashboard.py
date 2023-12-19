from __future__ import annotations

import logging
from functools import partial
from typing import TYPE_CHECKING, List, Literal

import dash
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash import ClientsideFunction, Input, Output, clientside_callback, get_relative_path, html

try:
    from pydantic.v1 import Field, validator
except ImportError:  # pragma: no cov
    from pydantic import Field, validator

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
        # Setting order here ensures that the pages in dash.page_registry preserves the order of the List[Page].
        # For now the homepage (path /) corresponds to self.pages[0].
        # Note redirect_from=["/"] doesn't work and so the / route must be defined separately.
        for order, page in enumerate(self.pages):
            path = page.path if order else "/"
            dash.register_page(
                module=page.id, name=page.title, path=path, order=order, layout=partial(self._make_page_layout, page)
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

        return dbc.Container(
            id="dashboard_container_outer",
            children=[
                html.Div(vizro.__version__, id="vizro_version", hidden=True),
                ActionLoop._create_app_callbacks(),
                dash.page_container,
            ],
            className=self.theme,
            fluid=True,
        )

    def _make_page_layout(self, page: Page):
        # Identical across pages
        dashboard_title = (
            html.Div(children=[html.H2(self.title), html.Hr()], className="dashboard_title", id="dashboard_title_outer")
            if self.title
            else html.Div(hidden=True, id="dashboard_title_outer")
        )
        theme_switch = daq.BooleanSwitch(
            id="theme_selector", on=self.theme == "vizro_dark", persistence=True, persistence_type="session"
        )

        # Shared across pages but slightly differ in content. These could possibly be done by a clientside
        # callback instead.
        page_title = html.H2(children=page.title, id="page_title")
        navigation: _NavBuildType = self.navigation.build(active_page_id=page.id)
        nav_bar = navigation["nav_bar_outer"]
        nav_panel = navigation["nav_panel_outer"]

        # Different across pages
        page_content: _PageBuildType = page.build()
        control_panel = page_content["control_panel_outer"]
        component_container = page_content["component_container_outer"]

        # Arrangement
        header = html.Div(children=[page_title, theme_switch], className="header", id="header_outer")
        nav_control_elements = [dashboard_title, nav_panel, control_panel]
        nav_control_panel = (
            html.Div(nav_control_elements, className="nav_control_panel")
            if any(not getattr(element, "hidden", False) for element in nav_control_elements)
            else None
        )

        left_side = html.Div(children=[nav_bar, nav_control_panel], className="left_side", id="left_side_outer")
        right_side = html.Div(children=[header, component_container], className="right_side", id="right_side_outer")
        return html.Div([left_side, right_side], className="page_container", id="page_container_outer")

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
