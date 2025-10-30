from vizro.models._fake_vizro.models.models import (
    Action,
    Card,
    Component,
    Dashboard,
    Graph,
    Page,
    SubComponent,
    VizroBaseModel,
)

__all__ = [
    "Action",
    "Card",
    "Component",
    "Dashboard",
    "Graph",
    "Page",
    "SubComponent",
    "VizroBaseModel",
]

# To resolve ForwardRefs we need to import ExportDataAction (similar to vizro.models.__init__.py)
# Import after models to avoid circular import
from vizro.models._fake_vizro.actions import ExportDataAction

# Rebuild all models to resolve forward references
for model in [*__all__]:
    globals()[model].model_rebuild()
