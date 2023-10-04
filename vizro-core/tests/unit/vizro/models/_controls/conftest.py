import random

import numpy as np
import pandas as pd
import pytest

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro


@pytest.fixture
def dfs_with_shared_column():
    df1 = pd.DataFrame()
    df1["x"] = np.random.uniform(0, 10, 100)
    df1["y"] = np.random.uniform(0, 10, 100)
    df2 = df1.copy()

    df1["shared_column"] = np.random.uniform(0, 10, 100)
    df2["shared_column"] = random.choices(["CATEGORY 1", "CATEGORY 2"], k=100)

    return df1, df2


@pytest.fixture
def managers_one_page_two_graphs(gapminder):
    """Instantiates a simple model_manager and data_manager with a page, and two graph models and gapminder data."""
    vm.Page(
        id="test_page",
        title="My first dashboard",
        components=[
            vm.Graph(id="scatter_chart", figure=px.scatter(gapminder, x="lifeExp", y="gdpPercap")),
            vm.Graph(id="bar_chart", figure=px.bar(gapminder, x="country", y="gdpPercap")),
        ],
    )
    Vizro._pre_build()


@pytest.fixture
def managers_shared_column_different_dtype(dfs_with_shared_column):
    """Instantiates the managers with a page and two graphs sharing the same column but of different data types."""
    df1, df2 = dfs_with_shared_column
    vm.Page(
        id="graphs_with_shared_column",
        title="Page Title",
        components=[
            vm.Graph(figure=px.scatter(df1, x="x", y="y", color="shared_column")),
            vm.Graph(figure=px.scatter(df2, x="x", y="y", color="shared_column")),
        ],
    )
    Vizro._pre_build()
