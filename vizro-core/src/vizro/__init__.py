import json
import logging
import os
from pathlib import Path

import plotly.io as pio
from dash.development.base_component import ComponentRegistry
from packaging.version import parse

from ._constants import VIZRO_ASSETS_PATH
from ._vizro import Vizro, _make_resource_spec

logging.basicConfig(level=os.getenv("VIZRO_LOG_LEVEL", "WARNING"))

base_path = Path(__file__).parent / "_themes"
pio.templates["vizro_dark"] = json.loads((base_path / "vizro_dark.json").read_text())
pio.templates["vizro_light"] = json.loads((base_path / "vizro_light.json").read_text())

__all__ = ["Vizro"]
__version__ = "0.1.40"

# For dev versions, a branch or tag called e.g. 0.1.20.dev0 does not exist and so won't work with the CDN. We point
# to main instead, but this can be manually overridden to the current feature branch name if required.
# This would only be the case where you need to test something with serve_locally=False and have changed
# assets compared to main. In this case you need to push your assets changes to remote for the CDN to update,
# and it might also be necessary to clear the CDN cache: https://www.jsdelivr.com/tools/purge.
_git_branch = __version__ if not parse(__version__).is_devrelease else "main"
BASE_EXTERNAL_URL = f"https://cdn.jsdelivr.net/gh/mckinsey/vizro@{_git_branch}/vizro-core/src/vizro/"
# Enables the use of our own Bootstrap theme in a pure Dash app with `external_stylesheets=vizro.bootstrap`.
bootstrap = f"{BASE_EXTERNAL_URL}static/css/vizro-bootstrap.min.css"

# For the below _css_dist and _js_dist to be used by Dash, they must be retrieved by dash.resources.Css.get_all_css().
# This means adding them to dash.development.base_component.ComponentRegistry. The simplest way to do this is to run
# ComponentRegistry.registry.add("vizro") and this appears to be sufficient for our needs, but it is not documented
# anywhere. The same function is run (together with some others which we don't need and make things a bit dirty) when
# subclassing Component, thanks to the metaclass ComponentMeta. We used to define a dummy component and do this route,
# even though we don't need the component for anything, but it's cleaner to do ComponentRegistry.registry.add("vizro").
# Since we need to *remove* the library resources when Vizro is used as a framework it's also clearer when this gets
# reversed by ComponentRegistry.registry.discard("vizro") in Vizro(). _css_dist and _js_dist is automatically served on
# import of vizro, regardless of whether the Vizro class or any other bits are used.
ComponentRegistry.registry.add("vizro")

# Files needed to use Vizro as a library (not a framework), e.g. in a pure Dash app.
# This list should be kept to the bare minimum so we don't insert any more than the minimum required CSS on pure Dash
# apps. At the moment the only library components we support just are KPI cards. Note that anything that's not CSS
# is handled as a script, even if it's a font file or image.
_library_css_files = [
    VIZRO_ASSETS_PATH / "css/figures.css",
]
_library_js_files = [
    VIZRO_ASSETS_PATH / "css/fonts/material-symbols-outlined.woff2",
]


_css_dist = [_make_resource_spec(css_file) for css_file in sorted(_library_css_files)]
_js_dist = [_make_resource_spec(js_file) for js_file in sorted(_library_js_files)]
