from typing import List, Tuple

import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
try:
    from pydantic.v1 import BaseModel, Field
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, Field

model_sum_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a data assistant with expertise dashboard design and a vizualization library named Vizro. \n
            Summarize the user \n
            question and list out Vizro models required for creating the dashboard. \n
            Available Vizro models to choose from: \n ------- \n
            [
            'AgGrid' # for table creation,
            'Card',
            'Filter',
            'Graph',
            'Page', # always required
            'Dashboard', # always required
            ]  \n ------- \n
            Here is the user question:""",
        ),
        ("placeholder", "{messages}"),
    ]
)

class ModelName(BaseModel):
    """Vizro model name output"""

    model_required: str = Field(description="Name of the Vizro model required")

class ModelSummary(BaseModel):
    """Vizro model summary output"""

    model_summary: List[ModelName]

def generate_import_statement(models):
        import_statement = f"from vizro import Vizro\n"

        required_models = []
        for model_name in models.model_summary:
            model_name = model_name.model_required
            required_models.append(model_name)
        final_required_models = sorted(list(set(required_models)))
        model_import_statement = f"from vizro.models import {', '.join(final_required_models)}\n"
        import_statement += model_import_statement

        if "Graph" in final_required_models:
            import_statement += f"import vizro.plotly.express as px\nfrom vizro.models.types import capture\nimport plotly.graph_objects as go\n"

        if "AgGrid" in final_required_models:
            import_statement += f"from vizro.tables import dash_ag_grid\n"

        # to be removed
        import_statement += f"import pandas as pd\n"

        return import_statement