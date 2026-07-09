import io

import pandas as pd
from pydantic_ai import Agent, RunContext

from .response_models import CHART_TYPES, BaseChartPlan

chart_agent = Agent[pd.DataFrame, BaseChartPlan](
    deps_type=pd.DataFrame,
    output_type=BaseChartPlan,
    instructions=(
        """You are an expert in data visualization. Given a user request and a pandas DataFrame that is already in
the shape to plot, describe the requested chart declaratively by filling the chart plan: choose a `chart_type`,
map plotly-express arguments to columns via `encodings` (e.g. x, y, color, size, facet_col; for a pie use names
and values), and put styling in `options`. Vizro-AI does not transform data — map the existing columns as-is.
Only reference columns that exist in the data. Do NOT write code."""
    ),
)


@chart_agent.instructions
def add_df(ctx: RunContext[pd.DataFrame | None]) -> str:
    """Add the dataframe context and the available chart types to the prompt."""
    if not isinstance(ctx.deps, pd.DataFrame):
        raise ValueError("DataFrame dependency is required and must be a pandas DataFrame.")

    buffer = io.StringIO()
    ctx.deps.info(buf=buffer)
    return (
        f"Available chart types: {CHART_TYPES}\n\n"
        f"A sample of the data is {ctx.deps.sample(5)} and the data info is:\n{buffer.getvalue()}"
    )
