"""Code generation graph for dashboard generation."""

import logging
import operator
from typing import Annotated, Dict, List, Optional

import pandas as pd
import vizro.models as vm
from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableConfig
from langgraph.constants import END, Send
from langgraph.graph import StateGraph
from tqdm.auto import tqdm
from vizro_ai.dashboard._pydantic_output import _get_pydantic_output
from vizro_ai.dashboard.response_models.dashboard import DashboardPlanner
from vizro_ai.dashboard.response_models.df_info import DfInfo, _create_df_info_content, _get_df_info
from vizro_ai.dashboard.response_models.page import PagePlanner
from vizro_ai.dashboard.utils import DfMetadata, MetadataContent, _execute_step
from vizro_ai.utils.helper import DebugFailure

try:
    from pydantic.v1 import BaseModel, validator
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, validator


logger = logging.getLogger(__name__)


Messages = List[BaseMessage]
"""List of messages."""


class GraphState(BaseModel):
    """Represents the state of dashboard graph.

    Attributes
        messages : With user question, error messages, reasoning
        dfs : Dataframes
        df_metadata : Cleaned dataframe names and their metadata
        dashboard_plan : Plan for the dashboard
        pages : Vizro pages
        dashboard : Vizro dashboard

    """

    messages: List[BaseMessage]
    dfs: List[pd.DataFrame]
    df_metadata: DfMetadata
    dashboard_plan: Optional[DashboardPlanner] = None
    pages: Annotated[List, operator.add]
    dashboard: Optional[vm.Dashboard] = None

    class Config:
        """Pydantic configuration."""

        arbitrary_types_allowed = True

    @validator("dfs")
    def check_dataframes(cls, v):
        """Check if the dataframes are valid."""
        if not isinstance(v, list):
            raise ValueError("dfs must be a list")
        for df in v:
            if not isinstance(df, pd.DataFrame):
                raise ValueError("Each element in dfs must be a Pandas DataFrame")
        return v


def _store_df_info(state: GraphState, config: RunnableConfig) -> Dict[str, DfMetadata]:
    """Store information about the dataframes."""
    dfs = state.dfs
    df_metadata = state.df_metadata
    query = state.messages[0].content
    current_df_names = []
    with tqdm(total=len(dfs), desc="Store df info") as pbar:
        for df in dfs:
            df_schema, df_sample = _get_df_info(df)
            df_info = _create_df_info_content(
                df_schema=df_schema, df_sample=df_sample, current_df_names=current_df_names
            )

            llm = config["configurable"].get("model", None)
            try:
                df_name = _get_pydantic_output(
                    query=query,
                    llm_model=llm,
                    response_model=DfInfo,
                    df_info=df_info,
                ).dataset
            except DebugFailure as e:
                logger.warning(f"Failed in name generation {e}")
                df_name = f"df_{len(current_df_names)}"

            current_df_names.append(df_name)

            pbar.write(f"df_name: {df_name}")
            pbar.update(1)
            df_metadata.metadata[df_name] = MetadataContent(df_schema=df_schema, df=df, df_sample=df_sample)

    return {"df_metadata": df_metadata}


def _dashboard_plan(state: GraphState, config: RunnableConfig) -> Dict[str, DashboardPlanner]:
    """Generate a dashboard plan."""
    node_desc = "Generate dashboard plan"
    pbar = tqdm(total=2, desc=node_desc)
    query = state.messages[0].content
    df_metadata = state.df_metadata

    llm = config["configurable"].get("model", None)

    _execute_step(
        pbar,
        node_desc + " --> in progress \n(this step could take longer " "when more complex requirements are given)",
        None,
    )
    try:
        dashboard_plan = _get_pydantic_output(
            query=query, llm_model=llm, response_model=DashboardPlanner, df_info=df_metadata.get_schemas_and_samples()
        )
    except DebugFailure as e:
        logger.error(f"Error in dashboard plan generation: {e}", exc_info=True)
        raise
    _execute_step(pbar, node_desc + " --> done", None)
    pbar.close()

    return {"dashboard_plan": dashboard_plan}


class BuildPageState(BaseModel):
    """Represents the state of building the page.

    Attributes
        df_metadata : Cleaned dataframe names and their metadata
        page_plan : Plan for the dashboard

    """

    df_metadata: DfMetadata
    page_plan: PagePlanner = None


def _build_page(state: BuildPageState, config: RunnableConfig) -> Dict[str, List[vm.Page]]:
    """Build a page."""
    df_metadata = state["df_metadata"]
    page_plan = state["page_plan"]

    llm = config["configurable"].get("model", None)
    page = page_plan.create(model=llm, df_metadata=df_metadata)

    return {"pages": [page]}


def _continue_to_pages(state: GraphState) -> List[Send]:
    """Map-reduce logic to build pages in parallel."""
    df_metadata = state.df_metadata
    return [
        Send(node="_build_page", arg={"page_plan": v, "df_metadata": df_metadata}) for v in state.dashboard_plan.pages
    ]


def _build_dashboard(state: GraphState) -> Dict[str, vm.Dashboard]:
    """Build a dashboard."""
    dashboard_plan = state.dashboard_plan
    pages = state.pages

    dashboard = vm.Dashboard(title=dashboard_plan.title, pages=pages)

    return {"dashboard": dashboard}


def _create_and_compile_graph():
    graph = StateGraph(GraphState)

    graph.add_node("_store_df_info", _store_df_info)
    graph.add_node("_dashboard_plan", _dashboard_plan)
    graph.add_node("_build_page", _build_page)
    graph.add_node("_build_dashboard", _build_dashboard)

    graph.add_edge("_store_df_info", "_dashboard_plan")
    graph.add_conditional_edges("_dashboard_plan", _continue_to_pages)
    graph.add_edge("_build_page", "_build_dashboard")
    graph.add_edge("_build_dashboard", END)

    graph.set_entry_point("_store_df_info")

    runnable = graph.compile()

    return runnable
