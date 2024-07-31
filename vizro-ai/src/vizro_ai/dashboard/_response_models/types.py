"""Types for response models."""

from typing import Literal

# TODO make available in documentation

# Complete list: ["AgGrid", "Button", "Card", "Container", "Graph", "Table", "Tabs"]
CompType = Literal["AgGrid", "Card", "Graph"]
"""Component types currently supported by Vizro-AI."""

# Complete list: ["Filter", "Parameter"]
CtrlType = Literal["Filter"]
"""Control types currently supported by Vizro-AI."""
