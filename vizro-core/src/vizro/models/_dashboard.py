from __future__ import annotations

import logging
from typing import TYPE_CHECKING, List, Literal, Optional

import dash
import dash_bootstrap_components as dbc
import plotly.io as pio
from dash import ClientsideFunction, Input, Output, clientside_callback, html
from pydantic import Field, validator

import vizro
from vizro._constants import MODULE_PAGE_404, STATIC_URL_PREFIX
from vizro.actions._action_loop._action_loop import ActionLoop
from vizro.models import Navigation, VizroBaseModel
from vizro.models._models_utils import _log_call

if TYPE_CHECKING:
    from vizro.models import Page

logger = logging.getLogger(__name__)


def update_theme(on: bool):
    return "vizro_dark" if on else "vizro_light"


def create_layout_page_404():
    return html.Div(
        [
            html.Img(src=STATIC_URL_PREFIX + "/images/errors/error_404.svg"),
            html.Div(
                [
                    html.Div(
                        [
                            html.H3("This page could not be found.", className="heading-3-600"),
                            html.P("Make sure the URL you entered is correct."),
                        ],
                        className="error_text_container",
                    ),
                    dbc.Button("Take me home", href="/", className="button_primary"),
                ],
                className="error_content_container",
            ),
        ],
        className="page_error_container",
    )


class Dashboard(VizroBaseModel):
    """Vizro Dashboard to be used within [`Vizro`][vizro._vizro.Vizro.build].

    Args:
        pages (List[Page]): See [`Page`][vizro.models.Page].
        theme (Literal["vizro_dark", "vizro_light"]): Layout theme to be applied across dashboard.
            Defaults to `vizro_dark`.
        navigation (Optional[Navigation]): See [`Navigation`][vizro.models.Navigation]. Defaults to `None`.
        title (Optional[str]): Dashboard title to appear on every page on top left-side. Defaults to `None`.
    """

    pages: List[Page]
    theme: Literal["vizro_dark", "vizro_light"] = Field(
        "vizro_dark", description="Layout theme to be applied across dashboard. Defaults to `vizro_dark`"
    )
    navigation: Optional[Navigation] = None
    title: Optional[str] = Field(None, description="Dashboard title to appear on every page on top left-side.")

    @validator("pages", always=True)
    def validate_pages(cls, pages):
        if not pages:
            raise ValueError("Ensure this value has at least 1 item.")
        return pages

    @validator("navigation", always=True)
    def validate_navigation(cls, navigation, values):
        if "pages" not in values:
            return navigation
        if navigation is None:
            return Navigation(pages=[page.id for page in values["pages"]])
        return navigation

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # pio is the backend global state and shouldn't be changed while
        # the app is running. This limitation leads to the case that Graphs blink
        # on page load if user previously has changed theme_selector.
        pio.templates.default = self.theme

    @_log_call
    def pre_build(self):
        # Setting order here ensures that the pages in dash.page_registry preserves the order of the List[Page].
        # For now the homepage (path /) corresponds to self.pages[0].
        # Note redirect_from=["/"] doesn't work and so the / route must be defined separately.
        for order, page in enumerate(self.pages):
            path = page.path if order else "/"
            dash.register_page(module=page.id, name=page.title, path=path, order=order, layout=page.build)
        self._create_error_page_404()

    @_log_call
    def build(self):
        for page in self.pages:
            page.build()  # TODO: ideally remove, but necessary to register slider callbacks
        self._update_theme()

        return dbc.Container(
            id="dashboard_container_outer",
            children=[
                html.Div(id=f"vizro_version_{vizro.__version__}"),
                ActionLoop._create_app_callbacks(),
                dash.page_container,
            ],
            className=self.theme,
            fluid=True,
        )

    @staticmethod
    def _update_theme():
        clientside_callback(
            ClientsideFunction(namespace="clientside", function_name="update_dashboard_theme"),
            Output("dashboard_container_outer", "className"),
            Input("theme_selector", "on"),
        )

    @staticmethod
    def _create_error_page_404():
        return dash.register_page(module=MODULE_PAGE_404, layout=create_layout_page_404())
