from typing import Dict, List, Tuple

import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
try:
    from pydantic.v1 import BaseModel, Field
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, Field


def _get_df_info(df: pd.DataFrame) -> Tuple[Dict[str, str], str]:
    """Get the dataframe schema and head info as strings."""
    # create a dictionary of column names and data types pairs
    formatted_pairs = {col_name: str(dtype) for col_name, dtype in df.dtypes.items()}
    df_sample = df.sample(5).to_markdown()
    return formatted_pairs, df_sample

df_sum_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a data assistant with expertise naming a pandas dataframe. \n
            Inspect the provided data and give a short unique name to the dataset. \n
            Here is the dataframe sample:  \n ------- \n  {df_sample} \n ------- \n
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
