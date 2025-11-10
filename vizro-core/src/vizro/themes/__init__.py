"""Themes that can be used in and outside Vizro framework.

vizro.themes.colors: Vizro colors
vizro.themes.palettes: Vizro palettes (same for light and dark themes) includes sequential and diverging color scales.

Example:
```python
from vizro.themes import colors, palettes

print(colors.cyan_100)
print(palettes.qualitative)
```
"""

from .colors import colors
from .palettes import palettes

__all__ = ["colors", "palettes"]
