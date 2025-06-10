import logging

import pytest
import vizro.models as vm
from pydantic import ValidationError
from vizro.managers import model_manager
from vizro.models import VizroBaseModel

from vizro_ai.dashboard._response_models.controls import ControlPlan, _create_filter_proxy

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

    def test_create_filter_proxy(self, df_cols, df_schema, controllable_components, expected_filter):
        filter_proxy = _create_filter_proxy(df_cols, df_schema, controllable_components)
        result = filter_proxy(targets=["bar_chart"], column="a")

        assert result.model_dump(exclude={"id": True}) == expected_filter.model_dump(
            exclude={"id": True, "selector": True, "type": True}
        )


class TestControlCreate:
    """Test control creation."""

    def test_control_create_valid(self, fake_llm_filter, controllable_components, df_metadata):
        control_plan = ControlPlan(
            control_type="Filter",
            control_description="Create a parameter that targets the data based on the column 'a'.",
            df_name="bar_chart",
        )
        result = control_plan.create(
            model=fake_llm_filter, controllable_components=controllable_components, all_df_metadata=df_metadata
        )
        assert result.model_dump(exclude={"id": True}) == vm.Filter(targets=["bar_chart"], column="a").model_dump(
            exclude={"id": True}
        )

    def test_control_create_invalid_df_name(
        self, fake_llm_filter, df_metadata, caplog
    ):  # testing the fallback when an invalid dataframe name is provided to ControlPlan.
        with caplog.at_level(logging.WARNING):
            control_plan = ControlPlan(
                control_type="Filter",
                control_description="Create a parameter that targets the data based on the column 'a'.",
                df_name="line_chart",
            )
            result = control_plan.create(
                model=fake_llm_filter, controllable_components=["bar_chart"], all_df_metadata=df_metadata
            )

        assert result is None
        assert "Dataframe line_chart not found in metadata, returning default values." in caplog.text

    def test_control_create_invalid_control_type(
        self, fake_llm_filter, df_metadata, caplog
    ):  # testing the fallback when an invalid dataframe name is provided to ControlPlan.
        with pytest.raises(ValidationError):
            with caplog.at_level(logging.WARNING):
                control_plan = ControlPlan(
                    control_type="Parameter",
                    control_description="Create a parameter that targets the data based on the column 'a'.",
                    df_name="bar_chart",
                )
                result = control_plan.create(
                    model=fake_llm_filter, controllable_components=["bar_chart"], all_df_metadata=df_metadata
                )

                assert result is None
                assert "Build failed for `Control`, returning default values." in caplog.text
