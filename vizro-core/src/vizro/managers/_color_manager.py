"""The color manager assigns consistent colors to categorical values across a Vizro app."""

from __future__ import annotations

import threading
from itertools import cycle
from typing import Any

from vizro.themes._palettes import qualitative


class ColorManager:
    """Assigns a fixed color to each category the first time it's seen, and reuses it afterwards.

    Used by `vizro.models._components.graph._apply_consistent_colors` to back `vm.Dashboard(consistent_colors=True)`.
    """

    def __init__(self):
        self.__category_colors: dict[Any, str] = {}
        self.__palette_cycle = cycle(qualitative)
        self.__lock = threading.Lock()

    def _get_color_discrete_map(self, categories) -> dict[Any, str]:
        """Builds a color_discrete_map that assigns the same color to a category everywhere it appears."""
        with self.__lock:
            # key=str avoids TypeError for object-dtype columns with mutually non-orderable values (e.g.
            # mixed int/str categories) - the sort just needs to be deterministic, not meaningful.
            return {category: self.__get_color(category) for category in sorted(categories, key=str)}

    def __get_color(self, category):
        if category not in self.__category_colors:
            self.__category_colors[category] = next(self.__palette_cycle)
        return self.__category_colors[category]

    def _clear(self):
        self.__init__()  # type: ignore[misc]


color_manager = ColorManager()
