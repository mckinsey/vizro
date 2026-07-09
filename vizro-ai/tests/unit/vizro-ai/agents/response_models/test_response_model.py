"""Tests for the declarative chart plan models (no code execution)."""

import plotly.express as px
import plotly.graph_objects as go
import pytest
from pydantic import ValidationError

from vizro_ai.agents.response_models import CHART_TYPES, BaseChartPlan, ChartPlan, ChartPlanFactory
from vizro_ai.agents.response_models._response_models import allowed_encodings, styling_options, validate_against_data


@pytest.fixture
def iris():
    return px.data.iris()


class TestGrammarDiscovery:
    """The chart grammar is derived by introspecting plotly express."""

    def test_common_chart_types_present(self):
        assert {"bar", "line", "scatter", "pie", "box", "histogram"} <= set(CHART_TYPES)

    def test_map_and_geo_charts_excluded(self):
        assert not ({"scatter_mapbox", "choropleth", "scatter_geo", "line_map"} & set(CHART_TYPES))

    def test_density_heatmap_kept_despite_map_substring(self):
        assert "density_heatmap" in CHART_TYPES

    def test_encodings_and_options_derive_from_signature(self):
        assert {"x", "y", "color"} <= allowed_encodings("bar")
        assert {"names", "values"} <= allowed_encodings("pie")
        assert "barmode" in styling_options("bar")


class TestBaseChartPlan:
    def test_valid_plan(self):
        plan = BaseChartPlan(chart_type="scatter", encodings={"x": "sepal_width", "y": "sepal_length"})
        assert plan.chart_type == "scatter"

    def test_unknown_chart_type_rejected(self):
        with pytest.raises(ValidationError, match="Unknown chart_type"):
            BaseChartPlan(chart_type="banana", encodings={})

    def test_referenced_columns(self):
        plan = BaseChartPlan(chart_type="bar", encodings={"x": "continent", "y": "pop", "color": "continent"})
        assert set(plan.referenced_columns()) == {"continent", "pop"}


class TestRendering:
    def test_figure_and_json(self, iris):
        plan = BaseChartPlan(
            chart_type="scatter", encodings={"x": "sepal_width", "y": "sepal_length", "color": "species"}
        )
        assert isinstance(plan.figure(iris), go.Figure)
        assert '"data"' in plan.to_figure_json(iris)

    def test_code_and_code_vizro(self, iris):
        plan = BaseChartPlan(chart_type="bar", encodings={"x": "species", "y": "sepal_length"}, title="t")
        assert "px.bar(data_frame" in plan.code and "x='species'" in plan.code
        # code_vizro is a standard vizro.plotly.express chart for vm.Graph — not a @capture custom chart
        assert "import vizro.plotly.express as px" in plan.code_vizro
        assert "px.bar(data_frame" in plan.code_vizro
        assert "@capture" not in plan.code_vizro

    def test_chart_function_returns_figure(self, iris):
        plan = BaseChartPlan(chart_type="scatter", encodings={"x": "sepal_width", "y": "sepal_length"})
        assert isinstance(plan.chart_function(iris), go.Figure)
        assert callable(plan.get_chart_function(chart_name="my_chart"))


class TestValidateAgainstData:
    def test_valid(self, iris):
        plan = BaseChartPlan(chart_type="scatter", encodings={"x": "sepal_width", "y": "sepal_length"})
        assert validate_against_data(plan, iris) == []

    def test_missing_column(self, iris):
        plan = BaseChartPlan(chart_type="scatter", encodings={"x": "nope"})
        assert any("nope" in e for e in validate_against_data(plan, iris))

    def test_invalid_encoding_for_chart_type(self, iris):
        plan = BaseChartPlan(chart_type="pie", encodings={"names": "species", "size": "sepal_length"})
        assert any("size" in e and "valid encoding" in e for e in validate_against_data(plan, iris))


class TestChartPlanFactory:
    """The factory validates a plan against a dataframe — by inspection, never by executing code."""

    def test_valid_plan_passes(self, iris):
        model = ChartPlanFactory(data_frame=iris)
        instance = model(chart_type="scatter", encodings={"x": "sepal_width", "y": "sepal_length"}, chart_insights="ok")
        assert isinstance(instance, ChartPlan)

    def test_missing_column_fails(self, iris):
        model = ChartPlanFactory(data_frame=iris)
        with pytest.raises(ValidationError, match="not in the data"):
            model(chart_type="scatter", encodings={"x": "nope"}, chart_insights="x")

    def test_base_chart_plan_variant(self, iris):
        model = ChartPlanFactory(data_frame=iris, chart_plan=BaseChartPlan)
        instance = model(chart_type="bar", encodings={"x": "species"})
        assert isinstance(instance, BaseChartPlan)
