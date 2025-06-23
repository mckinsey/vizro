"""Controls plan model."""

import logging
from typing import Any, Optional, get_args

import pandas as pd
import vizro.models as vm
from pydantic import (
    BaseModel,
    Field,
    ValidationError,
    create_model,
    field_validator,
    model_validator,
)

from vizro_ai.dashboard._pydantic_output import _get_pydantic_model
from vizro_ai.dashboard._response_models.types import ControlType

logger = logging.getLogger(__name__)


def _create_filter_proxy(df_cols, df_schema, controllable_components) -> BaseModel:
    """Create a filter proxy model."""

    def validate_targets(v):
        """Validate the targets."""
        for target in v:
            if target not in controllable_components:
                raise ValueError(f"targets must be one of {controllable_components}")
        return v

    def validate_targets_not_empty(v):
        """Validate the targets not empty."""
        if not controllable_components:
            raise ValueError(
                """
                This might be due to the filter target is not found in the controllable components.
                returning default values.
                """
            )
        return v

    def validate_column(v):
        """Validate the column."""
        if v not in df_cols:
            raise ValueError(f"column must be one of {df_cols}")
        return v

    @model_validator(mode="before")
    @classmethod
    def validate_date_picker_column(cls, data: Any):
        """Validate the column for date picker."""
        column = data.get("column")
        selector = data.get("selector")
        if selector and hasattr(selector, "type") and selector.type == "date_picker":
            if not pd.api.types.is_datetime64_any_dtype(df_schema[column]):
                raise ValueError(
                    f"""
                    The column '{column}' is not of datetime type. Selector type 'date_picker' is
                    not allowed. Use 'dropdown' instead.
                    """
                )
        return data

    return create_model(
        "FilterProxy",
        targets=(
            list[str],
            Field(
                ...,
                description=f"""
                Target component to be affected by filter.
                Must be one of {controllable_components}. ALWAYS REQUIRED.
                """,
            ),
        ),
        column=(str, Field(..., description="Column name of DataFrame to filter. ALWAYS REQUIRED.")),
        __validators__={
            "validator1": field_validator("targets", mode="before")(validate_targets),
            "validator2": field_validator("column")(validate_column),
            "validator3": field_validator("targets", mode="before")(validate_targets_not_empty),
            "validator4": validate_date_picker_column,
        },
    )


def _create_filter(filter_prompt, model, df_cols, df_schema, controllable_components) -> vm.Filter:
    result_proxy = _create_filter_proxy(
        df_cols=df_cols, df_schema=df_schema, controllable_components=controllable_components
    )
    proxy = _get_pydantic_model(query=filter_prompt, llm_model=model, response_model=result_proxy, df_info=df_schema)
    return vm.Filter(**proxy.model_dump(exclude_unset=True))


class ControlPlan(BaseModel):
    """Control plan model."""

    control_type: ControlType = Field(
        description=f"""
        IMPORTANT:
        This field MUST be one of the following values ONLY: [{", ".join(repr(t) for t in get_args(ControlType))}].
        NO OTHER VALUES are allowed. The value must match exactly one of the options above.
        Any other value will result in a validation error.
        """,
    )
    control_description: str = Field(
        description="""
        Description of the control. Include everything that seems to relate to this control.
        Be as detailed as possible. Keep the original relevant description AS IS. If this control is used
        to control a specific component, include the relevant component details.
        """,
    )
    df_name: str = Field(
        description="""
        The name of the dataframe that the target component will use.
        If the dataframe is not used, please specify that.
        """,
    )

    def create(self, model, controllable_components, all_df_metadata) -> Optional[vm.Filter]:
        """Create the control."""
        filter_prompt = f"""
        Create a filter from the following instructions: <{self.control_description}>. Do not make up
        things that are optional and DO NOT configure actions, action triggers or action chains.
        If no options are specified, leave them out.
        """
        try:
            _df_schema = all_df_metadata.get_df_schema(self.df_name)
            _df_cols = list(_df_schema.keys())
        except KeyError:
            logger.warning(f"Dataframe {self.df_name} not found in metadata, returning default values.")
            return None

        try:
            if self.control_type == "Filter":
                res = _create_filter(
                    filter_prompt=filter_prompt,
                    model=model,
                    df_cols=_df_cols,
                    df_schema=_df_schema,
                    controllable_components=controllable_components,
                )
                return res

        except ValidationError as e:
            logger.warning(
                f"""
[FALLBACK] Build failed for `Control`, returning default values. Try rephrase the prompt or select a different model.
Error details: {e}
Relevant prompt: {self.control_description}
"""
            )
            return None
