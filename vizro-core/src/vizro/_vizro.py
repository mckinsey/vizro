import logging
import os
from pathlib import Path
from typing import Dict, List, Tuple

import dash
import flask

from vizro._constants import STATIC_URL_PREFIX
from vizro.managers import data_manager, model_manager
from vizro.models import Dashboard

logger = logging.getLogger(__name__)


class Vizro:
    """The main class of the `vizro` package."""

    _user_assets_folder = Path.cwd() / "assets"
    _lib_assets_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

    def __init__(self):
        """Initializes Dash."""
        _js, _css = _append_styles(self._lib_assets_folder, STATIC_URL_PREFIX)
        self.dash = dash.Dash(
            use_pages=True,
            pages_folder="",
            external_scripts=_js,
            external_stylesheets=_css,
            assets_folder=self._user_assets_folder,
        )

        @self.dash.server.route("/<url_prefix>/<path:filepath>")
        def serve_static(filepath, url_prefix=STATIC_URL_PREFIX):
            """Serve vizro static contents."""
            return flask.send_from_directory(self._lib_assets_folder, filepath)

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
            args: Any args to `dash.run_server`
            kwargs: Any kwargs to `dash.run_server`
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


def _append_styles(walk_dir: str, url_prefix: str) -> Tuple[List[Dict[str, str]], List[str]]:
    """Append vizro css and js resources."""
    _vizro_css = []
    _vizro_js = []

    for current_dir, _, files in sorted(os.walk(walk_dir)):
        base = "" if current_dir == walk_dir else os.path.relpath(current_dir, walk_dir).replace("\\", "/")
        for f in sorted(files):
            path = os.path.join("/" + url_prefix, base, f) if base else os.path.join("/" + url_prefix, f)
            extension = os.path.splitext(f)[1]
            if extension == ".js":
                _vizro_js.append({"src": path, "type": "module"})
            elif extension == ".css":
                _vizro_css.append(path)
    return _vizro_js, _vizro_css
