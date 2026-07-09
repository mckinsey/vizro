"""Tests for the declarative chart plan models (no code execution)."""

import sys

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pytest
from pydantic import ValidationError

from vizro_ai.agents.response_models import CHART_TYPES, BaseChartPlan, ChartPlan, ChartPlanFactory
from vizro_ai.agents.response_models._response_models import (
    _contains_non_finite,
    _vizro_px_builder,
    allowed_encodings,
    render_px_code,
    styling_options,
    validate_against_data,
)


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

    def test_labels_and_title_are_not_options(self):
        """labels/title have dedicated fields, so they must not double as option keys."""
        assert not ({"labels", "title", "data_frame"} & styling_options("bar"))


class TestBaseChartPlan:
    def test_valid_plan(self):
        plan = BaseChartPlan(chart_type="scatter", encodings={"x": "sepal_width", "y": "sepal_length"})
        assert plan.chart_type == "scatter"

    def test_unknown_chart_type_rejected(self):
        with pytest.raises(ValidationError, match="Unknown chart_type"):
            BaseChartPlan(chart_type="banana", encodings={})

    def test_extra_top_level_keys_rejected(self):
        """A flat {'x': ...} (encodings misplaced at the top level) must fail, not silently vanish."""
        with pytest.raises(ValidationError, match="x"):
            BaseChartPlan.model_validate({"chart_type": "line", "x": "year", "y": "gdp"})

    def test_non_finite_option_values_rejected(self):
        with pytest.raises(ValidationError, match="non-finite"):
            BaseChartPlan.model_validate_json(
                '{"chart_type": "bar", "encodings": {"x": "a"}, "options": {"size_max": NaN}}'
            )

    def test_list_and_dict_option_values_accepted(self):
        plan = BaseChartPlan(
            chart_type="bar",
            encodings={"x": "species"},
            options={"range_y": [0, 100], "category_orders": {"species": ["virginica", "setosa"]}},
        )
        assert plan.options["range_y"] == [0, 100]

    def test_referenced_columns(self):
        plan = BaseChartPlan(chart_type="bar", encodings={"x": "continent", "y": "pop", "color": "continent"})
        assert set(plan.referenced_columns()) == {"continent", "pop"}

    def test_referenced_columns_with_list_encoding(self):
        plan = BaseChartPlan(chart_type="scatter_matrix", encodings={"dimensions": ["sepal_width", "sepal_length"]})
        assert plan.referenced_columns() == ["sepal_width", "sepal_length"]


class TestContainsNonFinite:
    @pytest.mark.parametrize(
        "value, expected",
        [
            (float("nan"), True),
            (float("inf"), True),
            (1.5, False),
            ("text", False),
            (True, False),
            ([1, float("nan")], True),
            ({"a": [0, 100]}, False),
            ({"a": float("-inf")}, True),
        ],
    )
    def test_values(self, value, expected):
        assert _contains_non_finite(value) is expected


class TestRendering:
    def test_figure_and_json(self, iris):
        plan = BaseChartPlan(
            chart_type="scatter", encodings={"x": "sepal_width", "y": "sepal_length", "color": "species"}
        )
        assert isinstance(plan.figure(iris), go.Figure)
        assert '"data"' in plan.to_figure_json(iris)

    def test_figure_applies_labels_title_and_options(self, iris):
        plan = BaseChartPlan(
            chart_type="bar",
            encodings={"x": "species", "y": "sepal_length"},
            title="Sepals",
            labels={"sepal_length": "Sepal length"},
            options={"range_y": [0, 100]},
        )
        fig = plan.figure(iris)
        assert fig.layout.title.text == "Sepals"
        assert tuple(fig.layout.yaxis.range) == (0, 100)

    @pytest.mark.parametrize(
        "chart_type, encodings",
        [
            ("pie", {"names": "species", "values": "sepal_length"}),
            ("histogram", {"x": "sepal_width"}),
            ("violin", {"x": "species", "y": "petal_length"}),
            ("line", {"x": "sepal_width", "y": "sepal_length", "line_group": "species"}),
            ("scatter", {"x": "sepal_width", "y": "sepal_length", "hover_data": ["species"]}),
        ],
    )
    def test_figure_across_chart_types(self, iris, chart_type, encodings):
        assert isinstance(BaseChartPlan(chart_type=chart_type, encodings=encodings).figure(iris), go.Figure)

    def test_code_with_list_encoding_and_labels(self, iris):
        plan = BaseChartPlan(
            chart_type="scatter",
            encodings={"x": "sepal_width", "y": "sepal_length", "hover_data": ["species"]},
            labels={"sepal_width": "Sepal width"},
        )
        assert "hover_data=['species']" in plan.code
        assert "labels={'sepal_width': 'Sepal width'}" in plan.code
        namespace: dict = {}
        exec(plan.code, namespace)
        assert namespace["custom_chart"](iris) == plan.figure(iris)

    def test_invalid_encoding_raises_instead_of_silently_dropping(self, iris):
        plan = BaseChartPlan(chart_type="bar", encodings={"xx": "species", "y": "sepal_length"})
        with pytest.raises(ValueError, match="not a valid encoding"):
            plan.figure(iris)

    def test_encoding_key_in_options_raises_instead_of_overriding(self, iris):
        plan = BaseChartPlan(chart_type="bar", encodings={"x": "species"}, options={"x": "sepal_length"})
        with pytest.raises(ValueError, match="not a valid option"):
            plan.figure(iris)

    def test_data_frame_key_raises_cleanly(self, iris):
        plan = BaseChartPlan(chart_type="bar", encodings={"data_frame": "species", "y": "sepal_length"})
        with pytest.raises(ValueError, match="not a valid encoding"):
            plan.figure(iris)

    def test_unknown_chart_type_raises_at_render(self, iris):
        plan = BaseChartPlan.model_construct(chart_type="banana", encodings={}, options={}, labels={}, title="")
        with pytest.raises(ValueError, match="Unknown chart_type"):
            plan.figure(iris)

    def test_code_and_code_vizro(self, iris):
        plan = BaseChartPlan(chart_type="bar", encodings={"x": "species", "y": "sepal_length"}, title="t")
        assert "px.bar(data_frame" in plan.code and "x='species'" in plan.code
        # code_vizro is a standard vizro.plotly.express chart for vm.Graph — not a @capture custom chart
        assert "import vizro.plotly.express as px" in plan.code_vizro
        assert "px.bar(data_frame" in plan.code_vizro
        assert "@capture" not in plan.code_vizro

    def test_code_is_runnable_and_equivalent(self, iris):
        """The emitted code must produce the same figure build_figure does."""
        plan = BaseChartPlan(
            chart_type="bar", encodings={"x": "species", "y": "sepal_length"}, title="t", options={"log_y": True}
        )
        namespace: dict = {}
        exec(plan.code, namespace)
        assert namespace["custom_chart"](iris) == plan.figure(iris)

    def test_code_vizro_is_runnable(self, iris):
        plan = BaseChartPlan(chart_type="bar", encodings={"x": "species", "y": "sepal_length"})
        namespace: dict = {}
        exec(plan.code_vizro, namespace)
        assert isinstance(namespace["custom_chart"](iris), go.Figure)

    def test_code_raises_for_invalid_keys_like_figure_does(self, iris):
        """figure() and code must not diverge: a plan that cannot render cannot emit code either."""
        plan = BaseChartPlan(chart_type="scatter", encodings={"x": "sepal_width"}, options={"barmode": "group"})
        with pytest.raises(ValueError, match="not a valid option"):
            _ = plan.code

    def test_code_without_any_kwargs(self):
        plan = BaseChartPlan(chart_type="scatter_matrix")
        assert "px.scatter_matrix(data_frame)" in plan.code

    def test_render_px_code_rejects_non_identifier_chart_name(self):
        plan = BaseChartPlan(chart_type="bar", encodings={"x": "species"})
        with pytest.raises(ValueError, match="identifier"):
            render_px_code(plan, chart_name="my chart")

    def test_render_px_code_custom_name_in_both_variants(self):
        plan = BaseChartPlan(chart_type="bar", encodings={"x": "species"})
        assert "def my_chart(data_frame)" in render_px_code(plan, chart_name="my_chart")
        assert "def my_chart(data_frame)" in render_px_code(plan, chart_name="my_chart", vizro=True)


class TestChartFunctions:
    def test_chart_function_returns_figure(self, iris):
        plan = BaseChartPlan(chart_type="scatter", encodings={"x": "sepal_width", "y": "sepal_length"})
        assert isinstance(plan.chart_function(iris), go.Figure)
        assert callable(plan.get_chart_function(chart_name="my_chart"))

    def test_chart_function_kwargs_are_applied(self, iris):
        """Kwargs are plotly-express overrides on top of the plan — not silently ignored."""
        plan = BaseChartPlan(chart_type="scatter", encodings={"x": "sepal_width", "y": "sepal_length"})
        fig = plan.chart_function(iris, title="Custom Title")
        assert fig.layout.title.text == "Custom Title"
        fig = plan.get_chart_function()(iris, x="petal_width")
        assert fig.layout.xaxis.title.text == "petal_width"

    def test_get_chart_function_rejects_non_identifier_name(self):
        plan = BaseChartPlan(chart_type="bar", encodings={"x": "species"})
        with pytest.raises(ValueError, match="identifier"):
            plan.get_chart_function(chart_name="my chart")

    def test_get_chart_function_sets_name(self):
        plan = BaseChartPlan(chart_type="bar", encodings={"x": "species"})
        assert plan.get_chart_function(chart_name="my_chart").__name__ == "my_chart"

    def test_vizro_chart_function_returns_vizro_themed_figure(self, iris):
        plan = BaseChartPlan(chart_type="scatter", encodings={"x": "sepal_width", "y": "sepal_length"})
        fig = plan.vizro_chart_function(iris)
        assert isinstance(fig, go.Figure)
        # vizro.plotly.express figures carry capture info, so vm.Graph and dashboard
        # code export serialize them as a plain px call instead of inlining source.
        assert hasattr(fig, "_captured_callable")

    def test_vizro_chart_function_kwargs_are_applied(self, iris):
        plan = BaseChartPlan(chart_type="scatter", encodings={"x": "sepal_width", "y": "sepal_length"})
        fig = plan.vizro_chart_function(iris, title="Vizro Chart")
        assert fig.layout.title.text == "Vizro Chart"

    def test_vizro_px_builder_without_vizro_installed(self, mocker):
        mocker.patch.dict(sys.modules, {"vizro.plotly.express": None})
        with pytest.raises(RuntimeError, match="install `vizro`"):
            _vizro_px_builder("bar")


class TestValidateAgainstData:
    def test_valid(self, iris):
        plan = BaseChartPlan(chart_type="scatter", encodings={"x": "sepal_width", "y": "sepal_length"})
        assert validate_against_data(plan, iris) == []

    def test_unknown_chart_type(self, iris):
        plan = BaseChartPlan.model_construct(chart_type="banana", encodings={}, options={}, labels={}, title="")
        assert validate_against_data(plan, iris) == [f"Unknown chart_type 'banana'. Choose one of: {CHART_TYPES}."]

    def test_missing_column(self, iris):
        plan = BaseChartPlan(chart_type="scatter", encodings={"x": "nope"})
        assert any("nope" in e for e in validate_against_data(plan, iris))

    def test_invalid_encoding_for_chart_type(self, iris):
        plan = BaseChartPlan(chart_type="pie", encodings={"names": "species", "size": "sepal_length"})
        assert any("size" in e and "valid encoding" in e for e in validate_against_data(plan, iris))

    def test_title_in_options_flagged(self, iris):
        plan = BaseChartPlan(chart_type="bar", encodings={"x": "species"}, options={"title": "A"}, title="B")
        assert any("'title' is not a valid option" in e for e in validate_against_data(plan, iris))

    def test_unknown_label_key_flagged(self, iris):
        """Plotly silently drops unmatched label keys, so a typo'd relabel must be caught here."""
        plan = BaseChartPlan(chart_type="bar", encodings={"x": "species"}, labels={"speces": "Species"})
        assert any("Label key 'speces'" in e for e in validate_against_data(plan, iris))

    def test_synthetic_label_keys_allowed(self, iris):
        plan = BaseChartPlan(chart_type="histogram", encodings={"x": "sepal_width"}, labels={"count": "Count"})
        assert validate_against_data(plan, iris) == []


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

    def test_render_failure_fails_validation(self):
        # 'size' must be non-negative, so the column checks pass but the test render fails.
        df = pd.DataFrame({"x": [1, 2, 3], "size": [-1, -2, -3]})
        model = ChartPlanFactory(data_frame=df, chart_plan=BaseChartPlan)
        with pytest.raises(ValidationError, match="could not be rendered"):
            model(chart_type="scatter", encodings={"x": "x", "y": "x", "size": "size"})

    def test_small_dataframe_supported(self):
        df = pd.DataFrame({"x": [1], "y": [2]})
        model = ChartPlanFactory(data_frame=df, chart_plan=BaseChartPlan)
        assert model(chart_type="scatter", encodings={"x": "x", "y": "y"}) is not None

    def test_validates_against_sample_without_pinning_full_frame(self):
        """The factory must hold a small sample, not the (possibly huge) source frame."""
        import gc
        import weakref

        df = pd.DataFrame({"x": range(1000), "y": range(1000)})
        ref = weakref.ref(df)
        model = ChartPlanFactory(data_frame=df, chart_plan=BaseChartPlan)
        del df
        gc.collect()
        assert ref() is None
        assert model(chart_type="scatter", encodings={"x": "x", "y": "y"}) is not None
