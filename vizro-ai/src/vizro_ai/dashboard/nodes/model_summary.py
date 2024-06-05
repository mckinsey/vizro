from typing import List, Tuple

import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field

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
    """Model name output"""

    model_required: str = Field(description="Name of the Vizro model required")

class ModelSummary(BaseModel):
    """Model summary output"""

    model_summary: List[ModelName]

