from __future__ import annotations

import logging
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, List, Literal, TypedDict

import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import (
    ClientsideFunction,
    Input,
    Output,
    State,
    clientside_callback,
    dcc,
    get_asset_url,
    get_relative_path,
    html,
)

try:
    from pydantic.v1 import Field, validator
except ImportError:  # pragma: no cov
    from pydantic import Field, validator

from dash.development.base_component import Component

import vizro
from vizro import _themes as themes
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
    """Returns True if all `components` are either None and/or have hidden=True and/or className contains `d-none`."""
    return all(
        component is None
        or getattr(component, "hidden", False)
        or "d-none" in getattr(component, "className", "d-inline")
        for component in components
    )


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
        "nav-bar": dbc.Navbar,
        "nav-panel": dbc.Nav,
        "logo": html.Div,
        "control-panel": html.Div,
        "page-components": html.Div,
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
        self.pages[0].path = "/"

        for order, page in enumerate(self.pages):
            dash.register_page(
                module=page.id,
                name=page.title,
                description=page.description,
                image=meta_image,
                title=f"{self.title}: {page.title}" if self.title else page.title,
                path=page.path,
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
            Output("dashboard-container", "className"),
            Input("theme_selector", "checked"),
        )
        left_side_div_present = any([len(self.pages) > 1, self.pages[0].controls])
        if left_side_div_present:
            clientside_callback(
                ClientsideFunction(namespace="clientside", function_name="collapse_nav_panel"),
                [
                    Output("collapsable-left-side", "is_open"),
                    Output("collapse-icon", "style"),
                    Output("collapse-tooltip", "children"),
                ],
                Input("collapse-icon", "n_clicks"),
                State("collapsable-left-side", "is_open"),
            )

        return html.Div(
            id="dashboard-container",
            children=[
                html.Div(id="vizro_version", children=vizro.__version__, hidden=True),
                dcc.Store(id="vizro_themes", data={"dark": themes.dark, "light": themes.light}),
                ActionLoop._create_app_callbacks(),
                dash.page_container,
            ],
            className=self.theme,
        )

    def _get_page_divs(self, page: Page) -> _PageDivsType:
        # Identical across pages
        dashboard_title = (
            html.H2(id="dashboard-title", children=self.title)
            if self.title
            else html.H2(id="dashboard-title", hidden=True)
        )
        settings = html.Div(
            children=dmc.Switch(
                id="theme_selector",
                checked=self.theme == "vizro_light",
                persistence=True,
                persistence_type="session",
                className="toggle-switch",
            ),
            id="settings",
        )
        logo_img = self._infer_image(filename="logo")
        path_to_logo = get_asset_url(logo_img) if logo_img else None
        logo = html.Img(id="logo", src=path_to_logo, hidden=not path_to_logo)

        # Shared across pages but slightly differ in content. These could possibly be done by a clientside
        # callback instead.
        page_title = html.H2(id="page-title", children=page.title)
        navigation: _NavBuildType = self.navigation.build(active_page_id=page.id)
        nav_bar = navigation["nav-bar"]
        nav_panel = navigation["nav-panel"]

        # Different across pages
        page_content: _PageBuildType = page.build()
        control_panel = page_content["control-panel"]
        page_components = page_content["page-components"]

        return html.Div(
            [dashboard_title, settings, page_title, nav_bar, nav_panel, logo, control_panel, page_components]
        )

    def _arrange_page_divs(self, page_divs: _PageDivsType):
        logo_title = [page_divs["logo"], page_divs["dashboard-title"]]
        page_header_divs = [html.Div(id="logo-and-title", children=logo_title, hidden=_all_hidden(logo_title))]
        left_sidebar_divs = [page_divs["nav-bar"]]
        left_main_divs = [page_divs["nav-panel"], page_divs["control-panel"]]
        right_header_divs = [page_divs["page-title"]]

        # Apply different container position logic based on condition
        if _all_hidden(page_header_divs):
            right_header_divs.append(page_divs["settings"])
        else:
            page_header_divs.append(page_divs["settings"])

        collapsable_icon = (
            html.Div(
                children=[
                    html.Span(
                        id="collapse-icon", children="keyboard_double_arrow_left", className="material-symbols-outlined"
                    ),
                    dbc.Tooltip(
                        id="collapse-tooltip",
                        children="Hide Menu",
                        placement="right",
                        target="collapse-icon",
                    ),
                ],
                className="collapse-icon-div",
            )
            if not _all_hidden([*left_sidebar_divs, *left_main_divs])
            else None
        )

        left_sidebar = html.Div(id="left-sidebar", children=left_sidebar_divs, hidden=_all_hidden(left_sidebar_divs))
        left_main = html.Div(id="left-main", children=left_main_divs, hidden=_all_hidden(left_main_divs))
        left_side = html.Div(id="left-side", children=[left_sidebar, left_main])

        collapsable_left_side = dbc.Collapse(
            id="collapsable-left-side", children=left_side, is_open=True, dimension="width"
        )

        right_header = html.Div(id="right-header", children=right_header_divs)
        right_main = page_divs["page-components"]
        right_side = html.Div(id="right-side", children=[right_header, right_main])

        page_header = html.Div(id="page-header", children=page_header_divs, hidden=_all_hidden(page_header_divs))
        page_main = html.Div(id="page-main", children=[collapsable_left_side, collapsable_icon, right_side])
        return html.Div(children=[page_header, page_main], className="page-container")

    def _make_page_layout(self, page: Page, **kwargs):
        # **kwargs are not used but ensure that unexpected query parameters do not raise errors. See
        # https://github.com/AnnMarieW/dash-multi-page-app-demos/#5-preventing-query-string-errors
        page_divs = self._get_page_divs(page=page)
        page_layout = self._arrange_page_divs(page_divs=page_divs)
        page_layout.id = page.id
        return page_layout

    @staticmethod
    def _make_page_404_layout():
        return html.Div(
            [
                html.Img(src=get_relative_path(f"/{STATIC_URL_PREFIX}/images/errors/error_404.svg")),
                html.Div(
                    [
                        html.Div(
                            children=[
                                html.H3("This page could not be found.", className="heading-3-600"),
                                html.P("Make sure the URL you entered is correct."),
                            ],
                            className="error_text_container",
                        ),
                        dbc.Button(children="Take me home", href=get_relative_path("/")),
                    ],
                    className="error_content_container",
                ),
            ],
            className="page_error_container",
        )

    @staticmethod
    def _infer_image(filename: str):
        valid_extensions = [".apng", ".avif", ".gif", ".jpeg", ".jpg", ".png", ".svg", ".webp"]
        assets_folder = Path(dash.get_app().config.assets_folder)
        if assets_folder.is_dir():
            for path in Path(assets_folder).rglob(f"{filename}.*"):
                if path.suffix in valid_extensions:
                    return str(path.relative_to(assets_folder))
