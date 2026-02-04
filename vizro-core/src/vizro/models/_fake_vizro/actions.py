"""Actions module - creates circular dependency with models.py.

models.py imports ExportDataAction from here
actions.py imports VizroBaseModel from models.py
→ CIRCULAR DEPENDENCY!
"""

from vizro.models._fake_vizro.models import VizroBaseModel


class ExportDataAction(VizroBaseModel):
    """Export data action that inherits from VizroBaseModel (defined in models.py)."""

    format: str = "csv"
