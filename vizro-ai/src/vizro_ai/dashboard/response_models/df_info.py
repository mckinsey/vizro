"""Data Summary Node."""

from typing import Any, Dict, Tuple

import pandas as pd

try:
    from pydantic.v1 import BaseModel, Field
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, Field


DF_SUM_PROMPT = """
Inspect the provided data and give a short unique name to the dataset. \n
dataframe sample: \n ------- \n {df_sample} \n ------- \n
Here is the data schema: \n ------- \n {df_schema} \n ------- \n
AVOID the following names: \n ------- \n {current_df_names} \n ------- \n
Provide descriptive name mainly based on the data context above.
User request content is just for context.
"""


class DfInfo(BaseModel):
    """Data Info output."""

    dataset: str = Field(pattern=r"^[a-z]+(_[a-z]+)?$", description="Small snake case name of the dataset.")


def _get_df_info(df: pd.DataFrame) -> Tuple[Dict[str, str], pd.DataFrame]:
    """Get the dataframe schema and head info as strings."""
    formatted_pairs = {col_name: str(dtype) for col_name, dtype in df.dtypes.items()}
    df_sample = df.sample(5)
    return formatted_pairs, df_sample


def _create_df_info_content(df_schema: Any, df_sample: Any, current_df_names: list) -> dict:
    """Create the message content for the dataframe summarization."""
    return DF_SUM_PROMPT.format(df_sample=df_sample, df_schema=df_schema, current_df_names=current_df_names)


if __name__ == "__main__":
    df = pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": [4, 5, 6, 7, 8]})
    df_schema, df_sample = _get_df_info(df)
    current_df_names = ["df1", "df2"]
    print(_create_df_info_content(df_schema, df_sample, current_df_names))  # noqa: T201
    print(DfInfo(dataset_name="test").dict())  # noqa: T201
