from pydantic.v1 import BaseModel as BaseModelV1
from vizro.tables import dash_ag_grid
from vizro.models import *
import vizro.plotly.express as px
from vizro.models.types import capture
from vizro import Vizro
from enum import Enum


class Imports(Enum):
    AgGrid = "from vizro.tables import dash_ag_grid"
    Graph = "import vizro.plotly.express as px"

