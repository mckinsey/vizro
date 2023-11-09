import logging
from pathlib import Path
from typing import List

import dash
import flask

from vizro._constants import STATIC_URL_PREFIX
from vizro.managers import data_manager, model_manager
from vizro.models import Dashboard

logger = logging.getLogger(__name__)


class Vizro:
    """The main class of the `vizro` package."""

    def __init__(self, **kwargs):
        """Initializes Dash app, stored in `self.dash`.

        Args:
            kwargs: Passed through to `Dash.__init__`, e.g. `assets_folder`, `url_base_pathname`. See
                [Dash documentation](https://dash.plotly.com/reference#dash.dash) for possible arguments.
        """
        self.dash = dash.Dash(**kwargs, use_pages=True, pages_folder="")

        # Include Vizro assets (in the static folder) as external scripts and stylesheets. We extend self.dash.config
        # objects so the user can specify additional external_scripts and external_stylesheets via kwargs.
        vizro_assets_folder = Path(__file__).with_name("static")
        static_url_path = self.dash.config.requests_pathname_prefix + STATIC_URL_PREFIX
        vizro_css = self._get_external_assets(static_url_path, vizro_assets_folder, "css")
        vizro_js = [
            {"src": path, "type": "module"}
            for path in self._get_external_assets(static_url_path, vizro_assets_folder, "js")
        ]
        self.dash.config.external_stylesheets.extend(vizro_css)
        self.dash.config.external_scripts.extend(vizro_js)

        # Serve all assets (including files other than css and js) that live in vizro_assets_folder at the
        # route /vizro. Based on code in Dash.init_app that serves assets_folder. This respects the case that the
        # dashboard is not hosted at the root of the server, e.g. http://www.example.com/dashboard/vizro.
        blueprint_prefix = self.dash.config.routes_pathname_prefix.replace("/", "_").replace(".", "_")
        self.dash.server.register_blueprint(
            flask.Blueprint(
                f"{blueprint_prefix}vizro_assets",
                self.dash.config.name,
                static_folder=vizro_assets_folder,
                static_url_path=static_url_path,
            )
        )

    def build(self, dashboard: Dashboard):
        """Builds the dashboard.

        Args:
            dashboard (Dashboard): [`Dashboard`][vizro.models.Dashboard] object.

        Returns:
            Vizro: App object
        """
        # Note that model instantiation and pre_build are independent of Dash.
        self._pre_build()

        self.dash.layout = dashboard.build()

        return self

    def run(self, *args, **kwargs):  # if type annotated, mkdocstring stops seeing the class
        """Runs the dashboard.

        Args:
            args: Passed through to `dash.run`.
            kwargs: Passed through to `dash.run`.
        """
        data_manager._frozen_state = True
        model_manager._frozen_state = True

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

    @staticmethod
    def _reset():
        """Private method that clears all state in the vizro app."""
        data_manager._clear()
        model_manager._clear()
        dash._callback.GLOBAL_CALLBACK_LIST = []
        dash._callback.GLOBAL_CALLBACK_MAP = {}
        dash._callback.GLOBAL_INLINE_SCRIPTS = []
        dash.page_registry.clear()
        dash._pages.CONFIG.clear()
        dash._pages.CONFIG.__dict__.clear()

    @staticmethod
    def _get_external_assets(new_path: str, folder: Path, extension: str) -> List[str]:
        """Returns a list of paths to assets with given extension in folder, prefixed with new_path.

        e.g. with new_path="/vizro", extension="css", folder="/path/to/vizro/vizro-core/src/vizro/static",
        we will get ["/vizro/css/accordion.css", "/vizro/css/button.css", ...].
        """
        return sorted((new_path / path.relative_to(folder)).as_posix() for path in folder.rglob(f"*.{extension}"))
