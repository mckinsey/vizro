from typing import List, TypedDict

import pandas as pd
from langgraph.graph import END, StateGraph
from vizro_ai.chains._llm_models import _get_llm_model
from vizro_ai.dashboard.data_summary import FullDataSummary, requirement_sum_prompt
from vizro_ai.dashboard.nodes.core_builder.vizro_ai_db import VizroAIDashboard

# model_default = "gpt-3.5-turbo"
model_default = "gpt-4o"


class GraphState(TypedDict):
    """Represents the state of dashboard graph.

    Attributes
        messages : With user question, error messages, reasoning
        df_schemas : Schema of the dataframes
        df_heads : Data sample of the dataframes
        dfs : Dataframes

    """

    messages: List
    df_schemas: List[str]
    df_heads: List[str]
    dfs: List[pd.DataFrame]


def generate_data_summary(state: GraphState):
    """Generate a summary of the dataframes provided.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation

    """
    messages = state["messages"]
    df_schemas = state["df_schemas"]
    df_heads = state["df_heads"]
    requirement_sum_chain = requirement_sum_prompt | _get_llm_model(model=model_default).with_structured_output(
        FullDataSummary
    )

    data_requirement_summary = requirement_sum_chain.invoke(
        {"df_heads": df_heads, "df_schemas": df_schemas, "messages": messages}
    )
    # messages += [
    #     (
    #         "assistant",
    #         data_requirement_summary,
    #     )
    # ]
    return {"messages": messages}


def generate_dashboard_code(state: GraphState):
    """Generate a dashboard code snippet.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation

    """
    messages = state["messages"]
    df_schemas = state["df_schemas"]
    df_heads = state["df_heads"]
    dfs = state["dfs"]

    first_df = dfs[0]
    model = _get_llm_model(model=model_default)
    vizro_ai_dashboard = VizroAIDashboard(model)
    dashboard = vizro_ai_dashboard.build_dashboard(first_df, messages[0])
    dashboard_code_string = dashboard.dict_obj(exclude_unset=True)

    messages += [
        (
            "assistant",
            dashboard_code_string,
        )
    ]
    return {"messages": messages}


def _create_and_compile_graph():
    graph = StateGraph(GraphState)

    graph.add_node("generate_data_summary", generate_data_summary)
    graph.add_node("generate_dashboard_code", generate_dashboard_code)

    graph.add_edge("generate_data_summary", "generate_dashboard_code")
    graph.add_edge("generate_dashboard_code", END)

    graph.set_entry_point("generate_data_summary")

    runnable = graph.compile()

    return runnable
