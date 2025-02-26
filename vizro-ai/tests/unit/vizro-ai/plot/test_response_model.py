import pandas as pd
import plotly.express as ppx
import pytest
import vizro.plotly.express as px

from vizro_ai.plot._response_models import (
    BaseChartPlan,
    ChartPlan,
    ChartPlanFactory,
    _check_chart_code,
    _strip_markdown,
)

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


@pytest.fixture
def sample_df():
    return pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})


@pytest.fixture
def valid_chart_code():
    return """def custom_chart(data_frame):
    import plotly.express as px
    return px.scatter(data_frame, x='x', y='y')"""


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


def test_chart_plan_factory_with_base_chart_plan(sample_df, valid_chart_code):
    """Test factory creates validated BaseChartPlan."""
    ValidatedModel = ChartPlanFactory(data_frame=sample_df, chart_plan=BaseChartPlan)

    assert issubclass(ValidatedModel, BaseChartPlan)
    assert ValidatedModel is not BaseChartPlan

    instance = ValidatedModel(
        chart_type="scatter", imports=["import plotly.express as px"], chart_code=valid_chart_code
    )
    assert isinstance(instance, BaseChartPlan)


def test_chart_plan_factory_with_chart_plan(sample_df, valid_chart_code):
    """Test factory creates validated ChartPlan."""
    ValidatedModel = ChartPlanFactory(data_frame=sample_df, chart_plan=ChartPlan)

    assert issubclass(ValidatedModel, ChartPlan)
    assert ValidatedModel is not ChartPlan

    instance = ValidatedModel(
        chart_type="scatter",
        imports=["import plotly.express as px"],
        chart_code=valid_chart_code,
        chart_insights="Test insights",
        code_explanation="Test explanation",
    )
    assert isinstance(instance, ChartPlan)


def test_chart_plan_factory_validation_failure(sample_df):
    """Test factory validation fails with invalid code."""
    ValidatedModel = ChartPlanFactory(data_frame=sample_df, chart_plan=BaseChartPlan)

    with pytest.raises(ValueError, match="The chart code must be wrapped in a function named"):
        ValidatedModel(chart_type="scatter", imports=["import plotly.express as px"], chart_code="invalid_code")


def test_base_chart_plan_without_validation(valid_chart_code):
    """Test BaseChartPlan without validation."""
    instance = BaseChartPlan(chart_type="scatter", imports=["import plotly.express as px"], chart_code=valid_chart_code)
    assert isinstance(instance, BaseChartPlan)


def test_chart_plan_without_validation(valid_chart_code):
    """Test ChartPlan without validation."""
    instance = ChartPlan(
        chart_type="scatter",
        imports=["import plotly.express as px"],
        chart_code=valid_chart_code,
        chart_insights="Test insights",
        code_explanation="Test explanation",
    )
    assert isinstance(instance, ChartPlan)
    assert instance.chart_insights == "Test insights"
    assert instance.code_explanation == "Test explanation"


def test_chart_plan_factory_preserves_fields(sample_df, valid_chart_code):
    """Test factory preserves all fields from base class."""
    ValidatedModel = ChartPlanFactory(data_frame=sample_df, chart_plan=ChartPlan)

    instance = ValidatedModel(
        chart_type="scatter",
        imports=["import plotly.express as px"],
        chart_code=valid_chart_code,
        chart_insights="Test insights",
        code_explanation="Test explanation",
    )

    # Check all fields are preserved
    assert instance.chart_type == "scatter"
    assert instance.imports == ["import plotly.express as px"]
    assert instance.chart_code == valid_chart_code
    assert instance.chart_insights == "Test insights"
    assert instance.code_explanation == "Test explanation"


def test_base_chart_plan_no_explanatory_fields(valid_chart_code):
    """Test BaseChartPlan doesn't have explanatory fields."""
    instance = BaseChartPlan(chart_type="scatter", imports=["import plotly.express as px"], chart_code=valid_chart_code)

    with pytest.raises(AttributeError):
        _ = instance.chart_insights

    with pytest.raises(AttributeError):
        _ = instance.code_explanation


class TestStripMarkdown:
    """Tests for the _strip_markdown function."""

    @pytest.mark.parametrize(
        "input_code, expected_output",
        [
            ('"""def custom_chart():\n    return None"""', "def custom_chart():\n    return None"),
            ("```python\ndef custom_chart():\n    return None\n```", "def custom_chart():\n    return None"),
            ("```py\ndef custom_chart():\n    return None\n```", "def custom_chart():\n    return None"),
            ("```\ndef custom_chart():\n    return None\n```", "def custom_chart():\n    return None"),
            ("def custom_chart():\n    return None", "def custom_chart():\n    return None"),
        ],
    )
    def test_strip_markdown_variations(self, input_code, expected_output):
        assert _strip_markdown(input_code) == expected_output


class TestCheckChartCode:
    """Tests for the _check_chart_code function."""

    def test_valid_chart_code(self):
        valid_code = """def custom_chart(data_frame):
    return px.scatter(data_frame)"""
        assert _check_chart_code(valid_code) == valid_code

    @pytest.mark.parametrize(
        "invalid_code, expected_error",
        [
            (
                """def wrong_name(data_frame):
    return px.scatter(data_frame)""",
                "The chart code must be wrapped in a function named `custom_chart`",
            ),
            (
                """def custom_chart(df):
    return px.scatter(df)""",
                "The chart code must accept a single argument `data_frame`",
            ),
            (
                """import px
def custom_chart(data_frame):
    return px.scatter(data_frame)""",
                None,  # Should pass - imports before function are stripped
            ),
        ],
    )
    def test_invalid_chart_code(self, invalid_code, expected_error):
        if expected_error:
            with pytest.raises(ValueError, match=expected_error):
                _check_chart_code(invalid_code)
        else:
            result = _check_chart_code(invalid_code)
            assert result.startswith("def custom_chart")
