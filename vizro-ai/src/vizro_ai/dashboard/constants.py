"""Define constants for the dashboard module."""

from typing import Literal

# For unsupported component and control types, how to handle them?
# option 1. Ignore silently
# option 2. Raise a warning and add the warning message into langgraph state. This gives the user transparency on why
#    a certain component or control was not created.
# option 3. Raise a warning and suggest additional reference material <=
component_type = Literal[
    "AgGrid", "Card", "Graph"
]  # Complete list: ["AgGrid", "Button", "Card", "Container", "Graph", "Table", "Tabs"]
control_type = Literal["Filter"]  # Complete list: ["Filter", "Parameter"]

# For other models, like ["Accordion", "NavBar"], how to handle them? <=


IMPORT_STATEMENTS = (
    "import vizro.plotly.express as px\n"
    "from vizro.models.types import capture\n"
    "import plotly.graph_objects as go\n"
    "from vizro.tables import dash_ag_grid\n"
    "import vizro.models as vm\n"
)
