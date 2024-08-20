import logging
import os

import plotly.io as pio
from dash.development.base_component import Component

from ._themes import dark, light
from ._vizro import Vizro

logging.basicConfig(level=os.getenv("VIZRO_LOG_LEVEL", "WARNING"))
pio.templates["vizro_dark"] = dark
pio.templates["vizro_light"] = light

__all__ = ["Vizro"]

__version__ = "0.1.20"


# For the below _css_dist to be used by Dash, it must be retrieved by dash.resources.Css.get_all_css(). This means it
# must be added to dash.development.base_component.ComponentRegistry. The simplest way to do this is to run
# ComponentRegistry.registry.add("vizro") and this appears to be sufficient for our needs, but it is not documented
# anywhere. The same function is run (together with some others which we probably don't need) when subclassing
# Component, thanks to the metaclass ComponentMeta. So we define a dummy component to go through this safer route,
# even though we don't need the component for anything. _css_dist is automatically served on import of vizro, regardless
# of whether the Vizro class or any other bits are used.
class _Dummy(Component):
    pass


# For dev versions, a branch or tag called e.g. 0.1.20.dev0 does not exist and so won't work with the CDN. We point
# to main instead, but this can be manually overridden to the current feature branch name if required.
# _git_branch = __version__ if "dev" not in __version__ else "main"
_git_branch = __version__ if "dev" not in __version__ else "main"
_library_css = ["static/css/figures"]
_base_external_url = f"https://cdn.jsdelivr.net/gh/mckinsey/vizro@{_git_branch}/vizro-core/src/vizro/"

# CSS is packaged and accessed using relative_package_path when serve_locally=False (the default) in
# the Dash instantiation. When serve_locally=True then, where defined, external_url will be used instead.
_css_dist = [
    {
        "namespace": "vizro",
        "relative_package_path": f"{css_file}.css",
        "external_url": f"{_base_external_url}{css_file}.min.css",
    }
    for css_file in _library_css
]

# Include font file so that figures with icons can be used outside Vizro as pure Dash components.
# The file can be served through the CDN in the same way as the CSS files but external_url is irrelevant here. The way
# the file is requested is through a relative url("./fonts/...") in the requesting CSS file. When the CSS file is
# served from the CDN then this will refer to the font file also on the CDN.
_css_dist.append(
    {
        "namespace": "vizro",
        "relative_package_path": "static/css/fonts/material-symbols-outlined.woff2",
    }
)
