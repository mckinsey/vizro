"""Controls plan model."""

import logging
from typing import Any, Dict, List, Optional, Type

import pandas as pd
import vizro.models as vm

try:
    from pydantic.v1 import BaseModel, Field, ValidationError, create_model, root_validator, validator
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, Field, ValidationError, create_model, root_validator, validator
from vizro_ai.dashboard._pydantic_output import _get_pydantic_model
from vizro_ai.dashboard._response_models.types import ControlType

logger = logging.getLogger(__name__)


class FilterProxyModel:
    """Filter proxy model."""

    @classmethod
    def _create_model(
        cls, df_cols: List[str], df_schema: Dict[str, Any], controllable_components: List[str]
    ) -> Type[BaseModel]:
        def validate_targets(v):
            if v not in controllable_components:
                raise ValueError(f"targets must be one of {controllable_components}")
            return v

        def validate_targets_not_empty(v):
            if not controllable_components:
                raise ValueError(
                    """
                    This might be due to the filter target is not found in the controllable components.
                    returning default values.
                    """
                )
            return v

        def validate_column(v):
            if v not in df_cols:
                raise ValueError(f"column must be one of {df_cols}")
            return v

        @root_validator(allow_reuse=True)
        def validate_date_picker_column(cls, values):
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
                List[str],
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
    FilterProxy = FilterProxyModel._create_model(
        df_cols=df_cols, df_schema=df_schema, controllable_components=controllable_components
    )
    proxy = _get_pydantic_model(query=filter_prompt, llm_model=model, response_model=FilterProxy, df_info=df_schema)
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
    # instead of requesting the df_name, we should request the target component name
    # replace df_name with target_component_name, then later retrieve the df_name from the controllable components.
    # This logic is more aligned with the Vizro usage pattern.
    target_components_id: List[str] = Field(
        ...,
        description="""
        The id of the target components that this control will affect.
        """,
    )

    def create(self, model, controllable_components, all_df_metadata, components_plan) -> Optional[vm.Filter]:
        """Create the control."""
        filter_prompt = f"""
        Create a filter from the following instructions: <{self.control_description}>. Do not make up
        things that are optional and DO NOT configure actions, action triggers or action chains.
        If no options are specified, leave them out.
        """

        df_name_collection = []
        for component_plan in components_plan:
            if component_plan.component_id in set(self.target_components_id) & set(controllable_components):
                name = component_plan.df_name
            else:
                continue

            if name not in df_name_collection:
                df_name_collection.append(name)
        if len(df_name_collection) > 1:
            logger.warning(
                f"""
[FALLBACK] Multiple dataframes found in the target components: {df_name_collection}.
Choose one dataframe to build the filter.
"""
            )
        df_name = df_name_collection[0] if df_name_collection else None

        try:
            _df_schema = all_df_metadata.get_df_schema(df_name)
            _df_cols = list(_df_schema.keys())
        except KeyError:
            logger.warning(f"Dataframe {df_name} not found in metadata, returning default values.")
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
    from vizro.tables import dash_ag_grid
    from vizro_ai._llm_models import _get_llm_model
    from vizro_ai.dashboard._response_models.components import ComponentPlan
    from vizro_ai.dashboard.utils import AllDfMetadata, DfMetadata

    load_dotenv()

    model = _get_llm_model()

    all_df_metadata = AllDfMetadata({})
    all_df_metadata.all_df_metadata["world_gdp"] = DfMetadata(
        df_schema={"a": "int64", "b": "int64"},
        df=pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": [4, 5, 6, 7, 8]}),
        df_sample=pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": [4, 5, 6, 7, 8]}),
    )
    components_plan = [
        ComponentPlan(
            component_type="AgGrid",
            component_description="Create a table that shows GDP data.",
            component_id="gdp_table",
            df_name="world_gdp",
        )
    ]
    vm.AgGrid(id="gdp_table", figure=dash_ag_grid(data_frame="world_gdp"))
    control_plan = ControlPlan(
        control_type="Filter",
        control_description="Create a filter that filters the data by column 'a'.",
        target_components_id=["gdp_table"],
    )
    control = control_plan.create(
        model,
        ["gdp_table"],
        all_df_metadata,
        components_plan,
    )
    print(control.__repr__())  # noqa: T201
