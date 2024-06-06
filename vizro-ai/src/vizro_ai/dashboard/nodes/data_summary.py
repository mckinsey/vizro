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


class FullDataSummary(BaseModel):
    """Full data summary output"""

    full_data_summary: List[DataSummary]


def _get_df_info(df: pd.DataFrame) -> Tuple[str, str]:
    """Get the dataframe schema and head info as strings."""
    formatted_pairs = [f"{col_name}: {dtype}" for col_name, dtype in df.dtypes.items()]
    schema_string = "\n".join(formatted_pairs)
    head_string = df.sample(5).to_markdown()
    return schema_string, head_string

df_sum_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a data assistant with expertise naming a pandas dataframe. \n
            Inspect the user \n
            question based on the above provided data and give a short unique name to the dataset. \n
            Here is the dataframe sample:  \n ------- \n  {df_head} \n ------- \n
            Here is the schema:  \n ------- \n  {df_schema} \n ------- \n
            Names currently in use: \n ------- \n {current_df_names} \n ------- \n
            \n ------- \n
            """,
        ),
    ]
)

class DfInfo(BaseModel):
    """Data Info output"""

    dataset_name: str = Field(description="Name of the dataset")
