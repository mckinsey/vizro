"""Module containing the planner functionality."""

import logging
from typing import Dict, List, Literal, Union

import vizro.models as vm
from langchain_openai import ChatOpenAI
from vizro.models.types import ComponentType

try:
    from pydantic.v1 import BaseModel, Field, ValidationError, create_model, validator
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, Field, ValidationError, create_model, validator
import numpy as np
from vizro.models._layout import _get_grid_lines, _get_unique_grid_component_ids, _validate_grid_areas
from vizro.tables import dash_ag_grid
from vizro_ai.dashboard.nodes._model import _get_proxy_model

logger = logging.getLogger(__name__)

# For unsupported component and control types, how to handle them?
# option 1. Ignore silently
# option 2. Raise a warning and add the warning message into langgraph state. This gives the user transparency on why
#    a certain component or control was not created.
# option 3. Raise a warning and suggest additional reference material
component_type = Literal[
    "AgGrid", "Card", "Graph"
]  # Complete list: ["AgGrid", "Button", "Card", "Container", "Graph", "Table", "Tabs"]
control_type = Literal["Filter"]  # Complete list: ["Filter", "Parameter"]

# For other models, like ["Accordion", "NavBar"], how to handle them?


class Component(BaseModel):
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
    data_frame: str = Field(
        ...,
        description="The name of the dataframe that this component will use. If the dataframe is "
        "not used, please specify that.",
    )

    def create(self, model, df_metadata) -> Union[ComponentType, None]:
        """Create the component."""
        from vizro_ai import VizroAI

        vizro_ai = VizroAI(model=model)

        if self.component_type == "Graph":
            return vm.Graph(
                id=self.component_id + "_" + self.page_id,
                figure=vizro_ai.plot(df=df_metadata[self.data_frame]["df"], user_input=self.component_description),
            )
        elif self.component_type == "AgGrid":
            return vm.AgGrid(id=self.component_id + "_" + self.page_id, figure=dash_ag_grid(data_frame=self.data_frame))
        elif self.component_type == "Card":
            return _get_proxy_model(
                query=self.component_description, llm_model=model, result_model=vm.Card, df_metadata=df_metadata
            )


# TODO: This is a very basic implementation of the filter proxy model. It needs to be improved.
# TODO: Try use `df_sample` to inform pydantic models like `OptionsType` about available choices.
# Caution: If just use `df_sample` to inform the pydantic model, the choices might not be exhaustive.
def create_filter_proxy(df_cols, df, available_components) -> BaseModel:
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


class Control(BaseModel):
    """Control plan model."""

    control_type: control_type
    control_description: str = Field(
        ...,
        description="Description of the control. Include everything that seems to relate to this control."
        "Be as detailed as possible. Keep the original relevant description AS IS. If this control is used"
        "to control a specific component, include the relevant component details.",
    )
    data_frame: str = Field(
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
            _df_schema, _df = (
                df_metadata[self.data_frame]["df_schema"],
                df_metadata[self.data_frame]["df"],
            )
            _df_cols = list(_df_schema.keys())
        # when wrong dataframe name is given
        except KeyError:
            logger.info(f"Dataframe {self.data_frame} not found in metadata, returning default values.")
            return None

        try:
            result_proxy = create_filter_proxy(df_cols=_df_cols, df=_df, available_components=available_components)
            proxy = _get_proxy_model(
                query=filter_prompt, llm_model=model, result_model=result_proxy, df_metadata=df_metadata
            )
            logger.info(
                f"`Control` proxy: {proxy.dict()}"
            )  # when wrong column name is given, `AttributeError: 'ValidationError' object has no attribute 'dict'``
            actual = vm.Filter.parse_obj(
                proxy.dict(
                    exclude={"selector": {"id": True, "actions": True, "_add_key": True}, "id": True, "type": True}
                )
            )
            # del model_manager._ModelManager__models[proxy.id]  # TODO: This is very wrong and needs to change

        except ValidationError as e:
            logger.info(f"Build failed for `Control`, returning default values. Error details: {e}")
            return None

        return actual


class LayoutProxyModel(BaseModel):
    """Proxy model for Layout."""

    grid: List[List[int]] = Field(..., description="Grid specification to arrange components on screen.")

    @validator("grid")
    def validate_grid(cls, grid):
        """Validate the grid."""
        if len({len(row) for row in grid}) > 1:
            raise ValueError("All rows must be of same length.")

        # Validate grid type and values
        unique_grid_idx = _get_unique_grid_component_ids(grid)
        if 0 not in unique_grid_idx or not np.array_equal(unique_grid_idx, np.arange((unique_grid_idx.max() + 1))):
            raise ValueError("Grid must contain consecutive integers starting from 0.")

        # Validates grid areas spanned by components and spaces
        component_grid_lines, space_grid_lines = _get_grid_lines(grid)
        _validate_grid_areas(component_grid_lines + space_grid_lines)
        return grid


class Layout(BaseModel):
    """Layout plan model."""

    layout_description: str = Field(
        ...,
        description="Description of the layout. Include everything that seems to relate"
        " to this layout AS IS. If layout not specified, describe layout as `N/A`.",
    )

    def create(self, model, df_metadata) -> Union[vm.Layout, None]:
        """Create the layout."""
        if self.layout_description == "N/A":
            return None

        try:
            proxy = _get_proxy_model(
                query=self.layout_description, llm_model=model, result_model=LayoutProxyModel, df_metadata=df_metadata
            )
            actual = vm.Layout.parse_obj(proxy.dict(exclude={}))
        except (ValidationError, AttributeError) as e:
            logger.info(f"Build failed for `Layout`, returning default values. Error details: {e}")
            actual = None

        return actual


class PagePlanner(BaseModel):
    """Page plan model."""

    title: str = Field(
        ...,
        description="Title of the page. If no description is provided, "
        "make a short and concise title from the components.",
    )
    components: List[Component]
    controls: List[Control] = Field([], description="Controls of the page.")
    layout: Layout = Field(None, description="Layout of the page.")


class DashboardPlanner(BaseModel):
    """Dashboard plan model."""

    title: str = Field(
        ...,
        description="Title of the dashboard. If no description is provided,"
        " make a short and concise title from the content of the pages.",
    )
    pages: List[PagePlanner]


def _get_dashboard_plan(
    query: str,
    model: Union[ChatOpenAI],
    df_metadata: Dict[str, Dict[str, str]],
) -> DashboardPlanner:
    return _get_proxy_model(query=query, llm_model=model, result_model=DashboardPlanner, df_metadata=df_metadata)


if __name__ == "__main__":
    import pandas as pd
    from vizro.managers import model_manager
    from vizro_ai.chains._llm_models import _get_llm_model

    model_default = "gpt-3.5-turbo"

    llm_model = _get_llm_model(model=model_default)
    # # Test the layout planner
    # layout1 = Layout(layout_description="grid=[[0,1]]")
    # print(layout1.create(model=llm_model, df_metadata={}))
    # # grid=[[0, 1]]

    # layout1 = Layout(layout_description="The card has text `This is a card`")
    # print(layout1.create(model=llm_model, df_metadata={}))
    # # None

    # Test the control planner
    control1 = Control(
        control_type="Filter",
        control_description="This filter allows users to filter the first table by continent."
        " It applies only to the table displaying worldwide population and GDP data.",
        data_frame="world_indicators",
    )
    model_manager["world_population_gdp_table"] = vm.AgGrid(figure=dash_ag_grid(data_frame="world_indicators"))

    print(  # noqa: T201
        control1.create(
            model=llm_model,
            available_components=["world_population_gdp_table", "stock_price_table"],
            df_metadata={
                "world_indicators": {
                    "df_schema": {
                        "country": "object",
                        "continent": "object",
                        "year": "int64",
                        "lifeExp": "float64",
                        "pop": "int64",
                        "gdpPercap": "float64",
                        "iso_alpha": "object",
                        "iso_num": "int64",
                    },
                    "df": pd.DataFrame(
                        {
                            "country": ["Afghanistan", "Albania", "Algeria", "Angola", "Argentina"],
                            "continent": ["Asia", "Europe", "Africa", "Africa", "Americas"],
                            "year": [1952, 1957, 1962, 1967, 1972],
                            "lifeExp": [28.801, 76.423, 43.077, 30.015, 62.485],
                            "pop": [8425333, 1282697, 9279525, 4232095, 2227000],
                            "gdpPercap": [779.445314, 1601.056136, 2449.008185, 3520.610273, 8955.553783],
                            "iso_alpha": ["AFG", "ALB", "DZA", "AGO", "ARG"],
                            "iso_num": [4, 8, 12, 24, 32],
                        }
                    ),
                }
            },
        )
    )
