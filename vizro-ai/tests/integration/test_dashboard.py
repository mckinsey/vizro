"""Tests for dashboard using VizroAI."""

import pytest
import vizro.plotly.express as px
from hamcrest import assert_that, equal_to
from vizro import Vizro
from vizro.managers._model_manager import DuplicateIDError
from vizro_ai import VizroAI

vizro_ai = VizroAI()

df1 = px.data.gapminder()
df2 = px.data.stocks()
df3 = px.data.tips()


@pytest.mark.filterwarnings("ignore::langchain_core._api.beta_decorator.LangChainBetaWarning")
@pytest.mark.filterwarnings("ignore::UserWarning")
def test_simple_dashboard():
    input_text = """
    I need a page with 1 table.
    The table shows the tech companies stock data.

    I need a second page showing 2 cards and one chart.
    The first card says 'The Gapminder dataset provides historical data on countries' development indicators.'
    The chart is an scatter plot showing life expectancy vs. GDP per capita by country. Life expectancy on the y axis, GDP per capita on the x axis, and colored by continent.
    The second card says 'Data spans from 1952 to 2007 across various countries.'
    The layout uses a grid of 3 columns and 2 rows.

    Row 1: The first row has three columns:
    The first column is occupied by the first card.
    The second and third columns are spanned by the chart.

    Row 2: The second row mirrors the layout of the first row with respect to chart, but the first column is occupied by the second card.

    Add a filter to filter the scatter plot by continent.
    Add a second filter to filter the chart by year.
    """

    dashboard = vizro_ai.dashboard([df1, df2], input_text)

    # Page 1
    assert_that(len(dashboard.pages[0].components), equal_to(1))
    # Page 2
    assert_that(len(dashboard.pages[1].components), equal_to(3))


@pytest.mark.filterwarnings("ignore::langchain_core._api.beta_decorator.LangChainBetaWarning")
@pytest.mark.filterwarnings("ignore::UserWarning")
def test_4_page_dashboard():
    input_text = """
    <Page 1>
    I need a page with 1 table and 1 line chart.
    The chart shows the stock price trends of GOOG and AAPL.
    The table shows the stock prices data details.

    <Page 2>
    I need a second page showing 1 card and 1 chart.
    The card says 'The Gapminder dataset provides historical data on countries' development indicators.'
    The chart is a scatter plot showing GDP per capita vs. life expectancy. GDP per capita on the x axis, life expectancy on the y axis, and colored by continent.
    Layout the card on the left and the chart on the right. The card takes 1/3 of the whole space on the left.
    The chart takes 2/3 of the whole space and is on the right.
    Add a filter to filter the scatter plot by continent.
    Add a second filter to filter the chart by year.

    <Page 3>
    This page displays the tips data dataset. use two different charts to show data
    distributions. one chart should be a bar chart and the other should be a scatter plot.
    first chart is on the left and the second chart is on the right.
    Add a filter to filter data in the scatter plot by smoker.

    <Page 4>
    Create 3 cards on this page:
    1. The first card on top says "This page combines data from various sources including tips, stock prices, and global indicators."
    2. The second card says "Insights from Gapminder dataset."
    3. The third card says "Stock price trends over time."

    Layout these 3 cards in this way:
    create a grid with 3 columns and 2 rows.
    Row 1: The first row has three columns:
    - The first column is empty.
    - The second and third columns span the area for card 1.

    Row 2: The second row also has three columns:
    - The first column is empty.
    - The second column is occupied by the area for card 2.
    - The third column is occupied by the area for card 3.
    """

    try:
        Vizro._reset()
        dashboard = vizro_ai.dashboard([df1, df2, df3], input_text)
        Vizro._reset()
    except DuplicateIDError as di:
        print(di)
        Vizro._reset()
        dashboard = vizro_ai.dashboard([df1, df2, df3], input_text)
        Vizro._reset()

    # Page 1
    assert_that(len(dashboard.pages[0].components), equal_to(2))
    # Page 2
    assert_that(len(dashboard.pages[1].components), equal_to(2))
    # Page 3
    assert_that(len(dashboard.pages[2].components), equal_to(2))
    # Page 4
    assert_that(len(dashboard.pages[3].components), equal_to(3))


@pytest.mark.filterwarnings("ignore::langchain_core._api.beta_decorator.LangChainBetaWarning")
@pytest.mark.filterwarnings("ignore::UserWarning")
def test_unsupported_dashboard():
    input_text = """
    <Page 1>
    I need a page showing 2 cards, one chart, and 1 button.
    The first card says 'The Tips dataset provides insights into customer tipping behavior.'
    The chart is a bar chart showing the total bill amount by day. Day on the x axis, total bill amount on the y axis, and colored by time of day.
    The second card says 'Data collected from various days and times.'
    Layout the two cards on the left and the chart on the right. Two cards take 1/3 of the whole space on the left in total.
    The first card is on top of the second card vertically.
    The chart takes 2/3 of the whole space and is on the right.
    The button would trigger a download action to download the Tips dataset.
    Add a filter to filter the bar chart by `size`.
    Make another tab on this page,
    In this tab, create a card saying "Tipping patterns and trends."
    Group all the above content into the first NavLink.

    <Second NavLink>
    Create two pages:
    1. The first page has a card saying "Analyzing global development trends."
    2. The second page has a scatter plot showing GDP per capita vs. life expectancy. GDP per capita on the x axis, life expectancy on the y axis, and colored by continent.
    Add a parameter to control the title of the scatter plot, with title options "Economic Growth vs. Health" and "Development Indicators."
    Also create a button and a spinning circle on the right-hand side of the page.

    <Third NavLink>
    Create one page:
    1. The first page has a card saying "Stock price trends over time."
    Create a button and a spinning circle on the right-hand side of the page.

    For hosting the dashboard on AWS, which service should I use?
    """

    try:
        vizro_ai.dashboard([df1, df2, df3], input_text)
    except ValueError as v:
        print(v)
