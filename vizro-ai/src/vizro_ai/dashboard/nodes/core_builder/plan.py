"""Module containing the planner functionality."""

import logging
from typing import Dict, List, Literal, Union

import vizro.models as vm
from langchain_openai import ChatOpenAI

try:
    from pydantic.v1 import BaseModel, Field, ValidationError
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, Field, ValidationError
import numpy as np
from pydantic.v1 import Field, create_model, validator
from vizro.models._layout import _get_grid_lines, _get_unique_grid_component_ids, _validate_grid_areas
from vizro.tables import dash_ag_grid
from vizro_ai.dashboard.nodes.core_builder.model import _get_model

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

component_type = Literal["AgGrid", "Card", "Graph"]
control_type = Literal["Filter"]


class CardProxyModel(BaseModel):
    """Proxy model for Card."""

    type: Literal["card"] = "card"
    text: str = Field(
        ..., description="Markdown string to create card title/text that should adhere to the CommonMark Spec."
    )
    href: str = Field(
        "",
        description="URL (relative or absolute) to navigate to. If not provided the Card serves as a text card only.",
    )


class Component(BaseModel):
    """Component plan model."""

    component_type: component_type
    component_description: str = Field(
        ...,
        description="Description of the component. Include everything that relates to this component. "
        "Be as detailed as possible."
        "Keep the original relavant description AS IS. Keep any links as original links.",
    )
    component_id: str = Field(
        pattern=r"^[a-z]+(_[a-z]+)?$", description="Small snake case description of this component"
    )
    data_frame: str = Field(
        ...,
        description="The name of the dataframe that this component will use. If the dataframe is "
        "not used, please specify that.",
    )

    def create(self, model, df_metadata):
        """Create the component."""
        if self.component_type == "Graph":
            return vm.Graph()
        elif self.component_type == "AgGrid":
            return vm.AgGrid(id=self.component_id, figure=dash_ag_grid(data_frame=self.data_frame))
        elif self.component_type == "Card":
            return _get_model(
                query=self.component_description, model=model, result_model=CardProxyModel, df_metadata=df_metadata
            )


class Components(BaseModel):
    """Components plan model."""

    components: List[Component]


def create_filter_proxy(df_cols, df_sample, available_components):
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
            Field([], 
            description="Target component to be affected by filter. If none are given "
            "then target all components on the page that use `column`."),
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
        "Be as detailed as possible. Keep the original relavant description AS IS. If this control is used"
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
        _df_schema, _df_sample = df_metadata[self.data_frame]["df_schema"], df_metadata[self.data_frame]["df_sample"]
        _df_cols = list(_df_schema.keys())
        try:
            result_proxy = create_filter_proxy(df_cols=_df_cols, df_sample=_df_sample, available_components=available_components)
            proxy = _get_model(query=filter_prompt, model=model, result_model=result_proxy, df_metadata=df_metadata)  # noqa: E501
            logger.info(f"`Control` proxy: {proxy.dict()}") # when wrong column name is given, `AttributeError: 'ValidationError' object has no attribute 'dict'``
            actual = vm.Filter.parse_obj(
                proxy.dict(exclude={"selector": {"id": True, "actions": True}, "id": True, "type": True})
            )
            # del model_manager._ModelManager__models[proxy.id]  # TODO: This is very wrong and needs to change

        except ValidationError:
            logger.info("Validation failed for `Control`, returning default values. Error details: {e}")
            actual = None
        return actual


class Controls(BaseModel):
    """Controls plan model."""

    controls: List[Control]


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
        " to this layout AS IS. If layout not provided, specify `NO layout`.",
    )

    def create(self, model, df_metadata):
        """Create the layout."""
        if self.layout_description == "NO layout":
            return None

        try:
            proxy = _get_model(
                query=self.layout_description, model=model, result_model=LayoutProxyModel, df_metadata=df_metadata
            )
            actual = vm.Layout.parse_obj(proxy.dict(exclude={}))
        except (ValidationError, AttributeError) as e:
            logger.info(f"Validation failed for `Layout`, returning default values. Error details: {e}")
            actual = None

        return actual


class PagePlanner(BaseModel):
    """Page plan model."""

    title: str = Field(
        ...,
        description="Title of the page. If no description is provided, "
        "make a short and concise title from the components.",
    )
    components: Components
    controls: Controls
    layout: Layout


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
    return _get_model(query=query, model=model, result_model=DashboardPlanner, df_metadata=df_metadata)


def _print_dashboard_plan(dashboard_plan):
    for i, page in enumerate(dashboard_plan.pages):
        for j in page.components.components:
            logger.info("--> " + repr(j))
        logger.info("--> " + repr(page.layout))
        for j in page.controls.controls:
            logger.info("--> " + repr(j))
        logger.info("\n")


if __name__ == "__main__":
    from vizro_ai.chains._llm_models import _get_llm_model
    from vizro.managers import model_manager

    model_default = "gpt-3.5-turbo"
    # model_default = "gpt-4-turbo"

    llm_model = _get_llm_model(model=model_default)
    # # Test the layout planner
    # layout1 = Layout(layout_description="grid=[[0,1]]")
    # print(layout1.create(model=llm_model, df_metadata={}))  # noqa: T201
    # # grid=[[0, 1]]

    # layout1 = Layout(layout_description="The card has text `This is a card`")
    # print(layout1.create(model=llm_model, df_metadata={}))  # noqa: T201
    # # None

    # Test the control planner
    control1 = Control(
        control_type="Filter", 
        control_description="This filter allows users to filter the first table by continent."
        " It applies only to the table displaying worldwide population and GDP data.", 
        data_frame="world_indicators"
        )
    model_manager["world_population_gdp_table"] = vm.AgGrid(figure=dash_ag_grid(data_frame="world_indicators"))

    print(control1.create(
        model=llm_model, 
        available_components=["world_population_gdp_table", "stock_price_table"], 
        df_metadata={'world_indicators': {'df_schema': {'country': 'object', 'continent': 'object', 'year': 'int64', 'lifeExp': 'float64', 'pop': 'int64', 'gdpPercap': 'float64', 'iso_alpha': 'object', 'iso_num': 'int64'}, 'df_sample': '|      | country   | continent   |   year |   lifeExp |       pop |   gdpPercap | iso_alpha   |   iso_num |\n|-----:|:----------|:------------|-------:|----------:|----------:|------------:|:------------|----------:|\n|  976 | Mauritius | Africa      |   1972 |    62.944 |    851334 |    2575.48  | MUS         |       480 |\n|  881 | Lesotho   | Africa      |   1977 |    52.208 |   1251524 |     745.37  | LSO         |       426 |\n|  701 | India     | Asia        |   1977 |    54.208 | 634000000 |     813.337 | IND         |       356 |\n| 1505 | Taiwan    | Asia        |   1977 |    70.59  |  16785196 |    5596.52  | TWN         |       158 |\n|  166 | Botswana  | Africa      |   2002 |    46.634 |   1630347 |   11003.6   | BWA         |        72 |'}})
        )
