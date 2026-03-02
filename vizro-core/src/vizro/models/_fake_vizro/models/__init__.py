from vizro.models._fake_vizro.models.models import (
    Action,
    Card,
    Component,
    Container,
    Dashboard,
    Graph,
    Page,
    SubComponent,
    Tabs,
    VizroBaseModel,
)

__all__ = [
    "Action",
    "Card",
    "Component",
    "Container",
    "Dashboard",
    "Graph",
    "Page",
    "SubComponent",
    "Tabs",
    "VizroBaseModel",
]

# To resolve ForwardRefs we need to import ExportDataAction (similar to vizro.models.__init__.py)
# Import after models to avoid circular import
from vizro.models._fake_vizro.actions import ExportDataAction

# Rebuild all models to resolve forward references
# Below we see that order matters, and while ExportDataAction now builds properly, not all models have a correct schema
for model in ["ExportDataAction", *__all__]:
    globals()[model].model_rebuild(force=True)
