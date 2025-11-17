from __future__ import annotations

import base64
import logging
from collections.abc import Iterable
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Literal, Optional, Union, cast

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
from vizro._themes._templates import dashboard_overrides
from vizro.managers import model_manager
from vizro.models import Navigation, Tooltip, VizroBaseModel
from vizro.models._action._action import _BaseAction
from vizro.models._controls import Filter, Parameter
from vizro.models._models_utils import _all_hidden, _log_call, warn_description_without_title
from vizro.models._navigation._navigation_utils import _NavBuildType
from vizro.models._tooltip import coerce_str_to_tooltip
from vizro.models.types import ControlType

if TYPE_CHECKING:
    from vizro.models import Page
    from vizro.models._page import _PageBuildType

logger = logging.getLogger(__name__)


# This is just used for type checking. Ideally it would inherit from some dash.development.base_component.Component
# (e.g. html.Div) as well as TypedDict, but that's not possible, and Dash does not have typing support anyway. When
# this type is used, the object is actually still a dash.development.base_component.Component, but this makes it easier
# to see what contract the component fulfills by making the expected keys explicit.
_InnerPageContentType = TypedDict(
    "_InnerPageContentType",
    {
        "header-left": html.Div,
        "header-right": html.Div,
        "page-header": html.Div,
        "page-components": html.Div,
        "nav-bar": dbc.Navbar,
        "nav-control-panel": html.Div,
    },
)

_OuterPageContentType = TypedDict(
    "_OuterPageContentType",
    {
        "header": html.Div,
        "nav-bar": dbc.Navbar,
        "right-side": html.Div,
        "collapse-left-side": dbc.Collapse,
        "collapse-icon-outer": html.Div,
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

    Abstract: Usage documentation
        [How to create a dashboard](../user-guides/dashboard.md)

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
        AfterValidator(warn_description_without_title),
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

        # Define callbacks when the dashboard is built but not every time the page is changed.
        for action in cast(Iterable[_BaseAction], model_manager._get_models(_BaseAction)):
            action._define_callback()

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
                    Output("collapse-left-side", "is_open"),
                    Output("collapse-icon", "style"),
                    Output("collapse-tooltip", "children"),
                ],
                Input("collapse-icon", "n_clicks"),
                State("collapse-left-side", "is_open"),
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
                dcc.Store(
                    id="vizro_controls_store",
                    data={
                        control.id: {"originalValue": control.selector.value, "pageId": page.id}
                        for page in self.pages
                        for control in cast(
                            Iterable[ControlType],
                            [*model_manager._get_models(Parameter, page), *model_manager._get_models(Filter, page)],
                        )
                    },
                ),
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

    def _get_logo_images(self):
        """Infers logo, logo_dark, and logo_light images and returns their corresponding html.Img components."""
        logo_img = self._infer_image(filename="logo")
        logo_dark_img = self._infer_image(filename="logo_dark")
        logo_light_img = self._infer_image(filename="logo_light")

        path_to_logo = get_asset_url(logo_img) if logo_img else None
        path_to_logo_dark = get_asset_url(logo_dark_img) if logo_dark_img else None
        path_to_logo_light = get_asset_url(logo_light_img) if logo_light_img else None

        logo = html.A(html.Img(id="logo", src=path_to_logo), href=get_relative_path("/"), hidden=not path_to_logo)
        logo_dark = html.A(
            html.Img(id="logo-dark", src=path_to_logo_dark), href=get_relative_path("/"), hidden=not path_to_logo_dark
        )
        logo_light = html.A(
            html.Img(id="logo-light", src=path_to_logo_light),
            href=get_relative_path("/"),
            hidden=not path_to_logo_light,
        )

        return logo, logo_dark, logo_light

    def _inner_page(self, page: Page) -> _InnerPageContentType:
        """Builds and returns the main layout components for a dashboard page as a dictionary.

        Args:
            page (Page): The page object for which to build the layout components.

        Returns:
            _InnerPageContentType: A dictionary with keys for header components, navigation,
                controls, and content components for the page.
        """
        # Shared across pages but slightly differ in content. Could possibly be done by a clientside callback.
        page_description = page.description.build().children if page.description else [None]
        page_title = html.H2(
            id="page-title", children=[html.Span(page.title, id=f"{page.id}_title"), *page_description]
        )
        navigation: _NavBuildType = cast(Navigation, self.navigation).build(active_page_id=page.id)
        nav_bar = navigation["nav-bar"]
        nav_panel = navigation["nav-panel"]

        # Different across pages
        page_content: _PageBuildType = page.build()
        control_panel = page_content["control-panel"]
        page_components = page_content["page-components"]

        # Identical across pages
        dashboard_description = self.description.build().children if self.description else [None]
        dashboard_title = (
            html.H2(id="dashboard-title", children=[self.title, *dashboard_description])
            if self.title
            else html.H2(id="dashboard-title", hidden=True)
        )

        logo, logo_dark, logo_light = self._get_logo_images()
        custom_header_content = self.custom_header()
        custom_header = html.Div(
            id="header-custom", children=custom_header_content, hidden=_all_hidden(custom_header_content)
        )

        header_left_content = [logo, logo_dark, logo_light, dashboard_title]
        header_left = html.Div(id="header-left", children=header_left_content, hidden=_all_hidden(header_left_content))
        header_right_content = [custom_header]

        # Construct required parent containers
        page_header_content = [page_title]
        page_header = html.Div(id="page-header", children=page_header_content)

        has_page_controls = bool(
            [*model_manager._get_models(Parameter, page), *model_manager._get_models(Filter, page)]
        )

        # Page header controls that appear on the right side of the header.
        action_progress_indicator = dcc.Loading(
            id="action-progress-indicator",
            delay_show=300,
            delay_hide=300,
            custom_spinner=html.Span(
                className="material-symbols-outlined progress-indicator",
                # Keep "progress_activity" children so the CSS spinner can render/display correctly.
                children="progress_activity",
            ),
            # Placeholder div is added as used as target from actions to show loading indicator.
            children=html.Div(id="action-progress-indicator-placeholder"),
        )
        reset_controls_button = dbc.Button(
            id=f"{page.id}_reset_button",
            children=[
                html.Span("reset_settings", className="material-symbols-outlined tooltip-icon"),
                dbc.Tooltip(children="Reset all page controls", target=f"{page.id}_reset_button"),
            ],
            class_name="btn-circular",
        )
        theme_switch = dbc.Switch(
            id="theme-selector", value=self.theme == "vizro_light", persistence=True, persistence_type="session"
        )
        header_controls = html.Div(
            id="header-controls",
            children=[
                action_progress_indicator,
                # Show the reset icon button in the header when there are page controls but no control panel.
                reset_controls_button if has_page_controls and _all_hidden(control_panel) else None,
                theme_switch,
            ],
        )

        # Apply different container position logic based on condition
        if _all_hidden(header_left_content + header_right_content):
            page_header_content.append(header_controls)
        else:
            header_right_content.append(header_controls)

        header_right = html.Div(
            id="header-right",
            children=header_right_content,
            hidden=_all_hidden(header_right_content),
        )

        # Show reset button with the icon in the control panel when both page controls and control panel exist.
        if has_page_controls and not _all_hidden(control_panel):
            icon = html.Span("reset_settings", className="material-symbols-outlined tooltip-icon")
            text = html.Span("Reset controls", className="btn-text")

            control_panel.children.append(
                dbc.Button(id=f"{page.id}_reset_button", children=[icon, text]),
            )

        nav_control_panel_content = [nav_panel, control_panel]
        nav_control_panel = html.Div(
            id="nav-control-panel", children=nav_control_panel_content, hidden=_all_hidden(nav_control_panel_content)
        )

        return html.Div(
            [
                header_left,
                header_right,
                page_header,
                page_components,
                nav_bar,
                nav_control_panel,
            ]
        )

    def _outer_page(self, inner_page: _InnerPageContentType) -> _OuterPageContentType:
        """Assembles the outer layout containers for a dashboard page using the components from inner_page.

        Args:
            inner_page (_InnerPageContentType): Dictionary of main page components built by inner_page().

        Returns:
            _OuterPageContentType: A dictionary with the outer containers, including header, right-side,
                left-side (collapsible), and the collapse icon container.
        """
        # Inner page containers used to construct outer page containers
        header_left = inner_page["header-left"]
        header_right = inner_page["header-right"]
        page_header = inner_page["page-header"]
        page_components = inner_page["page-components"]
        nav_bar = inner_page["nav-bar"]
        nav_control_panel = inner_page["nav-control-panel"]

        # Construct outer page containers
        header = html.Div(
            id="header",
            children=[header_left, header_right],
            hidden=_all_hidden([header_left, header_right]),
            className="no-left" if _all_hidden(header_left) else "",
        )
        right_side = html.Div(id="right-side", children=[page_header, page_components])
        collapse_left_side = dbc.Collapse(
            id="collapse-left-side",
            children=html.Div(id="left-side", children=[nav_control_panel]),
            is_open=True,
            dimension="width",
        )
        collapse_icon_outer = html.Div(
            children=[
                html.Span(id="collapse-icon", children="keyboard_arrow_left", className="material-symbols-outlined"),
                dbc.Tooltip(
                    id="collapse-tooltip",
                    children="Hide Menu",
                    placement="right",
                    target="collapse-icon",
                ),
            ],
            id="collapse-icon-outer",
            hidden=_all_hidden([nav_control_panel]),
        )
        return html.Div(
            [
                header,
                nav_bar,
                right_side,
                collapse_left_side,
                collapse_icon_outer,
            ]
        )

    def _arrange_page(self, outer_page: _OuterPageContentType):
        """Combines the outer containers into the final dashboard page layout.

        Args:
            outer_page (_OuterPageContentType): Dictionary of outer containers built by outer_page().

        Returns:
            html.Div: The complete Dash layout for the page, ready to render.
        """
        nav_bar = outer_page["nav-bar"]
        collapse_left_side = outer_page["collapse-left-side"]
        collapse_icon_outer = outer_page["collapse-icon-outer"]
        right_side = outer_page["right-side"]
        header = outer_page["header"]

        page_main = html.Div(id="page-main", children=[nav_bar, collapse_left_side, collapse_icon_outer, right_side])
        page_main_outer = html.Div(
            children=[header, page_main],
            className="page-main-outer no-left" if _all_hidden(collapse_icon_outer) else "page-main-outer",
        )
        return page_main_outer

    def _make_page_layout(self, page: Page, **kwargs):
        # **kwargs are not used but ensure that unexpected query parameters do not raise errors. See
        # https://github.com/AnnMarieW/dash-multi-page-app-demos/#5-preventing-query-string-errors
        inner_page = self._inner_page(page=page)
        outer_page = self._outer_page(inner_page=inner_page)
        page_layout = self._arrange_page(outer_page=outer_page)
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

    @staticmethod
    def custom_header() -> Union[Component, list[Component]]:
        """Returns a Dash component or list of components for the dashboard header's custom content area.

        Override this method in your subclass to add custom content that will appear to the left of the theme switch.
        """
        return []
