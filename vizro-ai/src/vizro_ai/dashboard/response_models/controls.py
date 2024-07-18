"""Controls plan model."""

import logging
from typing import List

import vizro.models as vm

try:
    from pydantic.v1 import BaseModel, Field, ValidationError, create_model, validator
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, Field, ValidationError, create_model, validator
from vizro_ai.dashboard._constants import control_type
from vizro_ai.dashboard._pydantic_output import _get_pydantic_output

logger = logging.getLogger(__name__)


def create_filter_proxy(df_cols, available_components) -> BaseModel:
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
            logger.info(f"Dataframe {self.df_name} not found in metadata, returning default values.")
            return None

        try:
            result_proxy = create_filter_proxy(df_cols=_df_cols, available_components=available_components)
            proxy = _get_pydantic_output(
                query=filter_prompt, llm_model=model, result_model=result_proxy, df_info=_df_schema
            )
            logger.info(
                f"`Control` proxy: {proxy.dict()}"
            )  # when wrong column name is given, `AttributeError: 'ValidationError' object has no attribute 'dict'``
            actual = vm.Filter.parse_obj(
                proxy.dict(
                    exclude={"selector": {"id": True, "actions": True, "_add_key": True}, "id": True, "type": True}
                )
            )

        except ValidationError as e:
            logger.warning(
                f"Build failed for `Control`, returning default values. Try rephrase the prompt or "
                f"select a different model. \n ------- \n Error details: {e} \n ------- \n "
                f"Relevant prompt: `{self.control_description}`"
            )
            return None

        return actual
