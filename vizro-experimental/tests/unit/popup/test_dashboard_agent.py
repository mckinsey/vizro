"""Unit tests for the ``query_dataframe`` @tool in dashboard_agent.

Regression for the ``**params: Any`` bug: when the tool used ``**params`` in its
signature, ``langchain_core.tools.@tool`` emitted a nested ``params`` object in the
tool schema and the function body never unpacked it, so every groupby / pivot_table /
sort_values call failed with ``'by' parameter is required``.
Verified against langchain_core==1.2.22.

These tests pin the flat schema and exercise the handler path with the exact
kwarg shape that LangChain will invoke the tool with.
"""

import pandas as pd
import pytest
from vizro.managers import data_manager

from vizro_experimental.chat.popup.dashboard_agent import query_dataframe


@pytest.fixture()
def scores_df():
    return pd.DataFrame(
        {
            "Category": ["Sports", "Sports", "Kids", "Kids", "Drama", "Drama"],
            "QoE": [4.4, 4.6, 8.0, 8.2, 7.0, 6.8],
        }
    )


@pytest.fixture()
def registered_dataset(scores_df):
    name = "test_scores"
    data_manager[name] = lambda: scores_df
    yield name
    data_manager._DataManager__data.pop(name, None)


class TestSchema:
    """Pin the LLM-facing tool schema to flat kwargs."""

    def test_schema_is_flat_not_nested(self):
        schema_keys = set(query_dataframe.args.keys())
        assert "params" not in schema_keys, (
            "Regression: @tool is exposing a nested 'params' object. "
            "The signature must use explicit kwargs, not **params."
        )

    def test_schema_exposes_all_expected_kwargs(self):
        expected = {
            "dataset_name",
            "operation",
            "by",
            "column",
            "agg",
            "index",
            "columns",
            "values",
            "n",
            "ascending",
            "value",
        }
        assert set(query_dataframe.args.keys()) == expected


class TestInvocation:
    """Exercise the tool with the flat-kwargs shape LangChain produces."""

    def test_groupby_with_flat_kwargs(self, registered_dataset):
        result = query_dataframe.invoke(
            {
                "dataset_name": registered_dataset,
                "operation": "groupby",
                "by": "Category",
                "agg": "mean",
                "column": "QoE",
            }
        )
        # Sports row: (4.4 + 4.6) / 2 = 4.5 — the lowest category mean.
        assert "Sports" in result
        assert "4.5" in result
        assert "Error" not in result

    def test_pivot_table_with_flat_kwargs(self, registered_dataset):
        result = query_dataframe.invoke(
            {
                "dataset_name": registered_dataset,
                "operation": "pivot_table",
                "index": "Category",
                "values": "QoE",
                "agg": "mean",
            }
        )
        assert "Sports" in result
        assert "Error" not in result

    def test_sort_values_requires_by(self, registered_dataset):
        result = query_dataframe.invoke(
            {
                "dataset_name": registered_dataset,
                "operation": "sort_values",
                "by": "QoE",
                "ascending": True,
                "n": 2,
            }
        )
        assert "Error" not in result
        assert "Sports" in result  # lowest-QoE rows land first

    def test_unknown_dataset_returns_error(self):
        result = query_dataframe.invoke({"dataset_name": "does_not_exist", "operation": "describe"})
        assert result.startswith("Error: Dataset 'does_not_exist' not found")

    def test_unknown_operation_returns_error(self, registered_dataset):
        result = query_dataframe.invoke({"dataset_name": registered_dataset, "operation": "rm_rf"})
        assert result.startswith("Error: Operation 'rm_rf' is not allowed")
