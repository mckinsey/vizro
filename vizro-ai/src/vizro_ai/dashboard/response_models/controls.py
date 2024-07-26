"""Controls plan model."""

import logging
from typing import List, Union

import vizro.models as vm

try:
    from pydantic.v1 import BaseModel, Field, ValidationError, create_model, validator
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, Field, ValidationError, create_model, validator
from vizro_ai.dashboard._pydantic_output import _get_pydantic_output
from vizro_ai.dashboard.response_models.types import CtrlType

logger = logging.getLogger(__name__)


def _create_filter_proxy(df_cols, controllable_components) -> BaseModel:
    """Create a filter proxy model."""

    def validate_targets(v):
        """Validate the targets."""
        if v not in controllable_components:
            raise ValueError(f"targets must be one of {controllable_components}")
        return v

    def validate_targets_not_empty(v):
        """Validate the targets not empty."""
        if controllable_components == []:
            raise ValueError(
                "This might be due to the filter target is not found in the controllable components. "
                "returning default values."
            )
        return v

    def validate_column(v):
        """Validate the column."""
        if v not in df_cols:
            raise ValueError(f"column must be one of {df_cols}")
        return v

    return create_model(
        "FilterProxy",
        targets=(
            List[str],
            Field(
                ...,
                description="Target component to be affected by filter. "
                f"Must be one of {controllable_components}. ALWAYS REQUIRED.",
            ),
        ),
        column=(str, Field(..., description="Column name of DataFrame to filter. ALWAYS REQUIRED.")),
        __validators__={
            "validator1": validator("targets", pre=True, each_item=True, allow_reuse=True)(validate_targets),
            "validator2": validator("column", allow_reuse=True)(validate_column),
            "validator3": validator("targets", pre=True, allow_reuse=True)(validate_targets_not_empty),
        },
        __base__=vm.Filter,
    )


def _create_filter(filter_prompt, model, df_cols, df_schema, controllable_components) -> vm.Filter:
    result_proxy = _create_filter_proxy(df_cols=df_cols, controllable_components=controllable_components)
    proxy = _get_pydantic_output(query=filter_prompt, llm_model=model, response_model=result_proxy, df_info=df_schema)
    return vm.Filter.parse_obj(
        proxy.dict(exclude={"selector": {"id": True, "actions": True, "_add_key": True}, "id": True, "type": True})
    )


class ControlPlan(BaseModel):
    """Control plan model."""

    control_type: CtrlType
    control_description: str = Field(
        ...,
        description="Description of the control. Include everything that seems to relate to this control."
        "Be as detailed as possible. Keep the original relevant description AS IS. If this control is used"
        "to control a specific component, include the relevant component details.",
    )
    df_name: str = Field(
        ...,
        description="The name of the dataframe that this component will use. "
        "If the dataframe is not used, please specify that.",
    )

    def create(self, model, controllable_components, df_metadata) -> Union[vm.Filter, None]:
        """Create the control."""
        filter_prompt = (
            f"Create a filter from the following instructions: <{self.control_description}>. Do not make up "
            f"things that are optional and DO NOT configure actions, action triggers or action chains."
            f" If no options are specified, leave them out."
        )
        try:
            _df_schema = df_metadata.get_df_schema(self.df_name)
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
                f"Build failed for `Control`, returning default values. Try rephrase the prompt or "
                f"select a different model. \n ------- \n Error details: {e} \n ------- \n "
                f"Relevant prompt: `{self.control_description}`"
            )
            return None


if __name__ == "__main__":
    import pandas as pd
    from vizro_ai.chains._llm_models import _get_llm_model
    from vizro_ai.dashboard.utils import DfMetadata, MetadataContent

    model = _get_llm_model()

    df_metadata = DfMetadata({})
    df_metadata.metadata["gdp_chart"] = MetadataContent(
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
        model, ["gdp_chart"], df_metadata
    )  # error: Target gdp_chart not found in model_manager.
