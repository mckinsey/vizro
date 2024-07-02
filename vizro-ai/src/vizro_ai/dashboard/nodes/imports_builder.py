"""Import statement builder node."""

from typing import List

from langchain_core.prompts import ChatPromptTemplate

try:
    from pydantic.v1 import BaseModel, Field
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, Field

model_sum_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a data assistant with expertise dashboard design and a visualization library named Vizro. \n
            Summarize the user \n
            question and list out Vizro models required for creating the dashboard. \n
            Available Vizro models to choose from: \n ------- \n
            [
            'AgGrid' # for table creation,
            'Card',
            'Filter',
            'Graph',
            'Layout',
            ]  \n ------- \n
            Here is the user question:""",
        ),
        ("placeholder", "{messages}"),
    ]
)


class ModelName(BaseModel):
    """Vizro model name output."""

    model_required: str = Field(description="Name of the Vizro model required")


class ModelSummary(BaseModel):
    """Vizro model summary output."""

    model_summary: List[ModelName]


def _generate_import_statement(models) -> str:
    import_statement = "from vizro import Vizro\n"

    required_models = ["Page", "Dashboard"]
    for model_name in models.model_summary:
        model_required = model_name.model_required
        required_models.append(model_required)
    final_required_models = sorted(set(required_models))
    model_import_statement = f"from vizro.models import {', '.join(final_required_models)}\n"
    import_statement += model_import_statement

    if "Graph" in final_required_models:
        import_statement += "import vizro.plotly.express as px\n"
        "from vizro.models.types import capture\nimport plotly.graph_objects as go\n"

    if "AgGrid" in final_required_models:
        import_statement += "from vizro.tables import dash_ag_grid\n"

    import_statement += """
    \n
    # # YOUR DATA INGESTION CODE GOES HERE
    # # define the data loading functions and store them in the data_manager
    # # example:
    # import pandas as pd
    # from vizro.managers import data_manager
    #
    # def load_data_a():
    #     return pd.read_csv('data_a.csv')
    #
    # def load_data_b():
    #     return pd.read_csv('data_b.csv')
    #
    # data_manager['data_a'] = load_data_a
    # data_manager['data_b'] = load_data_b
    #
    # # "data_a" and "data_b" are the keys referred by the field `data_frame=` in below dashboard code
    \n
    """

    return import_statement
