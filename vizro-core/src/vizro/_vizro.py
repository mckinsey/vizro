from __future__ import annotations

import logging
import warnings
from collections.abc import Iterable
from contextlib import suppress
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Any, TypedDict, cast

import dash
import plotly.io as pio
from dash.development.base_component import ComponentRegistry
from flask_caching import SimpleCache
from packaging.version import parse
from typing_extensions import Self

import vizro
from vizro._constants import VIZRO_ASSETS_PATH
from vizro.managers import data_manager
from vizro.managers._model_manager import FIGURE_MODELS
from vizro.models import Dashboard, Filter
from vizro.models.types import FigureType

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    # These are built into wsgiref.types for Python 3.11 onwards.
    from _typeshed.wsgi import StartResponse, WSGIEnvironment


class Vizro:
    """Vizro app."""

    def __init__(self, **kwargs: Any):
        """Initialize a Vizro app.

        Abstract: Usage documentation
            [How to run or deploy a dashboard](../user-guides/run-deploy.md/#advanced-dockerfile-configuration)

        Keyword Arguments:
            **kwargs: Arbitrary keyword arguments passed through to `Dash`, for example `assets_folder`,
                `url_base_pathname`. See [Dash documentation](https://dash.plotly.com/reference#dash.dash) for all
                possible arguments.
        """
        # Set suppress_callback_exceptions=True for the following reasons:
        # 1. Prevents the following Dash exception when using html.Div as placeholders in build methods:
        #    "Property 'cellClicked' was used with component ID '__input_ag_grid_id' in one of the Input
        #    items of a callback. This ID is assigned to a dash_html_components.Div component in the layout,
        #    which does not support this property."
        # 2. Improves performance by bypassing layout validation.
        self.dash = dash.Dash(
            **kwargs,
            pages_folder="",
            suppress_callback_exceptions=True,
            title="Vizro",
            use_pages=True,
        )

        # When Vizro is used as a framework, we want to include the library and framework resources.
        # Dash serves resources in the order 1. external_stylesheets/scripts; 2. library resources from the
        # ComponentRegistry; 3. resources added by append_css/scripts (which includes user's assets folder).
        # Vizro library resources are already present thanks to ComponentRegistry.registry.add("vizro") in
        # __init__.py. However, since Dash serves these before those added below it means that vizro-bootstrap.css would
        # be served  *after* Vizro library's figures.css. We always want vizro-bootstrap.css to be served first
        # so that it can be overridden. For pure Dash users this is achieved vizro-bootstrap.css is supplied as an
        # external_stylesheet. We could add vizro-bootstrap.css as an external_stylesheet here but it is awkward
        # because it means providing href="_dash-component-suite/..." or using the external_url. Instead we remove
        # Vizro as a component library and then just serve all the resources again. ValueError is suppressed so that
        # repeated calls to Vizro() don't give an error.
        with suppress(ValueError):
            ComponentRegistry.registry.discard("vizro")

        # Automatically detect if Bootstrap CSS is provided in external_stylesheets
        use_vizro_bootstrap = not self._has_bootstrap_css(kwargs.get("external_stylesheets", []))

        # vizro-bootstrap.min.css must be first so that it can be overridden, e.g. by bootstrap_overrides.css.
        # After that, all other items are sorted alphabetically.
        for path in sorted(
            VIZRO_ASSETS_PATH.rglob("*.*"), key=lambda file: (file.name != "vizro-bootstrap.min.css", file)
        ):
            # Skip vizro-bootstrap.min.css if external Bootstrap CSS is provided
            if path.name == "vizro-bootstrap.min.css" and not use_vizro_bootstrap:
                continue

            if path.suffix == ".css":
                self.dash.css.append_css(_make_resource_spec(path))
            elif path.suffix == ".js":
                self.dash.scripts.append_script(_make_resource_spec(path))
            else:
                # map files and fonts and images. These are treated like scripts since this is how Dash handles them.
                # This adds paths to self.dash.registered_paths so that they can be accessed without throwing an
                # error in dash._validate.validate_js_path.
                self.dash.scripts.append_script(_make_resource_spec(path))

        data_manager.cache.init_app(self.dash.server)

    @staticmethod
    def _has_bootstrap_css(external_stylesheets: list[str | dict[str, str]]) -> bool:
        """Detect if Bootstrap CSS is present in external stylesheets.

        Args:
            external_stylesheets: List of external stylesheets. Each entry can be a string (the URL).

        Returns:
            bool: True if Bootstrap CSS is detected, False otherwise
        """

        def _get_url(stylesheet: str | dict[str, str]) -> str:
            """Extract URL from stylesheet."""
            if isinstance(stylesheet, str):
                return stylesheet
            return stylesheet.get("href", "") if isinstance(stylesheet, dict) else ""

        return any("bootstrap" in _get_url(stylesheet).lower() for stylesheet in external_stylesheets)

    def build(self, dashboard: Dashboard) -> Self:
        """Builds the `dashboard`.

        Abstract: Usage documentation
            [How to create a dashboard](../user-guides/dashboard.md)

        Args:
            dashboard (Dashboard): configured dashboard model.

        Returns:
            Built Vizro app.

        """
        # Set global chart template to vizro_light or vizro_dark.
        # The choice between these is generally meaningless because chart colors in the two are identical, and
        # everything else gets overridden in the clientside theme selector callback.
        # Note this setting of global template isn't undone anywhere. If we really wanted to then we could try and
        # put in some teardown code, but it would probably never be 100% reliable. Vizro._reset can't do this well
        # either because it's a staticmethod so can't access self.old_theme (though we could use a global variable to
        # store it). Remember this template setting can't go in run() though since it's needed even in deployment.
        # Probably the best solution if we do want to fix this would be to have two separate paths that are followed:
        # 1. In deployment (or just outside Jupyter?), set the theme here and never revert it.
        # 2. In other contexts, use context manager in run method.
        pio.templates.default = dashboard.theme

        # Note that model instantiation and pre_build are independent of Dash.
        # Build the tree - this attaches _tree to every model
        dashboard = dashboard.__class__.model_validate(dashboard, context={"build_tree": True})

        # Store the tree on the Dash app for runtime access via get_tree().
        # This is the primary way runtime callbacks should access models.
        # Options considered for runtime tree storage, not tried all of course:
        #   1. Dashboard model (self._dashboard) - requires navigating from action to dashboard
        #   2. Vizro instance (self) - no clean way to access from callbacks
        #   3. Flask current_app - probably best alternative, but Dash-level is more appropriate
        #   4. Flask g - per-request, wrong lifecycle for app-scoped tree
        #   5. Dash app (get_app()) - CHOSEN as it seems the correct scope and callback-friendly
        self.dash.vizro_tree = dashboard._tree

        self._pre_build(dashboard)
        self.dash.layout = dashboard.build()

        # Store the dashboard object for later use in the run method.
        self._dashboard = dashboard

        # Add data-bs-theme attribute that is always present, even for pages without theme selector,
        # i.e. the Dash "Loading..." screen.
        bootstrap_theme = dashboard.theme.removeprefix("vizro_")
        self.dash.index_string = self.dash.index_string.replace("<html>", f"<html data-bs-theme='{bootstrap_theme}'>")

        # Note Dash.index uses self.dash.title instead of self.dash.config.title for backwards compatibility.
        if dashboard.title:
            self.dash.title = dashboard.title
        return self

    def run(self, **kwargs: Any):
        """Runs the dashboard locally using the Flask development server.

        Keyword Arguments:
            **kwargs: Arbitrary positional arguments passed through to `Dash.run`, for example `debug`,
                `port`. See [Dash documentation](https://dash.plotly.com/reference#app.run) for all possible
                arguments

        Abstract: Usage documentation
            [How to develop in Python script](../user-guides/run-deploy.md#develop-in-python-script)
        """
        data_manager._frozen_state = True
        # TODO: _frozen_state was on ModelManager - consider if we still need this concept

        # Check if there are undefined captured callables in the dashboard.
        # TODO: In the future we may want to try importing these, do users don't have to create an entirely
        # new dashboard config.
        _undefined_captured_callables: set[str] = {
            model.figure._function
            for model in cast(
                Iterable[FigureType],
                self._dashboard._tree.get_models(model_type=FIGURE_MODELS, root_model=self._dashboard),
            )
            if model.figure._prevent_run
        }

        if _undefined_captured_callables:
            raise ValueError(
                f"""Dashboard contains models with undefined CapturedCallable's: {_undefined_captured_callables}.
Provide a valid import path for these in your dashboard configuration."""
            )

        if kwargs.get("processes", 1) > 1 and type(data_manager.cache.cache) is SimpleCache:
            warnings.warn(
                "`SimpleCache` is designed to support only single process environments. If you would like to use "
                "multiple processes then you should change to a cache that supports it such as `FileSystemCache` or "
                "`RedisCache`."
            )

        self.dash.run(**kwargs)

    @staticmethod
    def _pre_build(dashboard: Dashboard):
        """Runs pre_build method on all models in the dashboard."""
        # Note that a pre_build method can itself add a model (e.g. an Action) to the tree, and so we need to
        # iterate through a snapshot (set/list) rather than the iterator itself or we loop through something that
        # changes size.
        # Any models that are created during the pre-build process *will not* themselves have pre_build run on them.
        # In future may add a second pre_build loop after the first one.

        # TODO: Things fail here because the MM copy of the model is outdated - fix in next iteration
        # This is also the reason why this is not replicated in fake Vizro
        for filter in cast(Iterable[Filter], dashboard._tree.get_models(Filter)):
            # Run pre_build on all filters first, then on all other models. This handles dependency between Filter
            # and Page pre_build and ensures that filters are pre-built before the Page objects that use them.
            # This is important because the Page pre_build method checks whether filters are dynamic or not, which is
            # defined in the filter's pre_build method. Also, the calculation of the data_frame Parameter targets
            # depends on the filter targets, so they should be pre-built after the filters as well.
            # It's also essential for filters to be pre-built before Container.pre_build runs or otherwise
            # control.selector won't be set.
            filter.pre_build()
        for model_id in set(dashboard._tree.iter_model_ids()):
            model = dashboard._tree.get_model(model_id)
            if hasattr(model, "pre_build") and not isinstance(model, Filter):
                model.pre_build()

    def __call__(self, environ: WSGIEnvironment, start_response: StartResponse) -> Iterable[bytes]:
        """Implements WSGI application interface.

        This means you can do e.g. gunicorn app:app without needing to manually define server = app.dash.server.
        """
        return self.dash.server(environ, start_response)

    @staticmethod
    def _reset():
        """Private method that clears all state in the `Vizro` app.

        This deliberately does not clear the data manager cache - see comments in data_manager._clear for
        explanation.
        """

        data_manager._clear()
        dash._callback.GLOBAL_CALLBACK_LIST = []
        dash._callback.GLOBAL_CALLBACK_MAP = {}
        dash._callback.GLOBAL_INLINE_SCRIPTS = []
        dash.page_registry.clear()
        dash._pages.CONFIG.clear()
        dash._pages.CONFIG.__dict__.clear()
        # To reset state to as if Vizro() hadn't been ran we need to make sure vizro is in the component
        # registry. This is a set so it's not possible to duplicate the entry. This handles the very edge case that
        # probably only occurs in our tests where someone does import vizro; Vizro(); Dash(), which means the Vizro
        # library components are no longer available. This would work correctly with import vizro; Vizro();
        # Vizro.reset(); Dash().
        ComponentRegistry.registry.add("vizro")


class _ResourceType(TypedDict, total=False):
    """Dash specification for a CSS or JS resource. Based on dash.resources.ResourceType.

    Dash uses relative_package_path when serve_locally=False (the default) in the Dash instantiation. When
    serve_locally=True then, where defined, external_url will be used instead. Only namespace and relative_package_path
    and required keys.
    """

    namespace: str
    relative_package_path: str
    external_url: str
    dynamic: bool
    dev_package_path: str
    absolute_path: str
    asset_path: str
    external_only: bool
    filepath: str
    dev_only: bool
    # async is a Python keyword so would need to use alternative functional TypedDict syntax for this to work. Since we
    # don't use it anywhere we keep using this TypedDict class syntax and just don't define it here.
    # async: bool | Literal["eager", "lazy"]


def _make_resource_spec(path: Path) -> _ResourceType:
    # For dev versions, a branch or tag called e.g. 0.1.20.dev0 does not exist and so won't work with the CDN. We point
    # to main instead, but this can be manually overridden to the current feature branch name if required.
    # This would only be the case where you need to test something with serve_locally=False and have changed
    # assets compared to main. In this case you need to push your assets changes to remote for the CDN to update,
    # and it might also be necessary to clear the CDN cache: https://www.jsdelivr.com/tools/purge.
    _git_branch = vizro.__version__ if not parse(vizro.__version__).is_devrelease else "main"
    BASE_EXTERNAL_URL = f"https://cdn.jsdelivr.net/gh/mckinsey/vizro@{_git_branch}/vizro-core/src/vizro/"

    # Get path relative to the vizro package root, where this file resides.
    # This must be a posix path to work on Windows, so that we convert all \ to / and routing works correctly.
    # See https://github.com/mckinsey/vizro/issues/836.
    relative_path = PurePosixPath(path.relative_to(Path(__file__).parent))

    resource_spec: _ResourceType = {"namespace": "vizro", "relative_package_path": str(relative_path)}

    if relative_path.suffix in {".css", ".js"}:
        # The CDN automatically minifies CSS and JS files which aren't already minified. Convert "filename.css" to
        # "filename.min.css" for these files.
        external_relative_path = (
            relative_path
            if ".min" in relative_path.suffixes
            else relative_path.with_suffix(f".min{relative_path.suffix}")
        )

        resource_spec["external_url"] = f"{BASE_EXTERNAL_URL}{external_relative_path}"
    else:
        # Files that aren't css or js cannot be minified, do not have external_url and set dynamic=True to ensure that
        # the file isn't included in the HTML source. See https://github.com/plotly/dash/pull/1078.
        # map and font files are served through the CDN in the same way as the CSS files but external_url is
        # irrelevant here. The way the file is requested is through a relative url("./fonts/...") in the requesting
        # CSS file. When the CSS file is served from the CDN then this will refer to the font file also on the CDN.
        resource_spec["dynamic"] = True

    return resource_spec


"""FURTHER PLAN OF ACTION

- [DONE] convert MM from dictionary to just tree reference, populate at correct moment
- [DONE] replace all methods with tree lookups
- [DONE] remove the MM from its global state
  - Global model_manager singleton no longer imported or used in src/
  - Build-time: models access tree via self._tree
  - Runtime (callbacks): models access tree via get_tree() -> dash.get_app().vizro_tree
  - Tree stored on Dash app instance (Option 5)
- [TODO] update tests to work without global model_manager
- [TODO] clean up ModelManager class and deprecation shims in _model_manager.py
- [TODO] Dash PAGE_REGISTRY is global and not cleared between
  dashboard instances, causing "duplicate paths" error when building a second dashboard in the same
  notebook.
"""
