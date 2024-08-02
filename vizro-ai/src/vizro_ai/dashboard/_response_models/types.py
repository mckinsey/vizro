"""Types for response models."""

from typing import Literal

# TODO make available in documentation

# Complete list: ["AgGrid", "Button", "Card", "Container", "Graph", "Table", "Tabs"]
ComponentType = Literal["AgGrid", "Card", "Graph"]
"""Component types currently supported by Vizro-AI."""

# Complete list: ["Filter", "Parameter"]
ControlType = Literal["Filter"]
"""Control types currently supported by Vizro-AI."""
