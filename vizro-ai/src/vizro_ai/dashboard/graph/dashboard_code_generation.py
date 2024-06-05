from typing import List, TypedDict
import re

import pandas as pd
from langgraph.graph import END, StateGraph
from vizro_ai.chains._llm_models import _get_llm_model
from vizro_ai.dashboard.nodes.data_summary import FullDataSummary, requirement_sum_prompt, DfInfo, df_sum_prompt
from vizro_ai.dashboard.nodes.model_summary import ModelSummary, model_sum_prompt
from vizro_ai.dashboard.nodes.core_builder.vizro_ai_db import VizroAIDashboard
from vizro.managers import data_manager
from vizro.managers._data_manager import DataManager

model_default = "gpt-3.5-turbo"
# model_default = "gpt-4o"


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
    data_manager: DataManager


def generate_model_summary(state: GraphState):
    """Generate a summary of the Vizro models required.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation

    """
    messages = state["messages"]
    model_sum_chain = model_sum_prompt | _get_llm_model(model=model_default).with_structured_output(ModelSummary)

    model_summary = model_sum_chain.invoke({"messages": messages})
    # print(f"model_summary: {model_summary}")
    messages += [
        (
            "assistant",
            model_summary,
        )
    ]
    return {"messages": messages}


def compose_imports_code(state: GraphState):
    """Generate code snippet for imports.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation

    """
    messages = state["messages"]
    _, models = messages[-1]

    import_statement = f"from vizro import Vizro\n"

    required_models = []
    for model_name in models.model_summary:
        model_name = model_name.model_required
        required_models.append(model_name)
    final_required_models = list(set(required_models))
    model_import_statement = f"from vizro.models import {', '.join(final_required_models)}\n"
    import_statement += model_import_statement

    if "Graph" in final_required_models:
        import_statement += f"import vizro.plotly.express as px\nfrom vizro.models.types import capture\nimport plotly.graph_objects as go\n"

    if "AgGrid" in final_required_models:
        import_statement += f"from vizro.tables import dash_ag_grid\n"

    # to be removed
    import_statement += f"import pandas as pd\n"

    messages += [
        (
            "assistant",
            import_statement,
        )
    ]
    return {"messages": messages}


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
    messages += [
        (
            "assistant",
            data_requirement_summary,
        )
    ]
    return {"messages": messages}


def generate_dashboard_code(state: GraphState):
    """Generate a dashboard code snippet.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation

    """
    messages = state["messages"]
    _, import_statement = messages[-1]
    # df_schemas = state["df_schemas"]
    # df_heads = state["df_heads"]
    dfs = state["dfs"]

    first_df = dfs[0]
    model = _get_llm_model(model=model_default)
    vizro_ai_dashboard = VizroAIDashboard(model)
    dashboard = vizro_ai_dashboard.build_dashboard(first_df, messages[0])
    dashboard_code_string = dashboard.dict_obj(exclude_unset=True)
    full_code_string = f"\n{import_statement}\ndashboard={dashboard_code_string}\n\nVizro().build(dashboard).run()\n"
    print(f"full_code_string: \n ------- \n{full_code_string}\n ------- \n")

    messages += [
        (
            "assistant",
            full_code_string,
        )
    ]
    return {"messages": messages}


def store_df_info(state: GraphState):
    """Store information about the dataframes.

    Args:
        dfs (list): List of dataframes

    Returns:
        dict: Dictionary containing the dataframes

    """
    df_schemas = state["df_schemas"]
    df_heads = state["df_heads"]
    dfs = state["dfs"]
    messages = state["messages"]
    # print(type(state["data_manager"]))
    data_manager = state["data_manager"]
    current_df_names = []
    cleaned_df_names = []
    for i, df in enumerate(dfs):
        df_schema = df_schemas[i]
        df_head = df_heads[i]
        data_sum_chain = df_sum_prompt | _get_llm_model(model=model_default).with_structured_output(
            DfInfo
        )

        df_name = data_sum_chain.invoke(
            {"df_schema": df_schema, "df_head": df_head, "messages": messages, "current_df_names": current_df_names}
        )

        print(f"df_name: {df_name}")
        current_df_names.append(df_name)

        cleaned_df_name = df_name.dataset_name.lower()
        cleaned_df_name = re.sub(r'\W+', '_', cleaned_df_name)
        cleaned_df_name = cleaned_df_name.strip('_')
        print(f"cleaned_df_name: {cleaned_df_name}")
        cleaned_df_names.append(cleaned_df_name)
        data_manager[cleaned_df_name] = df
    return {"data_manager": data_manager}



def _create_and_compile_graph():
    graph = StateGraph(GraphState)

    ### dashboard code generation ###
    # graph.add_node("generate_data_summary", generate_data_summary)
    graph.add_node("generate_model_summary", generate_model_summary)
    graph.add_node("compose_imports_code", compose_imports_code)
    graph.add_node("generate_dashboard_code", generate_dashboard_code)

    # graph.add_edge("generate_data_summary", "generate_dashboard_code")
    # graph.add_edge("generate_model_summary", "generate_dashboard_code")
    # graph.add_edge("generate_dashboard_code", END)
    graph.add_edge("generate_model_summary", "compose_imports_code")
    graph.add_edge("compose_imports_code", "generate_dashboard_code")
    graph.add_edge("generate_dashboard_code", END)

    # graph.set_entry_point("generate_data_summary")
    graph.set_entry_point("generate_model_summary")

    ### dashboard code generation ###

    # graph.add_node("store_df_info", store_df_info)
    # graph.add_edge("store_df_info", END)
    # graph.set_entry_point("store_df_info")

    runnable = graph.compile()

    return runnable
