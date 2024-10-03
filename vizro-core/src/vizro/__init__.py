import logging
import os

import plotly.io as pio
from dash.development.base_component import Component

from ._themes import dark, light
from ._vizro import Vizro, _library_css_files, _library_js_files, _make_resource_spec

logging.basicConfig(level=os.getenv("VIZRO_LOG_LEVEL", "WARNING"))
pio.templates["vizro_dark"] = dark
pio.templates["vizro_light"] = light

__all__ = ["Vizro"]

__version__ = "0.1.25.dev0"


# For the below _css_dist to be used by Dash, it must be retrieved by dash.resources.Css.get_all_css(). This means it
# must be added to dash.development.base_component.ComponentRegistry. The simplest way to do this is to run
# ComponentRegistry.registry.add("vizro") and this appears to be sufficient for our needs, but it is not documented
# anywhere. The same function is run (together with some others which we probably don't need) when subclassing
# Component, thanks to the metaclass ComponentMeta. So we define a dummy component to go through this safer route,
# even though we don't need the component for anything. _css_dist is automatically served on import of vizro, regardless
# of whether the Vizro class or any other bits are used.
class _Dummy(Component):
    pass


# AM: comment have minimum in _library_css_files
# tidy/remove map file as refers to stuff that doesn't exist
# remove 404 image? Or can keep there? Would it work through CDN? Remember to remove constant/
# Check order of CSS is same.
# Debugging hot reloading
# Ideally would do webpack to .min.js and ship the .min.js so that people using locally also get minified
# Likewise ideally would ship .min.css for all files, so that everyone benefits and not just those who do
# serve_locally=False

_css_dist = [_make_resource_spec(css_file) for css_file in _library_css_files]
_js_dist = [_make_resource_spec(js_file) for js_file in _library_js_files]
