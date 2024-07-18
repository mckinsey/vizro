"""Types for response models."""

from typing import Literal

# TODO: these are types rather than constants. Rename to types and move to types.py
# For unsupported component and control types, how to handle them?
# option 1. Ignore silently
# option 2. Raise a warning and add the warning message into langgraph state. This gives the user transparency on why
#    a certain component or control was not created.
# option 3. Raise a warning and suggest additional reference material <=

# Complete list: ["AgGrid", "Button", "Card", "Container", "Graph", "Table", "Tabs"]
component_type = Literal["AgGrid", "Card", "Graph"]
"""Component types currently supported by Vizro-AI."""

# Complete list: ["Filter", "Parameter"]
control_type = Literal["Filter"]
"""Control types currently supported by Vizro-AI."""
