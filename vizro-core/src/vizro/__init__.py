import logging
import os
from dash.development.base_component import ComponentRegistry

from ._vizro import Vizro

ComponentRegistry.registry.add("vizro")

_css_dist = [
    {
        "relative_package_path": "static/css/figures.css",
        "namespace": "vizro",

    },
]

_js_dist = []
__all__ = ["Vizro"]
__version__ = "0.1.20.dev0"

logging.basicConfig(level=os.getenv("VIZRO_LOG_LEVEL", "WARNING"))
