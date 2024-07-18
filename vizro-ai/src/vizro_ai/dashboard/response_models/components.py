"""Component plan model."""

import logging
from typing import Union

import vizro.models as vm
from vizro.models.types import ComponentType

try:
    from pydantic.v1 import BaseModel, Field
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, Field
from vizro.tables import dash_ag_grid
from vizro_ai.dashboard._constants import component_type
from vizro_ai.dashboard._pydantic_output import _get_pydantic_output
from vizro_ai.utils.helper import DebugFailure

logger = logging.getLogger(__name__)


class ComponentPlan(BaseModel):
    """Component plan model."""

    component_type: component_type
    component_description: str = Field(
        ...,
        description="Description of the component. Include everything that relates to this component. "
        "Be as detailed as possible."
        "Keep the original relevant description AS IS. Keep any links as original links.",
    )
    component_id: str = Field(
        pattern=r"^[a-z]+(_[a-z]+)?$", description="Small snake case description of this component."
    )
    page_id: str = Field(..., description="The page id where this component will be placed.")
    df_name: str = Field(
        ...,
        description="The name of the dataframe that this component will use. If no dataframe is "
        "used, please specify that as N/A.",
    )

    def create(self, model, df_metadata) -> ComponentType:
        """Create the component."""
        from vizro_ai import VizroAI

        vizro_ai = VizroAI(model=model)

        try:
            if self.component_type == "Graph":
                return vm.Graph(
                    id=self.component_id + "_" + self.page_id,
                    figure=vizro_ai.plot(df=df_metadata.get_df(self.df_name), user_input=self.component_description),
                )
            elif self.component_type == "AgGrid":
                return vm.AgGrid(id=self.component_id + "_" + self.page_id, figure=dash_ag_grid(data_frame=self.df_name))
            elif self.component_type == "Card":
                return _get_pydantic_output(query=self.component_description, llm_model=model, result_model=vm.Card)
        except DebugFailure as e:
            logger.warning(
                f"Failed to build component: {self.component_id}.\n ------- \n "
                f"Reason: {e} \n ------- \n Relevant prompt: `{self.component_description}`")
            return vm.Card(id=self.component_id, text=f"Failed to build component: {self.component_id}")
