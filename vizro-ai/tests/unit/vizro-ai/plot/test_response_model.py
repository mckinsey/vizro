import plotly.express as ppx
import pytest
import vizro.plotly.express as px

from vizro_ai.plot._response_models import ChartPlan, ChartPlanFactory

df = px.data.iris()


@pytest.fixture()
def chart_plan():
    return ChartPlan(
        chart_type="Bubble Chart",
        imports=["import plotly.express as px"],
        chart_code="""def custom_chart(data_frame):
    fig = px.scatter(data_frame, x='sepal_width', y='petal_width')
    return fig
""",
        chart_insights="Very good insights",
        code_explanation="Very good explanation",
    )


class TestChartPlanInstantiation:
    """Tests for the ChartPlan class instantiation."""

    def test_check_chart_code_valid(self):
        chart_plan_valid = ChartPlan(
            chart_type="Bubble Chart",
            imports=["import plotly.express as px"],
            chart_code="""def custom_chart(data_frame):
    fig = px.scatter(data_frame, x='sepal_width', y='petal_width')
    return fig
""",
            chart_insights="Very good insights",
            code_explanation="Very good explanation",
        )
        assert isinstance(chart_plan_valid, ChartPlan)

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
                """The chart code must accept a single argument `data_frame`,
and it should be the first argument of the chart.""",
            ),
        ],
    )
    def test_check_chart_code_invalid(self, chart_code, error_type, error_message):
        with pytest.raises(error_type, match=error_message):
            ChartPlan(
                chart_type="Bubble Chart",
                imports=["import plotly.express as px"],
                chart_code=chart_code,
                chart_insights="Very good insights",
                code_explanation="Very good explanation",
            )


class TestChartPlanFactory:
    """Tests for the ChartPlanFactory class, mainly the execution of the chart code."""

    @pytest.mark.parametrize(
        "chart_code",
        [
            """def custom_chart(data_frame):
    random_other_module_import = np.arange(10)
    other_random_module_import = random.sample(range(10), 10)
    fig = px.scatter(data_frame, x='sepal_width', y='petal_width')
    return fig
""",
            """def custom_chart(data_frame):
    fig = px.scatter(data_frame, x='sepal_length', y='petal_length')
    return fig
""",
            """```python
def custom_chart(data_frame):
    random_other_module_import = np.arange(10)
    other_random_module_import = random.sample(range(10), 10)
    fig = px.scatter(data_frame, x='sepal_width', y='petal_width')
    return fig
```""",
            """```py
def custom_chart(data_frame):
    random_other_module_import = np.arange(10)
    other_random_module_import = random.sample(range(10), 10)
    fig = px.scatter(data_frame, x='sepal_width', y='petal_width')
    return fig
```""",
            """```
def custom_chart(data_frame):
    random_other_module_import = np.arange(10)
    other_random_module_import = random.sample(range(10), 10)
    fig = px.scatter(data_frame, x='sepal_width', y='petal_width')
    return fig
```""",
        ],
    )
    def test_execute_chart_code_valid(self, chart_code):
        chart_plan_dynamic = ChartPlanFactory(data_frame=px.data.iris())
        chart_plan_dynamic_valid = chart_plan_dynamic(
            chart_type="Bubble Chart",
            imports=["import plotly.express as px", "import numpy as np", "import random"],
            chart_code=chart_code,
            chart_insights="Very good insights",
            code_explanation="Very good explanation",
        )
        assert isinstance(chart_plan_dynamic_valid, ChartPlan)

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
    random_call = sp.arange(5)
    fig = px.scatter(data_frame, x='sepal_width', y='petal_width')
    return fig
        """,
                ValueError,
                "Produced code execution failed the following error: <name 'sp' is not defined>.",
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
    def test_execute_chart_code_invalid(self, chart_code, error_type, error_message):
        chart_plan_dynamic = ChartPlanFactory(data_frame=px.data.iris())
        with pytest.raises(error_type, match=error_message):
            chart_plan_dynamic(
                chart_type="Bubble Chart",
                imports=["import plotly.express as px"],
                chart_code=chart_code,
                chart_insights="Very good insights",
                code_explanation="Very good explanation",
            )

    class TestChartPlanMethodsProperties:
        """Tests for the methods and properties of the ChartPlan class."""

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
                == """import vizro.plotly.express as px
from vizro.models.types import capture


@capture("graph")
def custom_chart(data_frame):
    fig = px.scatter(data_frame, x="sepal_width", y="petal_width")
    return fig
"""
            )

        @pytest.mark.parametrize(
            "chart_name, expected_chart_name",
            [
                ("new_name", "new_name"),
                (None, "custom_chart"),
            ],
        )
        def test_get_complete_code_chart_name_arg(self, chart_plan, chart_name, expected_chart_name):
            assert (
                chart_plan._get_complete_code(chart_name=chart_name)
                == f"""import plotly.express as px


def {expected_chart_name}(data_frame):
    fig = px.scatter(data_frame, x="sepal_width", y="petal_width")
    return fig
"""
            )

        @pytest.mark.parametrize(
            "vizro, expected_fig",
            [
                (False, ppx.scatter(df, x="sepal_width", y="petal_width")),
                (True, px.scatter(df, x="sepal_width", y="petal_width")),
            ],
        )
        def test_get_fig_object(self, chart_plan, vizro, expected_fig):
            fig = chart_plan.get_fig_object(data_frame=df, vizro=vizro)
            assert fig == expected_fig
