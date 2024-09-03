"""Tests for dashboard using VizroAI."""

import csv
import os
from datetime import datetime

import chromedriver_autoinstaller
import pytest
import vizro.plotly.express as px
from vizro import Vizro
from vizro_ai import VizroAI

vizro_ai = VizroAI()

df1 = px.data.gapminder()
df2 = px.data.stocks()


@pytest.mark.easy_dashboard
@pytest.fixture(scope="module", autouse=True)
def setup_test_environment():
    # We only need to install chromedriver outside CI.
    if not os.getenv("CI"):
        chromedriver_autoinstaller.install()


@pytest.mark.parametrize(
    "model_name",
    ["gpt-3.5-turbo"],
    ids=["gpt-3.5"],
)
@pytest.mark.filterwarnings("ignore::langchain_core._api.beta_decorator.LangChainBetaWarning")
@pytest.mark.filterwarnings("ignore::UserWarning")
@pytest.mark.filterwarnings("ignore:HTTPResponse.getheader()")
def test_simple_dashboard(dash_duo, model_name):  # noqa: PLR0915
    input_text = """
    I need a page with 1 table.
    The table shows the tech companies stock data.

    I need a second page showing 2 cards and one chart.
    The first card says 'The Gapminder dataset provides historical data on countries' development indicators.'
    The chart is an scatter plot showing life expectancy vs. GDP per capita by country.
    Life expectancy on the y axis, GDP per capita on the x axis, and colored by continent.
    The second card says 'Data spans from 1952 to 2007 across various countries.'
    The layout uses a grid of 3 columns and 2 rows.

    Row 1: The first row has three columns:
    The first column is occupied by the first card.
    The second and third columns are spanned by the chart.

    Row 2: The second row mirrors the layout of the first row with respect to chart,
    but the first column is occupied by the second card.

    Add a filter to filter the scatter plot by continent.
    Add a second filter to filter the chart by year.
    """
    report_dir = "tests/integration/reports"
    os.makedirs(report_dir, exist_ok=True)

    try:
        vizro_type = os.environ["VIZRO_TYPE"]
    except KeyError:
        vizro_type = "local_env"

    dashboard = vizro_ai._dashboard([df1, df2], input_text)
    app = Vizro().build(dashboard).dash
    dash_duo.start_server(app)
    assert dash_duo.get_logs() == []

    pages = [1 if dashboard.pages else 0][0]
    pages_num = [1 if len(dashboard.pages) == 2 else 0][0]

    try:
        grid_1 = [1 if dashboard.pages[0].layout.grid[0] == [0] else 0][0]
    except IndexError:
        grid_1 = 0
    try:
        grid_2 = [1 if dashboard.pages[1].layout.grid[0] == [0, 1, 1] else 0][0]
    except IndexError:
        grid_2 = 0

    try:
        components_num_1 = [1 if len(dashboard.pages[0].components) == 1 else 0][0]
    except IndexError:
        components_num_1 = 0
    try:
        components_num_2 = [1 if len(dashboard.pages[1].components) == 3 else 0][0]
    except IndexError:
        components_num_2 = 0

    try:
        controls_num_1 = [1 if len(dashboard.pages[0].controls) == 0 else 0][0]
    except IndexError:
        controls_num_1 = 0
    try:
        controls_num_2 = [1 if len(dashboard.pages[1].controls) == 2 else 0][0]
    except IndexError:
        controls_num_2 = 0

    try:
        comps_1 = [components.type for components in dashboard.pages[0].components]
        components_types_1 = [1 if comps_1.count("ag_grid") == 1 else 0][0]
    except IndexError:
        components_types_1 = 0
    try:
        comps_2 = [components.type for components in dashboard.pages[1].components]
        components_types_2 = [1 if comps_2.count("card") == 2 and comps_2.count("graph") == 1 else 0][0]
    except IndexError:
        components_types_2 = 0

    try:
        cntrls_2 = [controls.type for controls in dashboard.pages[1].controls]
        controls_types_2 = [1 if cntrls_2.count("filter") == 2 else 0][0]
    except IndexError:
        controls_types_2 = 0

    prescore = [
        pages,
        pages_num,
        grid_1,
        grid_2,
        components_num_1,
        components_num_2,
        controls_num_1,
        controls_num_2,
        components_types_1,
        components_types_2,
        controls_types_2,
    ]
    score = sum(prescore)

    with open(f"{report_dir}/report_model_{model_name}.csv", "a", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        writer.writerow([f"Vizro type = {vizro_type}, Datetime = {datetime.now()}"])
        writer.writerow([])
        writer.writerow(["Description, Score"])
        writer.writerow([f"Pages exists, {pages}"])
        writer.writerow([f"Correct pages number, {pages_num}"])
        writer.writerow([f"Correct grid first page, {grid_1}"])
        writer.writerow([f"Correct grid second page, {grid_2}"])
        writer.writerow([f"Correct components number first page, {components_num_1}"])
        writer.writerow([f"Correct components number second page, {components_num_2}"])
        writer.writerow([f"Correct controls number first page, {controls_num_1}"])
        writer.writerow([f"Correct controls number second page, {controls_num_2}"])
        writer.writerow([f"Correct components types first page, {components_types_1}"])
        writer.writerow([f"Correct components types second page, {components_types_2}"])
        writer.writerow([f"Correct controls types second page, {controls_types_2}"])
        writer.writerow([f"Total, {(score / len(prescore)):.4f}"])
        writer.writerow([])
        writer.writerow([])
