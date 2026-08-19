import threading
from itertools import cycle

from vizro.themes._palettes import qualitative

_lock = threading.Lock()
_palette_cycle = cycle(qualitative)
_category_colors: dict = {}


def _get_color(category):
    with _lock:
        if category not in _category_colors:
            _category_colors[category] = next(_palette_cycle)
        return _category_colors[category]


def _consistent_color_discrete_map(categories):
    """Builds a color_discrete_map that assigns the same color to a category everywhere it appears."""
    return {category: _get_color(category) for category in sorted(categories)}


def _clear():
    global _palette_cycle
    with _lock:
        _palette_cycle = cycle(qualitative)
        _category_colors.clear()
