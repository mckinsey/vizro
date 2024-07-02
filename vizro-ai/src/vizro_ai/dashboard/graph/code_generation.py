"""Code generation graph for dashboard generation."""

import inspect
import logging
import operator
import re
from typing import Annotated, Any, Dict, List, Union

import pandas as pd
import vizro.models as vm
from langchain_core.messages import BaseMessage, FunctionMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.constants import END, Send
from langgraph.graph import StateGraph
from vizro_ai.dashboard.nodes.core_builder.build import PageBuilder
from vizro_ai.dashboard.nodes.core_builder.plan import (
    DashboardPlanner,
    PagePlanner,
    _get_dashboard_plan,
    _print_dashboard_plan,
)
from vizro_ai.dashboard.nodes.data_summary import DfInfo, _get_df_info, df_sum_prompt
from vizro_ai.dashboard.nodes.imports_builder import ModelSummary, _generate_import_statement, model_sum_prompt

try:
    from pydantic.v1 import BaseModel, validator
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, validator


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


DfMetadata = Dict[str, Dict[str, Union[Dict[str, str], str]]]
"Cleaned dataframe names and their metadata."

Messages = List[BaseMessage]
"List of messages."


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
    dashboard_plan: DashboardPlanner = None
    pages: Annotated[List, operator.add]
    dashboard: vm.Dashboard = None

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
    logger.info("*** _store_df_info ***")
    dfs = state.dfs
    df_metadata = state.df_metadata
    messages = state.messages
    current_df_names = []
    for df in dfs:
        df_schema, df_sample = _get_df_info(df)

        llm = config["configurable"].get("model", None)
        data_sum_chain = df_sum_prompt | llm.with_structured_output(DfInfo)

        df_name = data_sum_chain.invoke(
            {"messages": messages, "df_schema": df_schema, "df_sample": df_sample, "current_df_names": current_df_names}
        )

        current_df_names.append(df_name)

        cleaned_df_name = df_name.dataset_name.lower()
        cleaned_df_name = re.sub(r"\W+", "_", cleaned_df_name)
        df_id = cleaned_df_name.strip("_")
        logger.info(f"df_name: {df_name} --> df_id: {df_id}")
        df_metadata[df_id] = {"df_schema": df_schema, "df_sample": df_sample}

    return {"df_metadata": df_metadata}


def _compose_imports_code(state: GraphState, config: RunnableConfig) -> Dict[str, Messages]:
    """Generate code snippet for imports."""
    logger.info("*** _compose_imports_code ***")
    messages = state.messages

    llm = config["configurable"].get("model", None)
    model_sum_chain = model_sum_prompt | llm.with_structured_output(ModelSummary)

    vizro_model_summary = model_sum_chain.invoke({"messages": messages})

    import_statement = _generate_import_statement(vizro_model_summary)

    messages.append(FunctionMessage(content=import_statement, name=inspect.currentframe().f_code.co_name))
    return {"messages": messages}


def _dashboard_plan(state: GraphState, config: RunnableConfig) -> Dict[str, DashboardPlanner]:
    """Generate a dashboard plan."""
    logger.info("*** _dashboard_plan ***")
    query = state.messages[0].content
    df_metadata = state.df_metadata

    llm = config["configurable"].get("model", None)
    dashboard_plan = _get_dashboard_plan(query=query, model=llm, df_metadata=df_metadata)
    _print_dashboard_plan(dashboard_plan)

    return {"dashboard_plan": dashboard_plan}


def _generate_dashboard_code(state: GraphState) -> Dict[str, Messages]:
    """Generate a dashboard code snippet."""
    logger.info("*** _generate_dashboard_code ***")
    messages = state.messages[-1].content
    import_statement = messages
    dashboard = state.dashboard

    dashboard_code_string = dashboard.dict_obj(exclude_unset=True)
    full_code_string = f"\n{import_statement}\ndashboard={dashboard_code_string}\n\nVizro().build(dashboard).run()\n"
    logger.info(f"full_code_string: \n ------- \n{full_code_string}\n ------- \n")

    messages.append(FunctionMessage(content=full_code_string, name=inspect.currentframe().f_code.co_name))
    return {"messages": messages}


class BuildPageState(BaseModel):
    """Represents the state of building the page.

    Attributes
        df_metadata : Cleaned dataframe names and their metadata
        page_plan : Plan for the dashboard

    """

    df_metadata: Dict[str, Dict[str, Any]]
    page_plan: PagePlanner = None


def _build_page(state: BuildPageState, config: RunnableConfig) -> Dict[str, List[vm.Page]]:
    """Build a page."""
    logger.info("*** build_page ***")
    df_metadata = state["df_metadata"]
    page_plan = state["page_plan"]

    llm = config["configurable"].get("model", None)
    page = PageBuilder(
        model=llm,
        df_metadata=df_metadata,
        page_plan=page_plan,
    ).page

    return {"pages": [page]}


def continue_to_pages(state: GraphState) -> List[Send]:
    """Continue to build pages."""
    df_metadata = state.df_metadata
    return [Send("_build_page", {"page_plan": v, "df_metadata": df_metadata}) for v in state.dashboard_plan.pages]


def _build_dashboard(state: GraphState) -> Dict[str, vm.Dashboard]:
    """Build a dashboard."""
    logger.info("*** build_dashboard ***")
    dashboard_plan = state.dashboard_plan
    pages = state.pages

    dashboard = vm.Dashboard(title=dashboard_plan.title, pages=pages)

    return {"dashboard": dashboard}


def _create_and_compile_graph():
    # main graph
    graph = StateGraph(GraphState)

    graph.add_node("_store_df_info", _store_df_info)
    graph.add_node("_compose_imports_code", _compose_imports_code)
    graph.add_node("_dashboard_plan", _dashboard_plan)
    graph.add_node("_build_page", _build_page)
    graph.add_node("_build_dashboard", _build_dashboard)

    graph.add_node("_generate_dashboard_code", _generate_dashboard_code)

    graph.add_edge("_store_df_info", "_compose_imports_code")
    graph.add_edge("_compose_imports_code", "_dashboard_plan")
    graph.add_conditional_edges("_dashboard_plan", continue_to_pages)
    graph.add_edge("_build_page", "_build_dashboard")

    # temporarily removed the node _generate_dashboard_code, will add it back once
    # the code to string is ready
    # graph.add_edge("_build_dashboard", "_generate_dashboard_code")
    # graph.add_edge("_generate_dashboard_code", END)
    graph.add_edge("_build_dashboard", END)

    graph.set_entry_point("_store_df_info")

    runnable = graph.compile()

    return runnable


if __name__ == "__main__":
    user_input = """
                I need a page with a table showing the population per continent \n
                I also want a page with two \ncards on it. One should be a card saying:
                `This was the jolly data dashboard, it was created in Vizro which is amazing` \n,
                and the second card should link to `https://vizro.readthedocs.io/`. The title of
                the dashboard should be: `My wonderful \njolly dashboard showing a lot of info`.\n
                The layout of this page should use `grid=[[0,1]]`
                """
    previous_fn_res = """"
                from vizro import Vizro\nfrom vizro.models import AgGrid, Card, Dashboard, Page\nfrom "
                "vizro.tables import dash_ag_grid\nimport pandas as pd\n"
                """
    test_state = {
        "messages": [
            HumanMessage(content=user_input),
            FunctionMessage(content=previous_fn_res, name="_compose_imports_code"),
        ],
        "dfs": [
            pd.DataFrame(),
        ],
        "df_metadata": {
            "globaldemographics": {
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
                "df_sample": "|      | country   | continent   |   year |   lifeExp |      pop |   "
                "gdpPercap | iso_alpha   |   iso_num |\n|-----:|:----------|:------------|-------:"
                "|----------:|---------:|------------:|:------------|----------:|\n|  215 | "
                "Burundi   | Africa      |   2007 |    49.58  |  8390505 |     430.071 | BDI"
                "         |       108 |\n| 1545 | Togo      | Africa      |   1997 |    58.39  |"
                "  4320890 |     982.287 | TGO         |       768 |\n|  772 | Italy     | Europe"
                "      |   1972 |    72.19  | 54365564 |   12269.3   | ITA         |       380 |\n|"
                " 1322 | Senegal   | Africa      |   1962 |    41.454 |  3430243 |    1654.99  | SEN"
                "         |       686 |\n|  732 | Iraq      | Asia        |   1952 |    45.32  |  5441766"
                " |    4129.77  | IRQ         |       368 |",
            },
        },
    }
    sample_state = GraphState(**test_state)
    message = _generate_dashboard_code(sample_state)
    print(message)  # noqa: T201
