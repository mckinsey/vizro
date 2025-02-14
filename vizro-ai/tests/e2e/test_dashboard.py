"""Tests for dashboard using VizroAI."""

import csv
import os
import statistics
from collections import Counter
from datetime import datetime

import chromedriver_autoinstaller
import numpy as np
import pytest
import vizro.plotly.express as px
from prompts import complex_prompt, easy_prompt, medium_prompt
from vizro import Vizro

from vizro_ai import VizroAI

df1 = px.data.gapminder()
df2 = px.data.stocks()
df3 = px.data.tips()
df4 = px.data.wind()


@pytest.fixture(scope="module", autouse=True)
def setup_test_environment():
    # We only need to install chromedriver outside CI.
    if not os.getenv("CI"):
        chromedriver_autoinstaller.install()


# If len() is 0, it means that nothing was entered for this score in config,
# in this case it should be 1.
def score_calculator(metrics_score: list[int]):
    return statistics.mean(metrics_score) if len(metrics_score) != 0 else 1


def logic(  # noqa: PLR0912, PLR0913, PLR0915
    dashboard,
    model_name,
    dash_duo,
    prompt_tier,
    prompt_name,
    prompt_text,
    config: dict,
):
    """Calculates all separate scores. Creates csv report.

    Attributes:
        dashboard: VizroAI generated dashboard
        model_name: GenAI model name
        dash_duo: dash_duo fixture
        prompt_tier: complexity of the prompt
        prompt_name: short prompt description
        prompt_text: prompt text
        config: json config of the expected dashboard

    """
    # TODO: Add layout score
    report_dir = "tests/e2e/reports"
    os.makedirs(report_dir, exist_ok=True)

    try:
        app = Vizro().build(dashboard).dash
        dash_duo.start_server(app)
        app_started = 1
        app_started_report = "App started!"
    except Exception as e:
        app_started = 0
        app_started_report = "App didn't start!"
        print(f"App start exception: {e}")  # noqa: T201

    try:
        assert dash_duo.get_logs() == []
        no_browser_console_errors = 1
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

    pages_exist = [1 if dashboard.pages else 0][0]
    pages_exist_report = bool(pages_exist)
    pages_num = [1 if len(dashboard.pages) == len(config["pages"]) else 0]
    pages_num_report = [f"{len(config['pages'])} page(s) for dashboard is {bool(pages_num[0])}"]

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
            f"{len(config['pages'][page]['components'])} component(s) for page {page} is {bool(components)}"
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
            f"{len(config['pages'][page]['controls'])} control(s) for page {page} is {bool(controls)}"
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

    # Every separate score has its own weight.
    scores = [
        {"score_name": "app_started_score", "weight": 0.4, "score": app_started},
        {"score_name": "no_browser_console_errors_score", "weight": 0.1, "score": no_browser_console_errors},
        {"score_name": "pages_score", "weight": 0.3, "score": pages_exist},
        {"score_name": "pages_number", "weight": 0.2, "score": score_calculator(metrics_score=pages_num)},
        {"score_name": "components_score", "weight": 0.2, "score": score_calculator(metrics_score=components_num)},
        {
            "score_name": "component_types_score",
            "weight": 0.2,
            "score": score_calculator(metrics_score=components_types_names),
        },
        {"score_name": "controls_score", "weight": 0.2, "score": score_calculator(metrics_score=controls_num)},
        {
            "score_name": "controls_types_score",
            "weight": 0.2,
            "score": score_calculator(metrics_score=controls_types_names),
        },
    ]

    scores_values = np.array([score["score"] for score in scores])
    weights = np.array([score["weight"] for score in scores])
    weighted_score = np.average(scores_values, weights=weights)

    # csv report creation
    data_rows = [
        datetime.now(),
        vizro_type,
        branch,
        python_version,
        model_name,
        prompt_tier,
        prompt_name,
        weighted_score,
    ]
    data_rows.extend(score["score"] for score in scores)
    data_rows.extend([prompt_text])

    with open(f"{report_dir}/report_model_{model_name}_{vizro_type}.csv", "a", newline=""):
        with open(f"{report_dir}/report_model_{model_name}_{vizro_type}.csv", "r+", newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=",")
            first_line = csvfile.readline()
            if not first_line:
                header_rows = [
                    "timestamp",
                    "vizro_type",
                    "branch",
                    "python_version",
                    "model",
                    "prompt_tier",
                    "prompt_name",
                    "weighted_score",
                ]
                header_rows.extend(score["score_name"] for score in scores)
                header_rows.extend(["prompt_text"])
                writer.writerow(header_rows)
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


@pytest.mark.parametrize(
    "model_name",
    [
        "gpt-4o-mini",
        "gpt-4o",
        "gpt-4-turbo",
    ],
    ids=[
        "gpt-4o-mini",
        "gpt-4o",
        "gpt-4-turbo",
    ],
)
@pytest.mark.parametrize(
    "tier_type, prompt_name, prompt_text, expected_config, dfs",
    [
        (
            easy_prompt["tier_type"],
            easy_prompt["prompt_name"],
            easy_prompt["prompt_text"],
            easy_prompt["expected_config"],
            [df1, df2],
        ),
        (
            medium_prompt["tier_type"],
            medium_prompt["prompt_name"],
            medium_prompt["prompt_text"],
            medium_prompt["expected_config"],
            [df1, df2, df3],
        ),
        (
            complex_prompt["tier_type"],
            complex_prompt["prompt_name"],
            complex_prompt["prompt_text"],
            complex_prompt["expected_config"],
            [df1, df2, df3, df4],
        ),
    ],
)
def test_dashboard_openai(dash_duo, model_name, tier_type, prompt_name, prompt_text, expected_config, dfs):  # noqa: PLR0913
    created_dashboard = VizroAI(model=model_name).dashboard(dfs, prompt_text)

    logic(
        dashboard=created_dashboard,
        model_name=model_name,
        dash_duo=dash_duo,
        prompt_tier=tier_type,
        prompt_name=prompt_name,
        prompt_text=prompt_text.replace("\n", " "),
        config=expected_config,
    )


@pytest.mark.parametrize(
    "model_name",
    [
        "claude-3-5-sonnet-latest",
        "claude-3-opus-latest",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
    ],
    ids=[
        "claude-3-5-sonnet-latest",
        "claude-3-opus-latest",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
    ],
)
@pytest.mark.parametrize(
    "tier_type, prompt_name, prompt_text, expected_config, dfs",
    [
        (
            easy_prompt["tier_type"],
            easy_prompt["prompt_name"],
            easy_prompt["prompt_text"],
            easy_prompt["expected_config"],
            [df1, df2],
        ),
    ],
)
def test_dashboard_anthropic(dash_duo, model_name, tier_type, prompt_name, prompt_text, expected_config, dfs):  # noqa: PLR0913
    created_dashboard = VizroAI(model=model_name).dashboard(dfs, prompt_text)

    logic(
        dashboard=created_dashboard,
        model_name=model_name,
        dash_duo=dash_duo,
        prompt_tier=tier_type,
        prompt_name=prompt_name,
        prompt_text=prompt_text.replace("\n", " "),
        config=expected_config,
    )
