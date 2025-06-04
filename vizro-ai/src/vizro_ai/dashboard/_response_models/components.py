"""Component plan model."""

import logging

import vizro.models as vm
from langchain_core.language_models.chat_models import BaseChatModel
from pydantic import BaseModel, Field, ValidationError
from vizro.tables import dash_ag_grid

from vizro_ai.dashboard._pydantic_output import _get_pydantic_model
from vizro_ai.dashboard._response_models.types import ComponentType
from vizro_ai.dashboard.utils import AllDfMetadata, ComponentResult
from vizro_ai.utils.helper import DebugFailure

logger = logging.getLogger(__name__)


class ComponentPlan(BaseModel):
    """Component plan model."""

    component_type: ComponentType
    component_description: str = Field(
        description="""
        Description of the component. Include everything that relates to this component.
        Be as specific and detailed as possible.
        Keep the original relevant description AS IS. Keep any links exactly as provided.
        Remember: Accuracy and completeness are key. Do not omit any relevant information provided about the component.
        """,
    )
    component_id: str = Field(
        pattern=r"^[a-z0-9]+(_[a-z0-9]+)*$", description="Small snake case description of this component."
    )
    df_name: str = Field(
        description="""
        The name of the dataframe that this component will use. If no dataframe is
        used, please specify that as N/A.
        """,
    )

    def create(self, model: BaseChatModel, all_df_metadata: AllDfMetadata) -> ComponentResult:
        """Create the component based on its type.

        Args:
            model: The llm used.
            all_df_metadata: Metadata for all available dataframes.

        Returns:
            ComponentResult containing:
            - component: The created component (vm.Card, vm.AgGrid, or vm.Graph)
            - code: Optional string containing the code used to generate the component (for Graph type only)

        """
        try:
            if self.component_type == "Graph":
                from vizro_ai import VizroAI

                vizro_ai = VizroAI(model=model)
                result = vizro_ai.plot(
                    df=all_df_metadata.get_df(self.df_name),
                    user_input=self.component_description,
                    max_debug_retry=2,  # TODO must be flexible
                    return_elements=True,
                    _minimal_output=True,
                )
                return ComponentResult(
                    component=vm.Graph(
                        id=self.component_id,
                        figure=result.get_fig_object(chart_name=self.component_id, data_frame=self.df_name, vizro=True),
                    ),
                    imports=result._get_imports(vizro=True),
                    code=result._get_chart_code(chart_name=self.component_id, vizro=True),
                )
            elif self.component_type == "AgGrid":
                return ComponentResult(
                    component=vm.AgGrid(id=self.component_id, figure=dash_ag_grid(data_frame=self.df_name))
                )
            elif self.component_type == "Card":
                card_prompt = f"""
                The Card uses the dcc.Markdown component from Dash as its underlying text component.
                Create a card based on the card description: {self.component_description}.
                """
                result_proxy = _get_pydantic_model(query=card_prompt, llm_model=model, response_model=vm.Card)
                proxy_dict = result_proxy.model_dump()
                proxy_dict["id"] = self.component_id
                return ComponentResult(component=vm.Card(**proxy_dict))

        except (DebugFailure, ValidationError) as e:
            logger.warning(
                f"""
[FALLBACK] Failed to build `Component`: {self.component_id}.
Reason: {e}
Relevant prompt: {self.component_description}
"""
            )
            return ComponentResult(
                component=vm.Card(id=self.component_id, text=f"Failed to build component: {self.component_id}")
            )
