from __future__ import annotations

import logging
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Iterable, List

import dash
import flask
import plotly.io as pio
from flask_caching import SimpleCache

from vizro._constants import STATIC_URL_PREFIX
from vizro.managers import data_manager, model_manager
from vizro.models import Dashboard

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    # These are built into wsgiref.types for Python 3.11 onwards.
    from _typeshed.wsgi import StartResponse, WSGIEnvironment


class Vizro:
    """The main class of the `vizro` package."""

    def __init__(self, **kwargs):
        """Initializes Dash app, stored in `self.dash`.

        Args:
            **kwargs : Passed through to `Dash.__init__`, e.g. `assets_folder`, `url_base_pathname`. See
                [Dash documentation](https://dash.plotly.com/reference#dash.dash) for possible arguments.

        """
        self.dash = dash.Dash(**kwargs, use_pages=True, pages_folder="", title="Vizro")

        # Include Vizro assets (in the static folder) as external scripts and stylesheets. We extend self.dash.config
        # objects so the user can specify additional external_scripts and external_stylesheets via kwargs.
        vizro_assets_folder = Path(__file__).with_name("static")
        requests_pathname_prefix = self.dash.config.requests_pathname_prefix
        # Exclude vizro/css/figures.css since these are distributed through the vizro._css_dist mechanism.
        # In future we will probably handle all assets this way and none of this code will be required.
        vizro_css = [
            requests_pathname_prefix + path
            for path in self._get_external_assets(vizro_assets_folder, "css")
            if path != "vizro/css/figures.css"
        ]

        # Ensure vizro-bootstrap.min.css is loaded in first to allow overwrites
        vizro_css.sort(key=lambda x: not x.endswith("vizro-bootstrap.min.css"))

        vizro_js = [
            {"src": requests_pathname_prefix + path, "type": "module"}
            for path in self._get_external_assets(vizro_assets_folder, "js")
        ]
        self.dash.config.external_stylesheets.extend(vizro_css)
        self.dash.config.external_scripts.extend(vizro_js)

        # Serve all assets (including files other than css and js) that live in vizro_assets_folder at the
        # route /vizro. Based on code in Dash.init_app that serves assets_folder. This respects the case that the
        # dashboard is not hosted at the root of the server, e.g. http://www.example.com/dashboard/vizro.
        routes_pathname_prefix = self.dash.config.routes_pathname_prefix
        blueprint_prefix = routes_pathname_prefix.replace("/", "_").replace(".", "_")
        self.dash.server.register_blueprint(
            flask.Blueprint(
                f"{blueprint_prefix}vizro_assets",
                self.dash.config.name,
                static_folder=vizro_assets_folder,
                static_url_path=routes_pathname_prefix + STATIC_URL_PREFIX,
            )
        )

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
        # everything else gets overridden in the post-fig creation layout.template update in Graph.__call__ and the
        # clientside theme selector callback.
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
