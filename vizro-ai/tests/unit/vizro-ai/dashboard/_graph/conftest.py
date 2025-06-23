import pandas as pd
import pytest
from langchain_core.messages import HumanMessage

from vizro_ai.dashboard._graph.dashboard_creation import GraphState
from vizro_ai.dashboard.utils import AllDfMetadata, DfMetadata


@pytest.fixture
def dataframes():
    return [pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": [4, 5, 6, 7, 8]})]


@pytest.fixture
def df_metadata():
    df_metadata = AllDfMetadata()
    df_metadata.all_df_metadata["gdp_chart"] = DfMetadata(
        df_schema={"a": "int64", "b": "int64"},
        df=pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": [4, 5, 6, 7, 8]}),
        df_sample=pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": [4, 5, 6, 7, 8]}),
    )
    return df_metadata


@pytest.fixture
def graph_state(dataframes, df_metadata):
    return GraphState(
        messages=[HumanMessage(content="contents of the message")],
        dfs=dataframes,
        all_df_metadata=df_metadata,
        pages=[],
        custom_charts_code=[],
        custom_charts_imports=[],
    )
