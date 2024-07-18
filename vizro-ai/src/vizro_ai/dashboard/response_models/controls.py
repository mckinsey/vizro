"""Controls plan model."""

import logging
from typing import List

import vizro.models as vm

try:
    from pydantic.v1 import BaseModel, Field, ValidationError, create_model, validator
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, Field, ValidationError, create_model, validator
from vizro_ai.dashboard._pydantic_output import _get_pydantic_output

from .types import control_type

logger = logging.getLogger(__name__)


def _create_filter_proxy(df_cols, available_components) -> BaseModel:
    """Create a filter proxy model."""

    def validate_targets(v):
        """Validate the targets."""
        if v not in available_components:
            raise ValueError(f"targets must be one of {available_components}")
        return v

    def validate_column(v):
        """Validate the column."""
        if v not in df_cols:
            raise ValueError(f"column must be one of {df_cols}")
        return v

    # TODO: properly check this - e.g. what is the best way to ideally dynamically include the available components
    # even in the schema
    return create_model(
        "FilterProxy",
        targets=(
            List[str],
            Field(
                ...,
                description="Target component to be affected by filter. "
                f"Must be one of {available_components}. ALWAYS REQUIRED.",
            ),
        ),
        column=(str, Field(..., description="Column name of DataFrame to filter. ALWAYS REQUIRED.")),
        __validators__={
            "validator1": validator("targets", pre=True, each_item=True, allow_reuse=True)(validate_targets),
            "validator2": validator("column", allow_reuse=True)(validate_column),
        },
        __base__=vm.Filter,
    )


def _create_filter(filter_prompt, model, df_cols, df_schema, available_components):
    result_proxy = _create_filter_proxy(df_cols=df_cols, available_components=available_components)
    proxy = _get_pydantic_output(query=filter_prompt, llm_model=model, response_model=result_proxy, df_info=df_schema)
    return vm.Filter.parse_obj(
        proxy.dict(exclude={"selector": {"id": True, "actions": True, "_add_key": True}, "id": True, "type": True})
    )


class ControlPlan(BaseModel):
    """Control plan model."""

    control_type: control_type
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

    # TODO: there is definitely room for dynamic model creation, e.g. with literals for targets
    def create(self, model, available_components, df_metadata):
        """Create the control."""
        filter_prompt = (
            f"Create a filter from the following instructions: {self.control_description}. Do not make up "
            f"things that are optional and DO NOT configure actions, action triggers or action chains."
            f" If no options are specified, leave them out."
        )
        try:
            _df_schema = df_metadata.get_df_schema(self.df_name)
            _df_cols = list(_df_schema.keys())
        # when wrong dataframe name is given
        except KeyError:
            logger.warning(f"Dataframe {self.df_name} not found in metadata, returning default values.")
            return None

        try:
            if self.control_type == "Filter":
                return _create_filter(
                    filter_prompt=filter_prompt,
                    model=model,
                    df_cols=_df_cols,
                    df_schema=_df_schema,
                    available_components=available_components,
                )
            else:
                logger.warning(f"Control type {self.control_type} not recognized.")
                return None

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
        control_description="Create a filter that filters the data based on the column 'a'.",
        df_name="gdp_chart",
    )
    control = control_plan.create(model, ["gdp_chart"], df_metadata)
