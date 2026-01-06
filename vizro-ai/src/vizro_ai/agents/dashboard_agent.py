import os
from dataclasses import dataclass
from typing import Any

import logfire
import pandas as pd
import plotly.express as px
import vizro.models as vm
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError
from pydantic.json_schema import GenerateJsonSchema
from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.anthropic import AnthropicProvider
from vizro import Vizro

# from vizro_ai.plot._response_models import BaseChartPlan, ChartPlan, ChartPlanFactory


class NoDefsGenerateJsonSchema(GenerateJsonSchema):
    """Custom schema generator that handles reference cases appropriately."""

    def generate(self, schema, mode="validation"):
        """Generate schema and resolve references if needed."""
        json_schema = super().generate(schema, mode=mode)

        # If schema is a reference (has $ref but no properties)
        if "$ref" in json_schema and "properties" not in json_schema:
            # Extract the reference path - typically like "#/$defs/ModelName"
            ref_path = json_schema["$ref"]
            if ref_path.startswith("#/$defs/"):
                model_name = ref_path.split("/")[-1]
                # Get the referenced definition from $defs
                # Simply copy the referenced definition content to the top level
                json_schema.update(json_schema["$defs"][model_name])
                # Remove the $ref since we've resolved it
                json_schema.pop("$ref", None)

        # Remove the $defs section if it exists
        json_schema.pop("$defs", None)
        return json_schema


@dataclass
class ModelJsonSchemaResults:
    """Results of the get_model_json_schema tool."""

    model_name: str
    json_schema: dict[str, Any]
    additional_info: str


class BaseDashboardPlan(BaseModel):
    """Base class for dashboard plans."""

    dashboard_config: dict[str, Any]
    # dashboard_code: str


dashboard_agent = Agent(
    deps_type=list[pd.DataFrame],
    output_type=BaseDashboardPlan,
    instructions=(
        """You are an expert in Vizro configuration. Given a user request and a list of dataframes,
        you need to generate a dashboard configuration.
        You should use the `get_model_json_schema` tool to get the JSON schema for the required models. Start with
        `Dashboard` and `Page` and then request what you need to add to the dashboard. You choices are: Graph, AgGrid,
        Card, Container, Filter, Parameter, Layout, Grid, Flex and more. Your final output should be a dashboard config.
        Call the `get_model_json_schema` tool only ONCE per model, then move to the final dashboard config putting it all together.
"""
    ),
    retries=10,
)


@dashboard_agent.instructions
def add_df(ctx: RunContext[list[pd.DataFrame]]) -> str:
    """Add the dataframe to the dashboard plan."""
    # Create a sample representation of each dataframe in the list
    samples = []
    for i, df in enumerate(ctx.deps):
        samples.append(f"Dataframe {i + 1}:\n{df.sample(5)}")

    return "A sample of the data is:\n" + "\n\n".join(samples)


@dashboard_agent.output_validator
def validate_dashboard_config(output: BaseDashboardPlan) -> BaseDashboardPlan:
    """Validate the dashboard configuration."""
    import copy

    # Make a deep copy to prevent mutation of the original config
    config_copy = copy.deepcopy(output.dashboard_config)

    try:
        vm.Dashboard.model_validate(config_copy)
    except ValidationError as e:
        raise ModelRetry(f"Invalid dashboard configuration: {e}")
    # TODO: not sure this works as expected, ie really retrying with the specific error message!
    return output


class GraphEnhanced(vm.Graph):
    """A Graph model that uses Plotly Express to create the figure."""

    figure: dict[str, Any] = Field(
        description="""
For simpler charts and without need for data manipulation, use this field:
This is the plotly express figure to be displayed. Only use valid plotly express functions to create the figure.
Only use the arguments that are supported by the function you are using and where no extra modules such as statsmodels
are needed (e.g. trendline):
- Configure a dictionary as if this would be added as **kwargs to the function you are using.
- You must use the key: "_target_: "<function_name>" to specify the function you are using. Do NOT precede by
    namespace (like px.line)
- you must refer to the dataframe by name, check file_name in the data_infos field ("data_frame": "<file_name>")
- do not use a title if your Graph model already has a title.

For more complex charts and those that require data manipulation, use the `custom_charts` field:
- create the suitable number of custom charts and add them to the `custom_charts` field
- refer here to the function signature you created
- you must use the key: "_target_: "<custom_chart_name>"
- you must refer to the dataframe by name, check file_name in the data_infos field ("data_frame": "<file_name>")
- in general, DO NOT modify the background (with plot_bgcolor) or color sequences unless explicitly asked for
- when creating hover templates, EXPLICITLY style them to work on light and dark mode
"""
    )


class AgGridEnhanced(vm.AgGrid):
    """AgGrid model that uses dash-ag-grid to create the figure."""

    figure: dict[str, Any] = Field(
        description="""
This is the ag-grid figure to be displayed. Only use arguments from the [`dash-ag-grid` function](https://dash.plotly.com/dash-ag-grid/reference).

The only difference to the dash version is that:
    - you must use the key: "_target_: "dash_ag_grid"
    - you must refer to data via "data_frame": <data_frame_name> and NOT via columnDefs and rowData (do NOT set)
        """
    )


@dashboard_agent.tool
def get_model_json_schema(ctx: RunContext[list[pd.DataFrame]], model_name: str) -> ModelJsonSchemaResults:
    """Get the JSON schema for the specified Vizro model.

    Args:
        model_name: Name of the Vizro model to get schema for (e.g., 'Card', 'Dashboard', 'Page')

    Returns:
        JSON schema of the requested Vizro model
    """
    modified_models = {
        "Graph": GraphEnhanced,
        "AgGrid": AgGridEnhanced,
        "Table": AgGridEnhanced,
    }

    if model_name in modified_models:
        return ModelJsonSchemaResults(
            model_name=model_name,
            json_schema=modified_models[model_name].model_json_schema(schema_generator=NoDefsGenerateJsonSchema),
            additional_info="""LLM must remember to replace `$ref` with the actual config. Request the schema of
that model if necessary.""",
        )

    if not hasattr(vm, model_name):
        return ModelJsonSchemaResults(
            model_name=model_name,
            json_schema={},
            additional_info=f"Model '{model_name}' not found in vizro.models",
        )

    model_class = getattr(vm, model_name)
    return ModelJsonSchemaResults(
        model_name=model_name,
        json_schema=model_class.model_json_schema(schema_generator=NoDefsGenerateJsonSchema),
        additional_info="""LLM must remember to replace `$ref` with the actual config. Request the schema of
that model if necessary.""",
    )


if __name__ == "__main__":
    load_dotenv()
    # configure logfire
    logfire.configure(token=os.getenv("LOGFIRE_TOKEN"))
    logfire.instrument_pydantic_ai()

    # User can configure model, including usage limits etc
    # model = OpenAIChatModel(
    #     "gpt-5-2025-08-07",
    #     provider=OpenAIProvider(base_url=os.getenv("OPENAI_BASE_URL"), api_key=os.getenv("OPENAI_API_KEY")),
    # )
    model = AnthropicModel(
        "claude-3-5-haiku-latest",
        provider=AnthropicProvider(api_key=os.getenv("ANTHROPIC_API_KEY")),
    )
    # So far can't get google to work...
    # model = GoogleModel(
    #     "gemini-2.5-flash-lite",
    #     provider=GoogleProvider(
    #         vertexai=True, api_key=os.getenv("GOOGLE_API_KEY"), base_url=os.getenv("GOOGLE_BASE_URL")
    #     ),
    # )

    # Get some data
    df_iris = px.data.iris()
    df_stocks = px.data.stocks()

    # Run the agent - user can choose the data_frame
    result = dashboard_agent.run_sync(
        model=model,
        user_prompt="Create a single page vizro dashboard with two charts, and three cards above the two charts. Refer to the data as iris and stocks.",
        deps=[df_iris, df_stocks],
    )
    print(result.output.dashboard_config)

    Vizro._reset()
    from vizro import Vizro
    from vizro.managers import data_manager

    data_manager["iris"] = df_iris
    data_manager["stocks"] = df_stocks

    config = result.output.dashboard_config
    dashboard = vm.Dashboard.model_validate(config)
    Vizro().build(dashboard=dashboard).run()

"""Learnings for the day

Generally dashboard creation via an agent can also work
Agent calls the correct tools
In the end things looked promising!
Anthropic models are much better seemingly than OpenAI models

Struggled still with (mostly with OpenAI):
- repeated tool calls
- run not finishing
- no proper output validation (invalid dashboard seemed to pass the output validator)
- things being rather slow

In general I am not fully clear on what architecture would be best:
- as is, I one agent with tools
- or more complex like agents that are tools or even a graph ==> ultimately I think we just have a main agent workflow
  - https://ai.pydantic.dev/multi-agent-applications/
  - so probably some form of final schema one works towards, which ends as soon as it passes might be good

Things to further investigate:
- Advanced tool returns: https://ai.pydantic.dev/tools/#advanced-tool-returns
- Dynamic tools: https://ai.pydantic.dev/tools/#tool-prepare
- Output functions: https://ai.pydantic.dev/output/#output-functions
- Output modes: https://ai.pydantic.dev/output/#output-modes
- Output validators: https://ai.pydantic.dev/output/#output-validator-functions
"""
