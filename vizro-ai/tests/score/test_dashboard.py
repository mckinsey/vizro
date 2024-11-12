"""Tests for dashboard using VizroAI."""

import csv
import os
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

import chromedriver_autoinstaller
import pytest
import vizro.plotly.express as px
from vizro import Vizro

from vizro_ai import VizroAI

vizro_ai = VizroAI()

df1 = px.data.gapminder()
df2 = px.data.stocks()
df3 = px.data.tips()


@dataclass
class Components:
    type: Literal["ag_grid", "card", "graph"]


@dataclass
class Controls:
    type: Literal["filter", "parameter"]


@pytest.fixture(scope="module", autouse=True)
def setup_test_environment():
    # We only need to install chromedriver outside CI.
    if not os.getenv("CI"):
        chromedriver_autoinstaller.install()


def logic(  # noqa: PLR0912, PLR0915
    dashboard,
    model_name,
    dash_duo,
    prompt_tier,
    config: dict,
):
    """Calculates all separate scores. Creates csv report.

    Attributes:
        dashboard: VizroAI generated dashboard
        model_name: GenAI model name
        dash_duo: dash_duo fixture
        prompt_tier: complexity of the prompt
        config: json config of the expected dashboard

    """
    report_dir = "tests/score/reports"
    os.makedirs(report_dir, exist_ok=True)

    app = Vizro().build(dashboard).dash

    try:
        dash_duo.start_server(app)
        app_started = 1.0
        app_started_report = "App started!"
    except Exception as e:
        app_started = 0
        app_started_report = "App didn't start!"
        print(f"App start exception: {e}")  # noqa: T201

    try:
        assert dash_duo.get_logs() == []
        no_browser_console_errors = 1.0
        no_browser_console_errors_report = "No error logs in browser console!"
    except AssertionError as e:
        no_browser_console_errors = 0
        no_browser_console_errors_report = "Error logs in browser console found!"
        print(f"Browser console exception: {e}")  # noqa: T201

    Vizro._reset()

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
    pages_num = [1 if len(dashboard.pages) == len(config["pages"]) else 0]
    pages_num_report = [f'{len(config["pages"])} page(s) for dashboard is {bool(pages_num[0])}']

    components_num = []
    components_num_report = []
    for page in range(len(config["pages"])):
        try:
            components = [
                1 if len(dashboard.pages[page].components) == len(config["pages"][page]["components"]) else 0
            ][0]
        except IndexError:
            components = 0
        components_num.append(components)
        components_num_report.append(
            f'{len(config["pages"][page]["components"])} component(s) for page {page} is {bool(components)}'
        )

    controls_num = []
    controls_num_report = []
    for page in range(len(config["pages"])):
        try:
            controls = [1 if len(dashboard.pages[page].controls) == len(config["pages"][page]["controls"]) else 0][0]
        except IndexError:
            controls = 0
        controls_num.append(controls)
        controls_num_report.append(
            f'{len(config["pages"][page]["controls"])} control(s) for page {page} is {bool(controls)}'
        )

    components_types_names = []
    components_types_names_report = []
    try:
        for page in range(len(config["pages"])):
            components_dashboard = Counter([component.type for component in dashboard.pages[page].components])
            components_config = Counter([component.type for component in config["pages"][page]["components"]])
            for component_name in components_config:
                components_types = [
                    1 if components_config[component_name] == components_dashboard[component_name] else 0
                ][0]
                components_types_names.append(components_types)
                components_types_names_report.append(
                    f"{components_config[component_name]} components_type(s) {component_name} "
                    f"for page {page} is {bool(components_types)}"
                )
    except IndexError:
        components_types = 0
        components_types_names.append(components_types)
        components_types_names_report.append("page or component does not exists")

    controls_types_names = []
    controls_types_names_report = []
    try:
        for page in range(len(config["pages"])):
            controls_dashboard = Counter([control.type for control in dashboard.pages[page].controls])
            controls_config = Counter([control.type for control in config["pages"][page]["controls"]])
            for control_name in controls_config:
                controls_types = [1 if controls_config[control_name] == controls_dashboard[control_name] else 0][0]
                controls_types_names.append(controls_types)
                controls_types_names_report.append(
                    f"{controls_config[control_name]} controls_type(s) {control_name} "
                    f"for page {page} is {bool(controls_types)}"
                )
    except IndexError:
        controls_types = 0
        controls_types_names.append(controls_types)
        controls_types_names_report.append("page or control does not exists")

    pages_exist.extend(pages_num)

    # Every separate score has its own weight.
    app_started_score = {"weight": 0.4, "score": app_started}
    no_browser_console_errors_score = {"weight": 0.1, "score": no_browser_console_errors}
    pages_score = {"weight": 0.2, "score": sum(pages_exist) / len(pages_exist)}
    components_score = {"weight": 0.1, "score": sum(components_num) / len(components_num)}
    component_types_score = {"weight": 0.1, "score": sum(components_types_names) / len(components_types_names)}
    controls_score = {"weight": 0.1, "score": sum(controls_num) / len(controls_num)}
    controls_types_score = {"weight": 0.1, "score": sum(controls_types_names) / len(controls_types_names)}

    scores = [
        app_started_score,
        no_browser_console_errors_score,
        pages_score,
        components_score,
        component_types_score,
        controls_score,
        controls_types_score,
    ]
    # total_weight should be equal to 1
    total_weight = sum(score["weight"] for score in scores)
    # If total_weight is not equal to 1, we're recalculating weights for every separate score
    # and calculating final weighted_score for the created dashboard
    if total_weight != 1:
        scores = [{"weight": score["weight"] / total_weight, "score": score["score"]} for score in scores]
    weighted_score = round(sum(score["weight"] * score["score"] for score in scores), 1)

    # csv report creation

    data_rows = [
        datetime.now(),
        vizro_type,
        branch,
        python_version,
        model_name,
        prompt_tier,
        weighted_score,
        app_started_score["score"],
        no_browser_console_errors_score["score"],
        pages_score["score"],
        components_score["score"],
        component_types_score["score"],
        controls_score["score"],
        controls_types_score["score"],
    ]

    with open(f"{report_dir}/report_model_{model_name}_{vizro_type}.csv", "a", newline=""):
        with open(f"{report_dir}/report_model_{model_name}_{vizro_type}.csv", "r+", newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=",")
            first_line = csvfile.readline()
            if not first_line:
                writer.writerow(
                    [
                        "timestamp",
                        "vizro_type",
                        "branch",
                        "python_version",
                        "model",
                        "prompt_tier",
                        "weighted_score",
                        "app_started_score",
                        "no_browser_console_errors_score",
                        "pages_score",
                        "components_score",
                        "component_types_score",
                        "controls_score",
                        "controls_types_score",
                    ]
                )
                writer.writerow(data_rows)
            else:
                writer.writerow(data_rows)

    # Readable report for the console output
    print(f"App started: {app_started_report}")  # noqa: T201
    print(f"Console errors: {no_browser_console_errors_report}")  # noqa: T201
    print(f"Pages exists: {pages_exist_report}")  # noqa: T201
    print(f"Correct pages number: {pages_num_report}")  # noqa: T201
    print(f"Components: {components_num_report}")  # noqa: T201
    print(f"Correct controls number: {controls_num_report}")  # noqa: T201
    print(f"Correct components types: {components_types_names_report}")  # noqa: T201
    print(f"Correct controls types: {controls_types_names_report}")  # noqa: T201
    print(f"Weighted score: {weighted_score}")  # noqa: T201
    print(f"Scores: {scores}")  # noqa: T201


@pytest.mark.easy_dashboard
@pytest.mark.parametrize(
    "model_name",
    ["gpt-4o-mini"],
    ids=["gpt-4o-mini"],
)
@pytest.mark.filterwarnings("ignore::langchain_core._api.beta_decorator.LangChainBetaWarning")
@pytest.mark.filterwarnings("ignore::UserWarning")
@pytest.mark.filterwarnings("ignore:HTTPResponse.getheader()")
def test_easy_dashboard(dash_duo, model_name):
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

    dashboard = vizro_ai.dashboard([df1, df2], input_text)

    logic(
        dashboard=dashboard,
        model_name=model_name,
        dash_duo=dash_duo,
        prompt_tier="easy",
        config={
            "pages": [
                {
                    "components": [
                        Components(type="ag_grid"),
                    ],
                    "controls": [],
                },
                {
                    "components": [
                        Components(type="card"),
                        Components(type="card"),
                        Components(type="graph"),
                    ],
                    "controls": [
                        Controls(type="filter"),
                        Controls(type="filter"),
                    ],
                },
            ],
        },
    )


@pytest.mark.medium_dashboard
@pytest.mark.parametrize(
    "model_name",
    ["gpt-4o-mini"],
    ids=["gpt-4o-mini"],
)
@pytest.mark.filterwarnings("ignore::langchain_core._api.beta_decorator.LangChainBetaWarning")
@pytest.mark.filterwarnings("ignore::UserWarning")
@pytest.mark.filterwarnings("ignore:HTTPResponse.getheader()")
def test_medium_dashboard(dash_duo, model_name):
    input_text = """
    <Page 1>
    I need a page with 1 table and 1 line chart.
    The chart shows the stock price trends of GOOG and AAPL.
    The table shows the stock prices data details.

    <Page 2>
    I need a second page showing 1 card and 1 chart.
    The card says 'The Gapminder dataset provides historical data on countries' development indicators.'
    The chart is a scatter plot showing GDP per capita vs. life expectancy.
    GDP per capita on the x axis, life expectancy on the y axis, and colored by continent.
    Layout the card on the left and the chart on the right. The card takes 1/3 of the whole space on the left.
    The chart takes 2/3 of the whole space and is on the right.
    Add a filter to filter the scatter plot by continent.
    Add a second filter to filter the chart by year.

    <Page 3>
    This page displays the tips dataset. use two different charts to show data
    distributions. one chart should be a bar chart and the other should be a scatter plot.
    first chart is on the left and the second chart is on the right.
    Add a filter to filter data in the scatter plot by smoker.

    <Page 4>
    Create 3 cards on this page:
    1. The first card on top says "This page combines data from various sources
     including tips, stock prices, and global indicators."
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

    dashboard = vizro_ai.dashboard([df1, df2, df3], input_text)

    logic(
        dashboard=dashboard,
        model_name=model_name,
        dash_duo=dash_duo,
        prompt_tier="medium",
        config={
            "pages": [
                {
                    "components": [
                        Components(type="ag_grid"),
                        Components(type="graph"),
                    ],
                    "controls": [],
                },
                {
                    "components": [
                        Components(type="card"),
                        Components(type="graph"),
                    ],
                    "controls": [
                        Controls(type="filter"),
                        Controls(type="filter"),
                    ],
                },
                {
                    "components": [
                        Components(type="graph"),
                        Components(type="graph"),
                    ],
                    "controls": [
                        Controls(type="filter"),
                    ],
                },
                {
                    "components": [
                        Components(type="card"),
                        Components(type="card"),
                        Components(type="card"),
                    ],
                    "controls": [],
                },
            ],
        },
    )
