"""Code powering the plot command."""

try:
    from pydantic.v1 import BaseModel, create_model, Field, validator, root_validator, PrivateAttr
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, Field, create_model, validator, root_validator, PrivateAttr
from typing import List

import plotly.express as px

from vizro_ai._llm_models import _get_llm_model
from vizro_ai.dashboard._pydantic_output import _get_pydantic_model
from vizro_ai.plot._utils._safeguard import _safeguard_check

import plotly.graph_objects as go
from typing import Optional, Set
import subprocess
import logging

ADDITIONAL_IMPORTS = {
    "import vizro.plotly.express as px",
    "import plotly.graph_objects as go",
    "import pandas as pd",
    "import numpy as np",
    "from vizro.models.types import capture"
}
CUSTOM_CHART_NAME = "custom_chart"

def _format_and_lint(code_string: str) -> str:
    # Tracking https://github.com/astral-sh/ruff/issues/659 for proper python API
    # Good example: https://github.com/astral-sh/ruff/issues/8401#issuecomment-1788806462
    linted = subprocess.check_output(
        ["ruff", "check", "--fix", "--exit-zero", "--silent", "--isolated", "-"], input=code_string, encoding="utf-8"
    )
    formatted = subprocess.check_output(
        ["ruff", "format", "--silent", "--isolated", "-"], input=linted, encoding="utf-8"
    )
    return formatted

class ChartPlanStatic(BaseModel):
    """Chart plan model."""

    chart_type: str = Field(
        ...,
        description="""
        Describes the chart type that best reflects the user request.
        """,
    )
    imports: List[str] = Field(
        ...,
        description="""
        List of import statements required to render the chart.
        """,
    )
    chart_code: str = Field(
        ...,
        description=f"""
        Python code that generates a generates a plotly go.Figure object. It must fulfill the following criteria:
        1. Must be wrapped in a function named `{CUSTOM_CHART_NAME}`
        2. Must accept a single argument `data_frame` which is a pandas DataFrame
        3. Must return a plotly go.Figure object
        4. All data used in the chart must be derived from the data_frame argument, all data manipulations must be done within the function.
        """,
    )
    chart_insights: str = Field(
        ...,
        description="""
        Insights to what the chart explains or tries to show.""",
    )
    code_explanation: str = Field(
        ...,
        description="""
        Explanation of the code steps used for `chart_code` field.""",
    )
    
    _additional_vizro_imports: Set[str] = PrivateAttr(ADDITIONAL_IMPORTS)

    @validator("chart_code")
    def _check_chart_code(cls, v):
        if f"def {CUSTOM_CHART_NAME}(" not in v:
            raise ValueError(f"The chart code must be wrapped in a function named `{CUSTOM_CHART_NAME}`")

        if "data_frame" not in v.split('\n')[0]:
            raise ValueError("The chart code must accept a single argument `data_frame`, and it should be the first argument of the chart.")
        return v

    @validator("chart_code")
    def _test_execute_chart_code(cls, v):
        try:
            _safeguard_check(v)
        except Exception as e:
            raise ValueError(f"Produced code failed the following error: {e}. Please check the code and try again.")
        exec(v)
        return v
    def _get_imports(self):
        return "\n".join(self.imports) + "\n" + "\n".join(self._additional_vizro_imports) + "\n"

    def _get_chart_code(self, chart_name:Optional[str] = None,vizro:bool  =  True):
        chart_code = self.chart_code
        if vizro:
            chart_code = chart_code.replace(f"def {CUSTOM_CHART_NAME}", f"@capture('graph')\ndef {CUSTOM_CHART_NAME}")
        if chart_name is not None:
            chart_code = chart_code.replace(f"def {CUSTOM_CHART_NAME}", f"def {chart_name}")
        return chart_code
    
    def _get_complete_code(self, chart_name: Optional[str] = None, vizro: bool = True, lint: bool = False):
        chart_name = chart_name or CUSTOM_CHART_NAME
        imports = self._get_imports()
        chart_code = self._get_chart_code(chart_name=chart_name, vizro=vizro)
        complete_code = imports + chart_code
        if lint:
            try:
                complete_code = _format_and_lint(complete_code)
            except Exception as e:
                logging.warning(f"Failed to lint the code due to {e}. Please fix and try again.")
        return complete_code

    def _get_fig_object(self, data_frame, chart_name:Optional[str] = None, vizro = True):
        """Get the figure object."""
        ldict = {}
        
        imports = self._get_imports()
        chart_code = self._get_chart_code(chart_name=chart_name, vizro=vizro)
        exec(imports + chart_code, globals(), ldict)
        chart = ldict[f"{chart_name}"]
        return chart(data_frame)


def _create_model(df) -> BaseModel:
    """Create a proxy model."""

    def _test_execute_chart_code(v):
        """Test the execution of the chart code."""
        try:
            _safeguard_check(v)
        except Exception as e:
            raise ValueError(f"Produced code failed the following error: {e}. Please check the code and try again.")
        ldict = {}
        exec(v, globals(), ldict)
        custom_chart = ldict[f"{CUSTOM_CHART_NAME}"]
        fig = custom_chart(df.sample(20))
        assert isinstance(
            fig, go.Figure
        ), f"Expected chart code to return a plotly go.Figure object, but got {type(fig)}"
        return v

    return create_model(
        "ChartPlanDynamic",
        __validators__={
            "validator1": validator("chart_code", allow_reuse=True)(_test_execute_chart_code),
        },
        __base__= ChartPlanStatic,
    )


if __name__ == "__main__":
    from dotenv import load_dotenv, find_dotenv
    import os

    load_dotenv(find_dotenv(usecwd=True))
    # df = px.data.iris()
    df = px.data.gapminder()

    dummy_model = _create_model(df=df)
    # dummy_model(chart_type="foo", imports=["bar"],chart_code="print('hello')",code_explanation="boo",chart_insights="bee")

    test = dummy_model(  # dummy_response = ChartPlanStatic(
        chart_type="Bubble Chart",
        imports=["import plotly.express as px"],
        chart_code="def custom_chart(data_frame):\n    fig = px.scatter(data_frame, x='gdpPercap', y='lifeExp', size='pop', color='continent', hover_name='country', animation_frame='year', log_x=True, size_max=60)\n    return fig",
        # chart_code="print('Hello World')\nx = 1",
        chart_insights="This bubble chart visualizes the changes in life expectancy and GDP per capita over time. Each bubble represents a country, with the size of the bubble indicating the population and the color representing the continent. The animation is based on the year, showing the evolution of the data over time.",
        code_explanation="1. Create a scatter plot using Plotly Express (px).\n2. Set the x-axis to 'gdpPercap' and the y-axis to 'lifeExp'.\n3. Size the bubbles based on 'pop' (population) and color them based on 'continent'.\n4. Enable hover information to display the country name.\n5. Add animation based on the 'year' column to animate the chart over time.\n6. Set log scaling for the x-axis.\n7. Return the Plotly figure object.",
    )

    # model = _get_llm_model()

    # query = "the trend of gdp over years in the US"
    # query = "show me the geo distribution of life expectancy and set year as animation "
    # query = "describe the composition of gdp in continents in 2007, and add horizontal line for avg gdp in 2007"
    # query = "plot a bubble chart to shows the changes in life expectancy gdp per capita  over time. Animate the chart by year"

    # print(df.sample(10).to_string())

    # res = _get_pydantic_model(query=query, llm_model=model, response_model=ChartPlan, df_info=df.sample(10).to_string())

    # print(res.imports)
    # print(res.chart_insights)
    # print(res.code_explanation)
    # print(res.chart_code)
    # exec(res.chart_code)
    # custom_chart = locals()["custom_chart"]
    # fig = custom_chart(df)
    # fig.show()
