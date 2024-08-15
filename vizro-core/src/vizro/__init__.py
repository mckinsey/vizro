import logging
import os

from dash.development.base_component import Component

from ._vizro import Vizro

logging.basicConfig(level=os.getenv("VIZRO_LOG_LEVEL", "WARNING"))

__all__ = ["Vizro"]

# __version__ = "0.1.20.dev0"
__version__ = "tidy/create-module-pure-functions"


# For the below _css_dist to be used by Dash, it must be retrieved by dash.resources.Css.get_all_css(). This means it
# must be added to dash.development.base_component.ComponentRegistry. The simplest way to do this is to run
# ComponentRegistry.registry.add("vizro") and this appears to be sufficient for our needs, but it is not documented
# anywhere. The same function is run (together with some others which we probably don't need) when subclassing
# Component, thanks to the metaclass ComponentMeta. So we define a dummy component to go through this safer route,
# even though we don't need the component for anything. _css_dist is automatically served on import of vizro, regardless
# of whether the Vizro class or any other bits are used.
class _Dummy(Component):
    pass


_library_css = ["static/css/figures"]
_base_external_url = f"https://cdn.jsdelivr.net/gh/mckinsey/vizro@{__version__}/vizro-core/src/vizro/"

_css_dist = [
    {
        "namespace": "vizro",
        "relative_package_path": f"{css_file}.css",
        "external_url": f"{_base_external_url}{css_file}.min.css",
    }
    for css_file in _library_css
]

_css_dist.append(
    {
        "namespace": "vizro",
        "relative_package_path": f"static/css/fonts/material-symbols-outlined.woff2",
    }
)
