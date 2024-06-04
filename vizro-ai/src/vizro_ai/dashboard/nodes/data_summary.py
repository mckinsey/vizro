from typing import List, Tuple

import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field

requirement_sum_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a data assistant with expertise dashboard design and a vizualization library named Vizro. \n
            Here are the dataframes:  \n ------- \n  {df_heads} \n ------- \n
            Here are the schemas:  \n ------- \n  {df_schemas} \n ------- \n
            Inspect the user \n
            question based on the above provided data and summarize which dataset to use for each Vizro model. \n
            First name each dataset with a user friendly name. \n
            Then provide a summary of the user question and the dataset to use for each Vizro model. \n
            Available Vizro models to choose from: \n ------- \n
            [
            'AgGrid' # for table creation,
            'Card',
            'Filter',
            'Graph',
            'Page',
            ]  \n ------- \n
            Here is the user question:""",
        ),
        ("placeholder", "{messages}"),
    ]
)


# Data model
class DataSummary(BaseModel):
    """Data summary output"""

    dataset_provided: str = Field(description="Names of the datasets provided")
    data_sample: str = Field(description="Sample data (first 5 rows) from the dataset provided")
    data_schema: str = Field(description="Schema of the dataset provided")
    dataset_vizro_model_mapping: str = Field(description="Mapping of dataset name to Vizro model")


class FullDataSummary(BaseModel):
    """Full data summary output"""

    full_data_summary: List[DataSummary]


def _get_df_info(dfs: List[pd.DataFrame]) -> Tuple[List[str], List[str]]:
    """Get the dataframe schema and head info as string."""
    schema_strings = []
    head_strings = []
    for _, df in enumerate(dfs):
        formatted_pairs = [f"{col_name}: {dtype}" for col_name, dtype in df.dtypes.items()]
        schema_string = "\n".join(formatted_pairs)

        schema_strings.append(schema_string)
        head_strings.append(df.head().to_markdown())
    return schema_strings, head_strings
