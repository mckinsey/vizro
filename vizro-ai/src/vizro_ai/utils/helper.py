"""Helper Functions For Vizro AI."""

import traceback
from typing import Callable, Dict, Optional, Tuple

import pandas as pd
import plotly.graph_objects as go
from vizro_ai.plot._utils._safeguard import _safeguard_check


def _get_df_info(df: pd.DataFrame) -> Tuple[str, str]:
    """Get the dataframe schema and head info as string."""
    formatted_pairs = [f"{col_name}: {dtype}" for col_name, dtype in df.dtypes.items()]
    schema_string = "\n".join(formatted_pairs)
    return schema_string, df.sample(5, replace=True, random_state=19).to_markdown()


class DebugFailure(Exception):
    """Debug Failure."""

    pass
