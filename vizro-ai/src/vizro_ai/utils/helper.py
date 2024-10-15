"""Helper Functions For Vizro AI."""

import pandas as pd


def _get_df_info(df: pd.DataFrame, n_sample: int = 5) -> tuple[str, str]:
    """Get the dataframe schema and head info as string."""
    formatted_pairs = [f"{col_name}: {dtype}" for col_name, dtype in df.dtypes.items()]
    schema_string = "\n".join(formatted_pairs)
    return schema_string, df.sample(n_sample, replace=True, random_state=19).to_markdown()


class DebugFailure(Exception):
    """Debug Failure."""

    pass
