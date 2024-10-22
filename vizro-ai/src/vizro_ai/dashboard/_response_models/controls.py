"""Controls plan model."""

import logging
from typing import Optional

import pandas as pd
import vizro.models as vm

try:
    from pydantic.v1 import BaseModel, Field, ValidationError, create_model, root_validator, validator
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, Field, ValidationError, create_model, root_validator, validator
from vizro_ai.dashboard._pydantic_output import _get_pydantic_model
from vizro_ai.dashboard._response_models.types import ControlType

logger = logging.getLogger(__name__)


def _create_filter_proxy(df_cols, df_schema, controllable_components) -> BaseModel:
    """Create a filter proxy model."""

    def validate_targets(v):
        """Validate the targets."""
        if v not in controllable_components:
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

    @root_validator(allow_reuse=True)
    def validate_date_picker_column(cls, values):
        """Validate the column for date picker."""
        column = values.get("column")
        selector = values.get("selector")
        if selector and selector.type == "date_picker":
            if not pd.api.types.is_datetime64_any_dtype(df_schema[column]):
                raise ValueError(
                    f"""
                    The column '{column}' is not of datetime type. Selector type 'date_picker' is
                    not allowed. Use 'dropdown' instead.
                    """
                )
        return values

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
            "validator1": validator("targets", pre=True, each_item=True, allow_reuse=True)(validate_targets),
            "validator2": validator("column", allow_reuse=True)(validate_column),
            "validator3": validator("targets", pre=True, allow_reuse=True)(validate_targets_not_empty),
            "validator4": validate_date_picker_column,
        },
        __base__=vm.Filter,
    )


def _create_filter(filter_prompt, model, df_cols, df_schema, controllable_components) -> vm.Filter:
    result_proxy = _create_filter_proxy(
        df_cols=df_cols, df_schema=df_schema, controllable_components=controllable_components
    )
    proxy = _get_pydantic_model(query=filter_prompt, llm_model=model, response_model=result_proxy, df_info=df_schema)
    return vm.Filter.parse_obj(proxy.dict(exclude_unset=True))


class ControlPlan(BaseModel):
    """Control plan model."""

    control_type: ControlType
    control_description: str = Field(
        ...,
        description="""
        Description of the control. Include everything that seems to relate to this control.
        Be as detailed as possible. Keep the original relevant description AS IS. If this control is used
        to control a specific component, include the relevant component details.
        """,
    )
    df_name: str = Field(
        ...,
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


if __name__ == "__main__":
    import pandas as pd
    from dotenv import load_dotenv

    from vizro_ai._llm_models import _get_llm_model
    from vizro_ai.dashboard.utils import AllDfMetadata, DfMetadata

    load_dotenv()

    model = _get_llm_model()

    all_df_metadata = AllDfMetadata({})
    all_df_metadata.all_df_metadata["gdp_chart"] = DfMetadata(
        df_schema={"a": "int64", "b": "int64"},
        df=pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": [4, 5, 6, 7, 8]}),
        df_sample=pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": [4, 5, 6, 7, 8]}),
    )
    control_plan = ControlPlan(
        control_type="Filter",
        control_description="Create a filter that filters the data by column 'a'.",
        df_name="gdp_chart",
    )
    control = control_plan.create(
        model, ["gdp_chart"], all_df_metadata
    )  # error: Target gdp_chart not found in model_manager.
