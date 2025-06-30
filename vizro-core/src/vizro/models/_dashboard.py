from __future__ import annotations

import base64
import logging
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Literal, Optional, cast

import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import plotly.io as pio
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
from dash.development.base_component import Component
from pydantic import AfterValidator, BeforeValidator, Field, ValidationInfo
from typing_extensions import TypedDict

import vizro
from vizro._constants import MODULE_PAGE_404, VIZRO_ASSETS_PATH
from vizro._themes.template_dashboard_overrides import dashboard_overrides
from vizro.actions._action_loop._action_loop import ActionLoop
from vizro.models import Navigation, Tooltip, VizroBaseModel
from vizro.models._models_utils import _log_call
from vizro.models._navigation._navigation_utils import _NavBuildType
from vizro.models._tooltip import coerce_str_to_tooltip

if TYPE_CHECKING:
    from vizro.models import Page
    from vizro.models._page import _PageBuildType

logger = logging.getLogger(__name__)


def _all_hidden(components: list[Component]):
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
        "logo-dark": html.Div,
        "logo-light": html.Div,
        "control-panel": html.Div,
        "page-components": html.Div,
    },
)


def set_navigation_pages(navigation: Optional[Navigation], info: ValidationInfo) -> Optional[Navigation]:
    if "pages" not in info.data:
        return navigation

    navigation = navigation or Navigation()
    navigation.pages = navigation.pages or [page.id for page in info.data["pages"]]
    return navigation


class Dashboard(VizroBaseModel):
    """Vizro Dashboard to be used within [`Vizro`][vizro._vizro.Vizro.build].

    Args:
        pages (list[Page]): See [`Page`][vizro.models.Page].
        theme (Literal["vizro_dark", "vizro_light"]): Layout theme to be applied across dashboard.
            Defaults to `vizro_dark`.
        navigation (Navigation): See [`Navigation`][vizro.models.Navigation]. Defaults to `None`.
        title (str): Dashboard title to appear on every page on top left-side. Defaults to `""`.
        description (Optional[Tooltip]): Optional markdown string that adds an icon next to the title.
            Hovering over the icon shows a tooltip with the provided description. This also sets the page's meta
            tags. Defaults to `None`.

    """

    pages: list[Page]
    theme: Literal["vizro_dark", "vizro_light"] = Field(
        default="vizro_dark", description="Theme to be applied across dashboard. Defaults to `vizro_dark`."
    )
    navigation: Annotated[
        Optional[Navigation], AfterValidator(set_navigation_pages), Field(default=None, validate_default=True)
    ]
    title: str = Field(default="", description="Dashboard title to appear on every page on top left-side.")
    # TODO: ideally description would have json_schema_input_type=Union[str, Tooltip] attached to the BeforeValidator,
    #  but this requires pydantic >= 2.9.
    description: Annotated[
        Optional[Tooltip],
        BeforeValidator(coerce_str_to_tooltip),
        Field(
            default=None,
            description="""Optional markdown string that adds an icon next to the title.
            Hovering over the icon shows a tooltip with the provided description. This also sets the page's meta
            tags. Defaults to `None`.""",
        ),
    ]

    @_log_call
    def pre_build(self):
        self._validate_logos()

        # Setting order here ensures that the pages in dash.page_registry preserves the order of the list[Page].
        # For now the homepage (path /) corresponds to self.pages[0].
        # Note redirect_from=["/"] doesn't work and so the / route must be defined separately.
        self.pages[0].path = "/"
        meta_img = self._infer_image("app") or self._infer_image("logo") or self._infer_image("logo_dark")
        dashboard_description_text = self.description.text if self.description else None

        for order, page in enumerate(self.pages):
            # Dash also uses the dashboard-level description passed into Dash() as the default for page-level
            # descriptions, but this would involve extracting dashboard.description and inserting it into the Dash app
            # config in Vizro.build. What we do here is simpler but has the same effect.
            dash.register_page(
                module=page.id,
                name=page.title,
                description=page.description.text if page.description else dashboard_description_text,
                image=meta_img,
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
            ClientsideFunction(namespace="dashboard", function_name="update_dashboard_theme"),
            # This currently doesn't do anything, but we need to define an Output such that the callback is triggered.
            Output("dashboard-container", "className"),
            Input("theme-selector", "value"),
        )
        left_side_div_present = any([len(self.pages) > 1, self.pages[0].controls])
        if left_side_div_present:
            clientside_callback(
                ClientsideFunction(namespace="dashboard", function_name="collapse_nav_panel"),
                [
                    Output("collapsible-left-side", "is_open"),
                    Output("collapse-icon", "style"),
                    Output("collapse-tooltip", "children"),
                ],
                Input("collapse-icon", "n_clicks"),
                State("collapsible-left-side", "is_open"),
            )

        layout = html.Div(
            id="dashboard-container",
            children=[
                html.Div(id="vizro_version", children=vizro.__version__, hidden=True),
                dcc.Store(
                    id="vizro_themes",
                    data={
                        "vizro_dark": pio.templates.merge_templates("vizro_dark", dashboard_overrides),
                        "vizro_light": pio.templates.merge_templates("vizro_light", dashboard_overrides),
                    },
                ),
                ActionLoop._create_app_callbacks(),
                dash.page_container,
            ],
        )

        # children=[layout] as a list rather than children=layout, so that app.dash.layout.children.append works to
        # easily add things to the Dash layout. In future we might have a neater function for patching components into
        # the Dash layout in which case this could change.
        return dmc.MantineProvider(
            children=[layout],
            # Use the `theme` to style all Mantine components with a Vizro theme. For more info see https://www.dash-mantine-components.com/components/mantineprovider
            theme={"primaryColor": "gray"},
        )

    def _validate_logos(self):
        logo_img = self._infer_image(filename="logo")
        logo_dark_img = self._infer_image(filename="logo_dark")
        logo_light_img = self._infer_image(filename="logo_light")

        if logo_dark_img and logo_light_img:
            if logo_img:
                raise ValueError(
                    "Cannot provide `logo` together with both `logo_dark` and `logo_light`. "
                    "Please provide either `logo`, or both `logo_dark` and `logo_light`."
                )
        elif logo_dark_img or logo_light_img:
            raise ValueError(
                "Both `logo_dark` and `logo_light` must be provided together. Please provide either both or neither."
            )

    def _get_page_divs(self, page: Page) -> _PageDivsType:
        # Identical across pages
        dashboard_description = self.description.build().children if self.description else [None]
        dashboard_title = (
            html.H2(id="dashboard-title", children=[self.title, *dashboard_description])
            if self.title
            else html.H2(id="dashboard-title", hidden=True)
        )
        settings = html.Div(
            children=dbc.Switch(
                id="theme-selector",
                value=self.theme == "vizro_light",
                persistence=True,
                persistence_type="session",
            ),
            id="settings",
        )

        logo_img = self._infer_image(filename="logo")
        logo_dark_img = self._infer_image(filename="logo_dark")
        logo_light_img = self._infer_image(filename="logo_light")

        path_to_logo = get_asset_url(logo_img) if logo_img else None
        path_to_logo_dark = get_asset_url(logo_dark_img) if logo_dark_img else None
        path_to_logo_light = get_asset_url(logo_light_img) if logo_light_img else None

        logo = html.Img(id="logo", src=path_to_logo, hidden=not path_to_logo)
        logo_dark = html.Img(id="logo-dark", src=path_to_logo_dark, hidden=not path_to_logo_dark)
        logo_light = html.Img(id="logo-light", src=path_to_logo_light, hidden=not path_to_logo_light)

        # Shared across pages but slightly differ in content. These could possibly be done by a clientside
        # callback instead.
        page_description = page.description.build().children if page.description else [None]
        page_title = html.H2(
            id="page-title", children=[html.Span(page.title, id=f"{page.id}_title"), *page_description]
        )
        # cannot actually be None if you check pages and layout field together
        navigation: _NavBuildType = cast(Navigation, self.navigation).build(active_page_id=page.id)
        nav_bar = navigation["nav-bar"]
        nav_panel = navigation["nav-panel"]

        # Different across pages
        page_content: _PageBuildType = page.build()
        control_panel = page_content["control-panel"]
        page_components = page_content["page-components"]

        return html.Div(
            [
                dashboard_title,
                settings,
                page_title,
                nav_bar,
                nav_panel,
                logo,
                logo_dark,
                logo_light,
                control_panel,
                page_components,
            ]
        )

    def _arrange_page_divs(self, page_divs: _PageDivsType):
        logo_title = [page_divs["logo"], page_divs["logo-dark"], page_divs["logo-light"], page_divs["dashboard-title"]]
        page_header_divs = [html.Div(id="logo-and-title", children=logo_title, hidden=_all_hidden(logo_title))]
        left_sidebar_divs = [page_divs["nav-bar"]]
        left_main_divs = [page_divs["nav-panel"], page_divs["control-panel"]]
        right_header_divs = [page_divs["page-title"]]

        # Apply different container position logic based on condition
        if _all_hidden(page_header_divs):
            right_header_divs.append(page_divs["settings"])
        else:
            page_header_divs.append(page_divs["settings"])

        collapsible_icon = (
            html.Div(
                children=[
                    html.Span(
                        id="collapse-icon", children="keyboard_arrow_left", className="material-symbols-outlined"
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

        collapsible_left_side = dbc.Collapse(
            id="collapsible-left-side", children=left_side, is_open=True, dimension="width"
        )

        right_header = html.Div(id="right-header", children=right_header_divs)
        right_main = page_divs["page-components"]
        right_side = html.Div(id="right-side", children=[right_header, right_main])

        page_header = html.Div(id="page-header", children=page_header_divs, hidden=_all_hidden(page_header_divs))
        page_main = html.Div(id="page-main", children=[collapsible_left_side, collapsible_icon, right_side])
        return html.Div(children=[page_header, page_main], className="page-container")

    def _make_page_layout(self, page: Page, **kwargs):
        # **kwargs are not used but ensure that unexpected query parameters do not raise errors. See
        # https://github.com/AnnMarieW/dash-multi-page-app-demos/#5-preventing-query-string-errors
        page_divs = self._get_page_divs(page=page)
        page_layout = self._arrange_page_divs(page_divs=page_divs)
        page_layout.id = page.id
        return page_layout

    def _make_page_404_layout(self):
        # The svg file is available through the _dash-component-suites/vizro route, as used in Dash's
        # _relative_url_path, but that feels too private to access directly. Hence read the file in directly rather
        # than referring to its path.
        error_404_svg = base64.b64encode((VIZRO_ASSETS_PATH / "images/error_404.svg").read_bytes()).decode("utf-8")
        return html.Div(
            [
                # Theme switch is added such that the 404 page has the same theme as the user-selected one.
                dbc.Switch(
                    id="theme-selector",
                    value=self.theme == "vizro_light",
                    persistence=True,
                    persistence_type="session",
                ),
                html.Img(src=f"data:image/svg+xml;base64,{error_404_svg}"),
                html.H3("This page could not be found."),
                html.P("Make sure the URL you entered is correct."),
                dbc.Button(children="Take me home", href=get_relative_path("/"), class_name="mt-4"),
            ],
            className="d-flex flex-column align-items-center justify-content-center min-vh-100",
        )

    @staticmethod
    def _infer_image(filename: str):
        valid_extensions = [".apng", ".avif", ".gif", ".jpeg", ".jpg", ".png", ".svg", ".webp"]
        assets_folder = Path(dash.get_app().config.assets_folder)
        if assets_folder.is_dir():
            for path in Path(assets_folder).rglob(f"{filename}.*"):
                if path.suffix in valid_extensions:
                    # Return path as posix so image source comes out correctly on Windows.
                    return path.relative_to(assets_folder).as_posix()
