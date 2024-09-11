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

    def logic(
            pages={"num": 2},
            components=[{"page_num": 1, "num": 1}, {"page_num": 2, "num": 3}],
            controls=[{"page_num": 1, "num": 0}, {"page_num": 2, "num": 2}],
            components_types=[{"page_num": 1, "type": "ag_grid", "num": 1}, {"page_num": 2, "type": "card", "num": 2},
                              {"page_num": 2, "type": "graph", "num": 1}],
            controls_types=[{"page_num": 2, "type": "filter", "num": 2}]
    ):
        pages_exist = [1 if dashboard.pages else 0][0]
        pages_num = [1 if len(dashboard.pages) == pages["num"] else 0][0]

        components_num = []
        if components:
            for component in components:
                try:
                    components = [1 if len(dashboard.pages[component["page_num"]-1].components) == component["num"] else 0][0]
                except IndexError:
                    components = 0
                components_num.append(components)

        controls_num = []
        if controls:
            for control in controls:
                try:
                    controls = [1 if len(dashboard.pages[control["page_num"]-1].controls) == control["num"] else 0][0]
                except IndexError:
                    controls = 0
                controls_num.append(controls)

        components_types_names = []
        if components_types:
            for components_type in components_types:
                try:
                    comps = [components.type for components in dashboard.pages[components_type["page_num"]-1].components]
                    components_types = [1 if comps.count(components_type["type"]) == components_type["num"] else 0][0]
                except IndexError:
                    components_types = 0
                components_types_names.append(components_types)

        controls_types_names = []
        if controls_types:
            for controls_type in controls_types:
                try:
                    cntrls = [controls.type for controls in dashboard.pages[controls_type["page_num"]-1].controls]
                    controls_types = [1 if cntrls.count(controls_type["type"]) == controls_type["num"] else 0][0]
                except IndexError:
                    controls_types = 0
                controls_types_names.append(controls_types)

        prescore = [
            pages_exist,
            pages_num,
        ]
        prescore.extend(components_num)
        prescore.extend(controls_num)
        prescore.extend(components_types_names)
        prescore.extend(controls_types_names)
        print("prescore: ", prescore)
        score = sum(prescore)

        with open(f"{report_dir}/report_model_{model_name}.csv", "a", newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=",")
            writer.writerow([f"Vizro type = {vizro_type}, Datetime = {datetime.now()}"])
            writer.writerow([])
            writer.writerow(["Description, Score"])
            writer.writerow([f"Pages exists: {pages_exist}"])
            writer.writerow([f"Correct pages number: {pages_num}"])
            writer.writerow([f"Correct components number: {components_num}"])
            writer.writerow([f"Correct controls number: {controls_num}"])
            writer.writerow([f"Correct components types: {components_types_names}"])
            writer.writerow([f"Correct controls types: {controls_types_names}"])
            writer.writerow([f"Total, {(score / len(prescore)):.4f}"])
            writer.writerow([])
            writer.writerow([])

    logic(
        pages={"num": 2},
        components=[{"page_num": 1, "num": 1}, {"page_num": 2, "num": 3}],
        controls=[{"page_num": 1, "num": 0}, {"page_num": 2, "num": 2}],
        components_types=[{"page_num": 1, "type": "ag_grid", "num": 1}, {"page_num": 2, "type": "card", "num": 2},
                          {"page_num": 2, "type": "graph", "num": 1}],
        controls_types=[{"page_num": 2, "type": "filter", "num": 2}]
    )
