import pytest
import vizro.models as vm
from vizro.managers import model_manager
from vizro.models import VizroBaseModel
from vizro_ai.dashboard._response_models.controls import ControlPlan, _create_filter, _create_filter_proxy

try:
    from pydantic.v1 import ValidationError
except ImportError:  # pragma: no cov
    from pydantic import ValidationError

# Needed for testing control creation.
model_manager.__setitem__("bar_chart", VizroBaseModel)


class TestFilterProxyCreate:
    """Tests filter proxy creation."""

    def test_create_filter_proxy_validate_targets(self, df_cols, df_schema, controllable_components):
        filter_proxy = _create_filter_proxy(df_cols, df_schema, controllable_components)
        with pytest.raises(ValidationError, match="targets must be one of"):
            filter_proxy(targets=["population_chart"], column="a")

    def test_create_filter_proxy_validate_targets_not_empty(self, df_cols, df_schema, controllable_components):
        filter_proxy = _create_filter_proxy(df_cols=df_cols, df_schema=df_schema, controllable_components=[])
        with pytest.raises(ValidationError):
            filter_proxy(targets=[], column="a")

    def test_create_filter_proxy_validate_columns(self, df_cols, df_schema, controllable_components):
        filter_proxy = _create_filter_proxy(df_cols, df_schema, controllable_components)
        with pytest.raises(ValidationError, match="column must be one of"):
            filter_proxy(targets=["bar_chart"], column="x")

    def test_create_filter_proxy(self, df_cols, df_schema, controllable_components):
        filter_proxy = _create_filter_proxy(df_cols, df_schema, controllable_components)
        actual_filter = filter_proxy(targets=["bar_chart"], column="a")

        assert actual_filter.dict(exclude={"id": True}) == vm.Filter(targets=["bar_chart"], column="a").dict(
            exclude={"id": True}
        )


class TestControlPlan:
    """Test control plan."""

    def test_control_plan_invalid_df_name(self, fake_llm_filter, df_metadata):
        control_plan = ControlPlan(
            control_type="Filter",
            control_description="Create a filter that filters the data based on the column 'a'.",
            df_name="population_chart",
        )
        default_control = control_plan.create(
            model=fake_llm_filter, controllable_components=["bar_chart"], all_df_metadata=df_metadata
        )
        assert default_control is None

    def test_control_plan_invalid_type(self, fake_llm_filter, df_metadata):
        with pytest.raises(ValidationError):
            ControlPlan(
                control_type="parameter",
                control_description="Create a parameter that targets the data based on the column 'a'.",
                df_name="bar_chart",
            )


def test_create_filter(filter_prompt, fake_llm_filter, df_cols, df_schema, controllable_components):
    actual_filter = _create_filter(
        filter_prompt=filter_prompt,
        model=fake_llm_filter,
        df_cols=df_cols,
        df_schema=df_schema,
        controllable_components=controllable_components,
    )
    assert actual_filter.dict(exclude={"id": True}) == vm.Filter(targets=["bar_chart"], column="a").dict(
        exclude={"id": True}
    )