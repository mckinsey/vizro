import io

import pandas as pd
from pydantic_ai import Agent, RunContext

from .response_models import BaseChartPlan

chart_agent = Agent[pd.DataFrame, BaseChartPlan](
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
    if not isinstance(ctx.deps, pd.DataFrame):
        raise ValueError("DataFrame dependency is required and must be a pandas DataFrame.")

    buffer = io.StringIO()
    ctx.deps.info(buf=buffer)
    return f"A sample of the data is {ctx.deps.sample(5)} and the data info is:\n{buffer.getvalue()}"
