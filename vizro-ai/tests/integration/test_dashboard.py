"""Tests for dashboard using VizroAI."""

import csv
import os
from datetime import datetime
from typing import Dict, List

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


def logic(  # noqa: PLR0912, PLR0913, PLR0915
    dashboard,
    model_name,
    prompt_tier,
    pages: Dict[str, int],
    components: List[Dict[str, int]],
    controls: List[Dict[str, int]],
    components_types: List[Dict[str, int]],
    controls_types: List[Dict[str, int]],
):
    report_dir = "tests/integration/reports"
    os.makedirs(report_dir, exist_ok=True)

    try:
        vizro_type = os.environ["VIZRO_TYPE"]
        branch = os.environ["BRANCH"]
        python_version = os.environ["PYTHON_VERSION"]
    except KeyError:
        vizro_type = "local_env"
        branch = "local"
        python_version = "local"

    pages_exist = [1 if dashboard.pages else 0]
    pages_exist_report = bool(pages_exist[0])
    pages_num = [1 if len(dashboard.pages) == pages["num"] else 0]
    pages_num_report = [f'{pages["num"]} page(s) for dashboard is {bool(components)}']

    components_num = []
    components_num_report = []
    if components:
        for component in components:
            try:
                components = [
                    1 if len(dashboard.pages[component["page_num"] - 1].components) == component["num"] else 0
                ][0]
            except IndexError:
                components = 0
            components_num.append(components)
            components_num_report.append(
                f'{component["num"]} component(s) for page {component["page_num"]} is {bool(components)}'
            )

    controls_num = []
    controls_num_report = []
    if controls:
        for control in controls:
            try:
                controls = [1 if len(dashboard.pages[control["page_num"] - 1].controls) == control["num"] else 0][0]
            except IndexError:
                controls = 0
            controls_num.append(controls)
            controls_num_report.append(
                f'{control["num"]} control(s) for page {control["page_num"]} is {bool(controls)}'
            )

    components_types_names = []
    components_types_names_report = []
    if components_types:
        for components_type in components_types:
            try:
                comps = [components.type for components in dashboard.pages[components_type["page_num"] - 1].components]
                components_types = [1 if comps.count(components_type["type"]) == components_type["num"] else 0][0]
            except IndexError:
                components_types = 0
            components_types_names.append(components_types)
            components_types_names_report.append(
                f'{components_type["num"]} components_type(s) {components_type["type"]} '
                f'for page {components_type["page_num"]} is {bool(controls)}'
            )

    controls_types_names = []
    controls_types_names_report = []
    if controls_types:
        for controls_type in controls_types:
            try:
                cntrls = [controls.type for controls in dashboard.pages[controls_type["page_num"] - 1].controls]
                controls_types = [1 if cntrls.count(controls_type["type"]) == controls_type["num"] else 0][0]
            except IndexError:
                controls_types = 0
            controls_types_names.append(controls_types)
            controls_types_names_report.append(
                f'{controls_type["num"]} controls_type(s) {controls_type["type"]} '
                f'for page {controls_type["page_num"]} is {bool(controls)}'
            )

    prescore = []
    pages_exist.extend(pages_num)
    prescore.extend(pages_exist)
    prescore.extend(components_num)
    prescore.extend(controls_num)
    prescore.extend(components_types_names)
    prescore.extend(controls_types_names)
    score = sum(prescore)

    pages_score = (sum(pages_exist) / len(pages_exist))
    components_score = (sum(components_num) / len(components_num))
    component_types_score = (sum(components_types_names) / len(components_types_names))
    controls_score = (sum(controls_num) / len(controls_num))
    controls_types_score = (sum(controls_types_names) / len(controls_types_names))
    total = [pages_score, components_score, component_types_score, controls_score, controls_types_score]
    total_score = (sum(total) / len(total))

    with open(f"{report_dir}/report_model_{model_name}_new.csv", "a", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        writer.writerow(["timestamp, vizro_type, branch, python_version, model, prompt_tier, total_score, pages_score, components_score, component_types_score, controls_score, controls_types_score"])
        writer.writerow([f"{datetime.now()}, {vizro_type}, {branch}, {python_version}, {model_name}, {prompt_tier}, {total_score}, {pages_score}, {components_score}, {component_types_score}, {controls_score}, {controls_types_score}"])

    # for cmd output
    print(f"Pages exists: {pages_exist_report}")  # noqa: T201
    print(f"Correct pages number: {pages_num_report}")  # noqa: T201
    print(f"Components: {components_num_report}")  # noqa: T201
    print(f"Correct controls number: {controls_num_report}")  # noqa: T201
    print(f"Correct components types: {components_types_names_report}")  # noqa: T201
    print(f"Correct controls types: {controls_types_names_report}")  # noqa: T201
    print(f"Total, {(score / len(prescore)):.4f}")  # noqa: T201


@pytest.mark.easy_dashboard
@pytest.mark.parametrize(
    "model_name",
    ["gpt-3.5-turbo"],
    ids=["gpt-3.5"],
)
@pytest.mark.filterwarnings("ignore::langchain_core._api.beta_decorator.LangChainBetaWarning")
@pytest.mark.filterwarnings("ignore::UserWarning")
@pytest.mark.filterwarnings("ignore:HTTPResponse.getheader()")
def test_simple_dashboard(dash_duo, model_name):
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

    dashboard = vizro_ai._dashboard([df1, df2], input_text)
    app = Vizro().build(dashboard).dash
    dash_duo.start_server(app)
    assert dash_duo.get_logs() == []

    logic(
        dashboard=dashboard,
        model_name=model_name,
        prompt_tier="easy",
        pages={"num": 2},
        components=[{"page_num": 1, "num": 1}, {"page_num": 2, "num": 3}],
        controls=[{"page_num": 1, "num": 0}, {"page_num": 2, "num": 2}],
        components_types=[
            {"page_num": 1, "type": "ag_grid", "num": 1},
            {"page_num": 2, "type": "card", "num": 2},
            {"page_num": 2, "type": "graph", "num": 1},
        ],
        controls_types=[{"page_num": 2, "type": "filter", "num": 2}],
    )
