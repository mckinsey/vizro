"""Code generation graph for dashboard generation."""

import logging
import operator
from typing import Annotated, Optional

import pandas as pd
import vizro.models as vm
from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableConfig
from langgraph.constants import END, Send
from langgraph.graph import StateGraph
from pydantic import BaseModel, BeforeValidator, ConfigDict, ValidationError
from tqdm.auto import tqdm

from vizro_ai.dashboard._pydantic_output import _get_pydantic_model
from vizro_ai.dashboard._response_models.dashboard import DashboardPlan
from vizro_ai.dashboard._response_models.df_info import DfInfo, _create_df_info_content, _get_df_info
from vizro_ai.dashboard._response_models.page import PagePlan
from vizro_ai.dashboard.utils import AllDfMetadata, DfMetadata, _execute_step
from vizro_ai.utils.helper import DebugFailure

logger = logging.getLogger(__name__)


Messages = list[BaseMessage]
"""List of messages."""


def _validate_dfs(v):
    if isinstance(v, pd.DataFrame):
        # without this, the model will not be able to validate the dfs properly.
        # for example, if a single df is passed, it's parsed as a list of strings.
        # which then raises validation error like:
        # dfs.0
        #  Input should be an instance of DataFrame [type=is_instance_of, input_value='country', input_type=str]
        #    For further information visit https://errors.pydantic.dev/2.10/v/is_instance_of
        raise ValueError(
            "A single DataFrame was provided to 'dfs'. Please pass a list of DataFrames instead, "
            "e.g., [df] or [df1, df2, ...]"
        )

    if not isinstance(v, list) or not all(isinstance(df, pd.DataFrame) for df in v):
        raise ValueError("Input should be a list of DataFrames")

    return v


class GraphState(BaseModel):
    """Represents the state of the dashboard graph.

    Attributes:
        messages: With user question, error messages, reasoning
        dfs: Dataframes
        all_df_metadata: Cleaned dataframe names and their metadata
        dashboard_plan: Plan for the dashboard
        pages: Vizro pages
        dashboard: Vizro dashboard
        custom_charts_code: Custom charts code

    """

    messages: list[BaseMessage]
    dfs: Annotated[list[pd.DataFrame], BeforeValidator(_validate_dfs)]
    all_df_metadata: AllDfMetadata
    dashboard_plan: Optional[DashboardPlan] = None
    pages: Annotated[list, operator.add]
    dashboard: Optional[type(vm.Dashboard)] = None
    custom_charts_code: Annotated[list, operator.add]
    custom_charts_imports: Annotated[list, operator.add]

    model_config = ConfigDict(arbitrary_types_allowed=True)


def _store_df_info(state: GraphState, config: RunnableConfig) -> dict[str, AllDfMetadata]:
    """Store information about the dataframes."""
    dfs = state.dfs
    all_df_metadata = state.all_df_metadata
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
                df_name = _get_pydantic_model(
                    query=query,
                    llm_model=llm,
                    response_model=DfInfo,
                    df_info=df_info,
                ).dataset
            except DebugFailure as e:
                logger.warning(f"Failed in name generation {e}")
                df_name = f"df_{len(current_df_names) + 1}"

            # fallback to a less descriptive but unique name if llm fails
            if df_name in current_df_names:
                df_name = f"df_{len(current_df_names) + 1}"

            current_df_names.append(df_name)

            pbar.write(f"df_name: {df_name}")
            pbar.update(1)
            all_df_metadata.all_df_metadata[df_name] = DfMetadata(df_schema=df_schema, df=df, df_sample=df_sample)

    return {"all_df_metadata": all_df_metadata}


def _dashboard_plan(state: GraphState, config: RunnableConfig) -> dict[str, DashboardPlan]:
    """Generate a dashboard plan."""
    node_desc = "Generate dashboard plan"
    pbar = tqdm(total=2, desc=node_desc)
    query = state.messages[0].content
    all_df_metadata = state.all_df_metadata

    llm = config["configurable"].get("model", None)

    _execute_step(
        pbar,
        node_desc + " --> in progress \n(this step could take longer when more complex requirements are given)",
        None,
    )
    try:
        dashboard_plan = _get_pydantic_model(
            query=query,
            llm_model=llm,
            response_model=DashboardPlan,
            df_info=all_df_metadata.get_schemas_and_samples(),
        )
    except (DebugFailure, ValidationError) as e:
        raise ValueError(
            f"""
            Failed to create a valid dashboard plan. Try rephrase the prompt or select a different
            model. Error details:
            {e}
            """
        )

    _execute_step(pbar, node_desc + " --> done", None)
    pbar.close()

    return {"dashboard_plan": dashboard_plan}


class BuildPageState(BaseModel):
    """Represents the state of building the page.

    Attributes:
        all_df_metadata: Cleaned dataframe names and their metadata
        page_plan: Plan for the dashboard page

    """

    all_df_metadata: AllDfMetadata
    page_plan: Optional[PagePlan] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)  # this is due to pandas df


def _build_page(state: BuildPageState, config: RunnableConfig) -> dict[str, list[vm.Page]]:
    """Build a page."""
    all_df_metadata = state["all_df_metadata"]
    page_plan = state["page_plan"]

    llm = config["configurable"].get("model", None)
    # TODO: this is a hack to get the custom chart code - we should find a much better way to do so
    page, custom_chart_imports, custom_chart_code = page_plan.create(model=llm, all_df_metadata=all_df_metadata)

    return {"pages": [page], "custom_charts_imports": [custom_chart_imports], "custom_charts_code": [custom_chart_code]}


def _continue_to_pages(state: GraphState) -> list[Send]:
    """Map-reduce logic to build pages in parallel."""
    all_df_metadata = state.all_df_metadata
    return [
        Send(node="_build_page", arg={"page_plan": v, "all_df_metadata": all_df_metadata})
        for v in state.dashboard_plan.pages
    ]


def _build_dashboard(state: GraphState) -> dict[str, vm.Dashboard]:
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
