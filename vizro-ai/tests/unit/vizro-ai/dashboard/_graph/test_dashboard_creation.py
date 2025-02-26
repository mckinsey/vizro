import pandas as pd
import pytest
from langchain_core.messages import HumanMessage
from pydantic import ValidationError

from vizro_ai.dashboard._graph.dashboard_creation import GraphState


class TestConfig:
    """Test GraphState config creation."""

    def test_graph_state_instantiation(self, graph_state, dataframes):
        assert isinstance(graph_state, GraphState)
        assert graph_state.messages[0].content == "contents of the message"
        assert graph_state.dfs == dataframes
        assert "gdp_chart" in graph_state.all_df_metadata.all_df_metadata
        assert graph_state.pages == []
        assert graph_state.custom_charts_code == []

    @pytest.mark.parametrize(
        "dataframes, output_error",
        [
            (pd.DataFrame(), "A single DataFrame was provided to 'dfs'"),
            ([pd.DataFrame(), {}], "Input should be a list of DataFrames"),
            ((pd.DataFrame(),), "Input should be a list of DataFrames"),
        ],
    )
    def test_check_dataframes_validation_error(self, dataframes, output_error, df_metadata):
        with pytest.raises(ValidationError, match=output_error):
            GraphState(
                messages=[HumanMessage(content="contents of the message")],
                dfs=dataframes,
                all_df_metadata=df_metadata,
                pages=[],
                custom_charts_code=[],
                custom_charts_imports=[],
            )
