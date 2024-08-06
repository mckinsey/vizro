"""Tests for dashboard using VizroAI."""

import os

import chromedriver_autoinstaller
import pytest
import vizro.plotly.express as px
from vizro import Vizro
from vizro_ai import VizroAI

vizro_ai = VizroAI()

df1 = px.data.gapminder()
df2 = px.data.stocks()


@pytest.fixture(scope="module", autouse=True)
def setup_test_environment():
    # We only need to install chromedriver outside CI.
    if not os.getenv("CI"):
        chromedriver_autoinstaller.install()


@pytest.mark.filterwarnings("ignore::langchain_core._api.beta_decorator.LangChainBetaWarning")
@pytest.mark.filterwarnings("ignore::UserWarning")
@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_simple_dashboard(dash_duo):
    input_text = """
    I need a page with 1 table.
    The table shows the tech companies stock data.

    I need a second page showing 2 cards and one chart.
    The first card says 'The Gapminder dataset provides historical data on countries' development indicators.'
    The chart is an scatter plot showing life expectancy vs. GDP per capita by country. Life expectancy on the y axis,
    GDP per capita on the x axis, and colored by continent.
    The second card says 'Data spans from 1952 to 2007 across various countries.'
    The layout uses a grid of 3 columns and 2 rows.

    Row 1: The first row has three columns:
    The first column is occupied by the first card.
    The second and third columns are spanned by the chart.

    Row 2: The second row mirrors the layout of the first row with respect to chart, but the first column is occupied
    by the second card.

    Add a filter to filter the scatter plot by continent.
    Add a second filter to filter the chart by year.
    """

    dashboard = vizro_ai.dashboard([df1, df2], input_text)
    app = Vizro().build(dashboard).run()
    dash_duo.start_server(app)
    assert dash_duo.get_logs() == []
