"""Data Summary Node."""

import pandas as pd
from pydantic import BaseModel, Field

DF_SUMMARY_PROMPT = """
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


def _get_df_info(df: pd.DataFrame) -> tuple[dict[str, str], pd.DataFrame]:
    """Get the dataframe schema and sample."""
    formatted_pairs = dict(df.dtypes.astype(str))
    df_sample = df.sample(5, replace=True, random_state=19)
    return formatted_pairs, df_sample


def _create_df_info_content(df_schema: dict[str, str], df_sample: pd.DataFrame, current_df_names: list[str]) -> dict:
    """Create the message content for the dataframe summarization."""
    return DF_SUMMARY_PROMPT.format(df_sample=df_sample, df_schema=df_schema, current_df_names=current_df_names)


if __name__ == "__main__":
    df = pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": [4, 5, 6, 7, 8]})
    df_schema, df_sample = _get_df_info(df)
    current_df_names = ["df1", "df2"]
    print(_create_df_info_content(df_schema, df_sample, current_df_names))  # noqa: T201
    print(DfInfo(dataset="test").model_dump())  # noqa: T201
