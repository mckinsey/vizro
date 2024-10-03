from __future__ import annotations

import logging
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Iterable, List

import dash
import plotly.io as pio
from flask_caching import SimpleCache

from vizro._constants import STATIC_URL_PREFIX
from vizro.managers import data_manager, model_manager
from vizro.models import Dashboard

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    # These are built into wsgiref.types for Python 3.11 onwards.
    from _typeshed.wsgi import StartResponse, WSGIEnvironment


_VIZRO_ASSETS_PATH = Path(__file__).with_name("static")

# Files needed to use Vizro as a library (not a framework), e.g. in a pure Dash app. These files are automatically
# served on import of vizro, regardless of whether the Vizro class or any other bits are used.
# This list should be kept to the bare minimum so we don't insert any more than the minimum required CSS on pure Dash
# apps.
# At the moment the only library components we support just are KPI cards, which just need CSS files.
# Just here for consistency. We don't currently provide any library JS, but this would be the case if there's JS
# required for any components that can be used outside Vizro framework.
_library_css_files = {
    _VIZRO_ASSETS_PATH / "css/figures.css",
    _VIZRO_ASSETS_PATH / "css/fonts/material-symbols-outlined.woff2",
}
_library_js_files = set()


class Vizro:
    """The main class of the `vizro` package."""

    def __init__(self, **kwargs):
        """Initializes Dash app, stored in `self.dash`.

        Args:
            **kwargs : Passed through to `Dash.__init__`, e.g. `assets_folder`, `url_base_pathname`. See
                [Dash documentation](https://dash.plotly.com/reference#dash.dash) for possible arguments.

        """
        # Setting suppress_callback_exceptions=True for the following reasons:
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

        # Add static assets that were not already included in the library. These are registered only when Vizro() is
        # called, i.e. when Vizro is used as a framework.
        for path in set(_VIZRO_ASSETS_PATH.rglob("*")) - _library_css_files - _library_js_files:
            if path.suffix == ".css":
                self.dash.css.append_css(_make_resource_spec(path))
            elif path.suffix == ".js":
                self.dash.scripts.append_script(_make_resource_spec(path))
            else:
                # map files and fonts and images. These are treated like scripts since this is how Dash handles them.
                # This adds paths to self.dash.registered_paths so that they can be accessed without throwing an
                # error dash._validate.validate_js_path.
                self.dash.scripts.append_script(_make_resource_spec(path, custom_type=True))

        data_manager.cache.init_app(self.dash.server)

    def build(self, dashboard: Dashboard):
        """Builds the `dashboard`.

        Args:
            dashboard (Dashboard): [`Dashboard`][vizro.models.Dashboard] object.

        Returns:
            self: Vizro app

        """
        # Note Dash.index uses self.dash.title instead of self.dash.app.config.title.
        if dashboard.title:
            self.dash.title = dashboard.title

        # Set global template to vizro_light or vizro_dark.
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
        self._pre_build()

        self.dash.layout = dashboard.build()

        return self

    def run(self, *args, **kwargs):  # if type annotated, mkdocstring stops seeing the class
        """Runs the dashboard.

        Args:
            *args : Passed through to `dash.run`.
            **kwargs : Passed through to `dash.run`.

        """
        data_manager._frozen_state = True
        model_manager._frozen_state = True

        if kwargs.get("processes", 1) > 1 and type(data_manager.cache.cache) is SimpleCache:
            warnings.warn(
                "`SimpleCache` is designed to support only single process environments. If you would like to use "
                "multiple processes then you should change to a cache that supports it such as `FileSystemCache` or "
                "`RedisCache`."
            )

        self.dash.run(*args, **kwargs)

    @staticmethod
    def _pre_build():
        """Runs pre_build method on all models in the model_manager."""
        # Note that a pre_build method can itself add a model (e.g. an Action) to the model manager, and so we need to
        # iterate through set(model_manager) rather than model_manager itself or we loop through something that
        # changes size.
        # Any models that are created during the pre-build process *will not* themselves have pre_build run on them.
        # In future may add a second pre_build loop after the first one.
        for model_id in set(model_manager):
            model = model_manager[model_id]
            if hasattr(model, "pre_build"):
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
        model_manager._clear()
        dash._callback.GLOBAL_CALLBACK_LIST = []
        dash._callback.GLOBAL_CALLBACK_MAP = {}
        dash._callback.GLOBAL_INLINE_SCRIPTS = []
        dash.page_registry.clear()
        dash._pages.CONFIG.clear()
        dash._pages.CONFIG.__dict__.clear()

    @staticmethod
    def _get_external_assets(folder: Path, extension: str) -> List[str]:
        """Returns a list of paths to assets with given `extension` in `folder`, prefixed with `STATIC_URL_PREFIX`.

        e.g. with STATIC_URL_PREFIX="vizro", extension="css", folder="/path/to/vizro/vizro-core/src/vizro/static",
        we will get ["vizro/css/accordion.css", "vizro/css/button.css", ...].
        """
        return sorted(
            (STATIC_URL_PREFIX / path.relative_to(folder)).as_posix() for path in folder.rglob(f"*.{extension}")
        )


def _make_resource_spec(path: Path, custom_type: bool = False):
    # TODO: proper docstring
    # Create a resource specification for Dash.
    # Dash uses relative_package_path when serve_locally=False (the default) in the Dash instantiation.
    # When serve_locally=True then, where defined, external_url will be used instead.
    # Set custom_type=True to handle files that aren't css or js, e.g. map or image or font files. These need to be
    # registered so that Dash validation doesn't throw an error, but they shouldn't be included in the HTML source.

    # For dev versions, a branch or tag called e.g. 0.1.20.dev0 does not exist and so won't work with the CDN. We point
    # to main instead, but this can be manually overridden to the current feature branch name if required.
    from vizro import __version__

    _git_branch = __version__ if "dev" not in __version__ else "main"
    BASE_EXTERNAL_URL = f"https://cdn.jsdelivr.net/gh/mckinsey/vizro@{_git_branch}/vizro-core/src/vizro/"

    # Get path relative to the vizro package root, where this file resides.
    relative_path = path.relative_to(Path(__file__).parent)

    resource_spec = {
        "namespace": "vizro",
        "relative_package_path": str(relative_path),
    }

    if not custom_type:
        # The CDN automatically minifies CSS and JS files which aren't already minified.
        if ".min" not in relative_path.suffixes:
            # Convert "filename.css" to "filename.min.css".
            new_suffix = f".min{relative_path.suffix}"
            external_url = f"{BASE_EXTERNAL_URL}{relative_path.with_suffix(new_suffix)}"
        else:
            external_url = f"{BASE_EXTERNAL_URL}{relative_path}"
            # TODO: check these are strings.
            # TODO: write proper tests.
        resource_spec["external_url"] = external_url
    else:
        # Files that aren't css or js cannot be minified, do not have external_url and set dynamic=True to ensure that
        # the file isn't included in the HTML source. See https://github.com/plotly/dash/pull/1078.
        # map and font files  are be served through the CDN in the same way as the CSS files but external_url is
        # irrelevant here. The way the file is requested is through a relative url("./fonts/...") in the requesting
        # CSS file. When the CSS file is served from the CDN then this will refer to the font file also on the CDN.
        resource_spec["dynamic"] = True

    return resource_spec
