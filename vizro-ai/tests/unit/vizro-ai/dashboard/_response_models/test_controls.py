import pytest
from vizro_ai.dashboard._response_models.controls import ControlPlan, _create_filter_proxy

try:
    from pydantic.v1 import ValidationError
except ImportError:  # pragma: no cov
    from pydantic import ValidationError


class TestControlCreate:
    """Tests control creation."""

    def test_create_filter_proxy_validate_targets(self, df_cols, df_schema, controllable_components):
        actual = _create_filter_proxy(df_cols, df_schema, controllable_components)
        with pytest.raises(ValidationError, match="targets must be one of"):
            actual(targets=["population_chart"], column="gdp")

    def test_create_filter_proxy_validate_targets_not_empty(self, df_cols, df_schema, controllable_components):
        actual = _create_filter_proxy(df_cols=df_cols, df_schema=df_schema, controllable_components=[])
        with pytest.raises(ValidationError):
            actual(targets=[], column="gdp")

    def test_create_filter_proxy_validate_columns(self, df_cols, df_schema, controllable_components):
        actual = _create_filter_proxy(df_cols, df_schema, controllable_components)
        with pytest.raises(ValidationError, match="column must be one of"):
            actual(targets=["gdp_chart"], column="x")


class TestControlPlan:
    """Test control plan."""

    def test_control_plan_invalid_df_name(self, fake_llm_filter, df_metadata):
        control_plan = ControlPlan(
            control_type="Filter",
            control_description="Create a filter that filters the data based on the column 'a'.",
            df_name="population_chart",
        )
        default_control = control_plan.create(
            model=fake_llm_filter, controllable_components=["gdp_chart"], all_df_metadata=df_metadata
        )
        assert default_control is None

    def test_control_plan_invalid_type(self, fake_llm_filter, df_metadata):
        with pytest.raises(ValidationError):
            ControlPlan(
                control_type="parameter",
                control_description="Create a parameter that targets the data based on the column 'a'.",
                df_name="gdp_chart",
            )
