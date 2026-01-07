import pandas as pd
from pandas.core.frame import DataFrame
from pydantic_ai import Agent, RunContext

from .response_models import BaseChartPlan

# from vizro_ai.plot._response_models import BaseChartPlan, ChartPlan, ChartPlanFactory

chart_agent = Agent[DataFrame, BaseChartPlan](
    deps_type=pd.DataFrame,
    output_type=BaseChartPlan,
    instructions=(
        """You are an expert in plotly data visualization. You are given a user request and you need to generate plotly
chart code."""
    ),
)


@chart_agent.instructions
def add_df(ctx: RunContext[pd.DataFrame | None]) -> str:
    """Add the dataframe to the chart plan."""
    if ctx.deps is None or type(ctx.deps) is not pd.DataFrame:
        raise ValueError("DataFrame dependency is required and must be a pandas DataFrame.")
    return f"A sample of the data is {ctx.deps.sample(5)}"
