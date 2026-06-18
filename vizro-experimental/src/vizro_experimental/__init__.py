"""vizro-experimental — home for in-development Vizro features.

Features here may change or be removed between releases. Graduated features move
to vizro-core.
"""

from dash.development.base_component import ComponentRegistry

__version__ = "0.0.1.dev0"

_PACKAGE = "vizro_experimental"

_css_dist = [
    {"namespace": _PACKAGE, "relative_package_path": "static/css/chat.css"},
    {"namespace": _PACKAGE, "relative_package_path": "static/css/chat_popup.css"},
]
_js_dist = [
    {"namespace": _PACKAGE, "relative_package_path": "static/js/chat.js"},
]

# Chat is a Vizro model, not a Dash component, so the ComponentMeta auto-register
# never runs. Register the package explicitly so Dash picks up _css_dist/_js_dist.
ComponentRegistry.registry.add(_PACKAGE)
