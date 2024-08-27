import pytest
from vizro_ai.plot2._response_models import ChartPlanStatic, ChartPlanDynamicFactory, ADDITIONAL_IMPORTS
import pytest
import pandas as pd
import numpy as np
from vizro.models.types import capture
import vizro.plotly.express as px


@pytest.fixture()
def chart_plan():
    return ChartPlanStatic(
        chart_type="Bubble Chart",
        imports=["import plotly.express as px"],
        chart_code="""def custom_chart(data_frame):
    fig = px.scatter(data_frame, x='sepal_width', y='petal_width')
    return fig
""",
        chart_insights="Very good insights",
        code_explanation="Very good explanation",
    )


class TestChartPlanStaticInstantiation:
    def test_check_chart_code_valid(self):
        chart_plan_valid = ChartPlanStatic(
            chart_type="Bubble Chart",
            imports=["import plotly.express as px"],
            chart_code="""def custom_chart(data_frame):
    fig = px.scatter(data_frame, x='sepal_width', y='petal_width')
    return fig
""",
            chart_insights="Very good insights",
            code_explanation="Very good explanation",
        )
        assert isinstance(chart_plan_valid, ChartPlanStatic)

    @pytest.mark.parametrize(
        "chart_code, error_type, error_message",
        [
            (
                """def wrong_name(data_frame):
    fig = px.scatter(data_frame, x='sepal_width', y='petal_width')
    return fig
        """,
                ValueError,
                "The chart code must be wrapped in a function named",
            ),
            (
                """def custom_chart(df):
    fig = px.scatter(df, x='sepal_width', y='petal_width')
    return fig
        """,
                ValueError,
                "The chart code must accept a single argument `data_frame`, and it should be the first argument of the chart.",
            ),
        ],
    )
    def test_check_chart_code_invalid(self, chart_code, error_type, error_message):
        with pytest.raises(error_type, match=error_message):
            chart_plan_invalid = ChartPlanStatic(
                chart_type="Bubble Chart",
                imports=["import plotly.express as px"],
                chart_code=chart_code,
                chart_insights="Very good insights",
                code_explanation="Very good explanation",
            )


class TestChartPlanDynamicFactory:
    def test_check_chart_code_valid(self):
        chart_plan_dynamic = ChartPlanDynamicFactory(data_frame=px.data.iris())
        chart_plan_dynamic_valid = chart_plan_dynamic(
            chart_type="Bubble Chart",
            imports=["import plotly.express as px"],
            chart_code="""def custom_chart(data_frame):
    fig = px.scatter(data_frame, x='sepal_width', y='petal_width')
    return fig
""",
            chart_insights="Very good insights",
            code_explanation="Very good explanation",
        )
        assert isinstance(chart_plan_dynamic_valid, ChartPlanStatic)

    @pytest.mark.parametrize(
        "chart_code, error_type, error_message",
        [
            (
                """def custom_chart(data_frame):
    fig = px.scatte(data_frame, x='sepal_width', y='petal_width')
    return fig
        """,
                ValueError,
                "Produced code execution failed the following error: <module 'plotly.express' has",
            ),
            (
                """def custom_chart(data_frame):
    fig = px.scatter(data_frame, x='sepal_width', y='petal_width')
    return fi
        """,
                ValueError,
                "Produced code execution failed the following error: <name 'fi' is not defined>.",
            ),
            (
                """def custom_chart(data_frame):
    fig = px.scatter(data_frame, x='sepal_width', y='petal_width')
    return "foo"
        """,
                ValueError,
                "Expected chart code to return a plotly go.Figure object, but got",
            ),
        ],
    )
    def test_check_chart_code_evaluation_invalid(self, chart_code, error_type, error_message):
        chart_plan_dynamic = ChartPlanDynamicFactory(data_frame=px.data.iris())
        with pytest.raises(error_type, match=error_message):
            chart_plan_dynamic_invalid = chart_plan_dynamic(
                chart_type="Bubble Chart",
                imports=["import plotly.express as px"],
                chart_code=chart_code,
                chart_insights="Very good insights",
                code_explanation="Very good explanation",
            )

    class TestChartPlanStaticMethodsProperties:
        def test_code(self, chart_plan):
            assert (
                chart_plan.code
                == """import plotly.express as px


def custom_chart(data_frame):
    fig = px.scatter(data_frame, x="sepal_width", y="petal_width")
    return fig
"""
            )
        
        def test_code_vizro(self, chart_plan):
            assert (
                chart_plan.code_vizro
                == """from vizro.models.types import capture
import vizro.plotly.express as px


@capture("graph")
def custom_chart(data_frame):
    fig = px.scatter(data_frame, x="sepal_width", y="petal_width")
    return fig
""")

    