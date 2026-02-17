"""Contains Vizro's carefully designed color system and palettes.

Attributes:
    colors (SimpleNamespace): Individual color values (hex codes)
    palettes (SimpleNamespace): Pre-configured color scales including:

        - qualitative: 10 distinct colors for categorical data
        - sequential_*: Sequential color gradients for ordered data
        - diverging_*: Diverging color scales for data with meaningful midpoints

Examples:
    ```python
    from vizro.themes import colors, palettes

    print(colors.blue_100)
    print(palettes.qualitative)
    ```
"""

from ._colors import colors
from ._palettes import palettes

__all__ = ["colors", "palettes"]
