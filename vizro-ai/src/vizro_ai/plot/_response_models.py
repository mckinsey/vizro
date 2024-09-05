"""Code powering the plot command."""

try:
    from pydantic.v1 import BaseModel, Field, PrivateAttr, create_model, validator
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, Field, PrivateAttr, create_model, validator
import logging
import subprocess
from typing import List, Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from vizro_ai.plot._utils._safeguard import _safeguard_check

ADDITIONAL_IMPORTS = [
    "import vizro.plotly.express as px",
    "import plotly.graph_objects as go",
    "import pandas as pd",
    "import numpy as np",
    "from vizro.models.types import capture",
]
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


def _exec_code(code: str):
    """Execute code and return the local dictionary."""
    # globals needed to access imports, they will not be modified by exec
    # ldict is used to store the chart function
    # potentially possible to restrict globals to only needed imports, but that is tricky
    ldict = {}
    exec(code, globals(), ldict)  # nosec
    return ldict


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
        List of import statements required to render the chart defined by the `chart_code` field.
        """,
    )
    chart_code: str = Field(
        ...,
        description=f"""
        Python code that generates a generates a plotly go.Figure object. It must fulfill the following criteria:
        1. Must be wrapped in a function named `{CUSTOM_CHART_NAME}`
        2. Must accept a single argument `data_frame` which is a pandas DataFrame
        3. Must return a plotly go.Figure object
        4. All data used in the chart must be derived from the data_frame argument, all data manipulations
        must be done within the function.
        """,
    )
    chart_insights: str = Field(
        ...,
        description="""
        Insights to what the chart explains or tries to show. Ideally concise and between 30 and 60 words.""",
    )
    code_explanation: str = Field(
        ...,
        description="""
        Explanation of the code steps used for `chart_code` field.""",
    )

    _additional_vizro_imports: List[str] = PrivateAttr(ADDITIONAL_IMPORTS)

    @validator("chart_code")
    def _check_chart_code(cls, v):
        # TODO: add more checks: ends with return, has return, no second function def, only one indented line
        if f"def {CUSTOM_CHART_NAME}(" not in v:
            raise ValueError(f"The chart code must be wrapped in a function named `{CUSTOM_CHART_NAME}`")

        if "data_frame" not in v.split("\n")[0]:
            raise ValueError(
                """The chart code must accept a single argument `data_frame`,
and it should be the first argument of the chart."""
            )
        return v

    def _get_imports(self, vizro: bool = False):
        imports = list(dict.fromkeys(self.imports + self._additional_vizro_imports))  # remove duplicates
        if vizro:  # TODO: improve code of below
            imports = [imp for imp in imports if "import plotly.express as px" not in imp]
        else:
            imports = [imp for imp in imports if "vizro" not in imp]
        return "\n".join(imports) + "\n"

    def _get_chart_code(self, chart_name: Optional[str] = None, vizro: bool = False):
        chart_code = self.chart_code
        if vizro:
            chart_code = chart_code.replace(f"def {CUSTOM_CHART_NAME}", f"@capture('graph')\ndef {CUSTOM_CHART_NAME}")
        if chart_name is not None:
            chart_code = chart_code.replace(f"def {CUSTOM_CHART_NAME}", f"def {chart_name}")
        return chart_code

    def _get_complete_code(self, chart_name: Optional[str] = None, vizro: bool = False, lint: bool = True):
        chart_name = chart_name or CUSTOM_CHART_NAME
        imports = self._get_imports(vizro=vizro)
        chart_code = self._get_chart_code(chart_name=chart_name, vizro=vizro)
        unformatted_code = imports + chart_code
        if lint:
            try:
                linted_code = _format_and_lint(unformatted_code)
                return linted_code
            except Exception:
                logging.exception("Code formatting failed; returning unformatted code")
                return unformatted_code

        return unformatted_code

    def get_fig_object(self, data_frame: pd.DataFrame, chart_name: Optional[str] = None, vizro=True):
        """Execute code to obtain the plotly go.Figure object. Be sure to check code to be executed before running.

        Args:
            data_frame: Data frame to be used in the chart.
            chart_name: Name of the chart function. Defaults to `None`,
                in which case it remains as `custom_chart`.
            vizro: Whether to add decorator to make it `vizro-core` compatible. Defaults to `True`.


        """
        chart_name = chart_name or CUSTOM_CHART_NAME
        code_to_execute = self._get_complete_code(chart_name=chart_name, vizro=vizro)
        ldict = _exec_code(code_to_execute)
        chart = ldict[f"{chart_name}"]
        return chart(data_frame)

    @property
    def code(self):
        return self._get_complete_code()

    @property
    def code_vizro(self):
        return self._get_complete_code(vizro=True)


class ChartPlanDynamicFactory:
    def __new__(cls, data_frame: pd.DataFrame) -> ChartPlanStatic:  # TODO: change to ChartPlanDynamic
        def _test_execute_chart_code(v):
            """Test the execution of the chart code."""
            try:
                _safeguard_check(v)
            except Exception as e:
                raise ValueError(
                    f"Produced code failed the safeguard validation: <{e}>. Please check the code and try again."
                )
            try:
                ldict = _exec_code(v)
                custom_chart = ldict[f"{CUSTOM_CHART_NAME}"]
                fig = custom_chart(data_frame.sample(20))
            except Exception as e:
                raise ValueError(
                    f"Produced code execution failed the following error: <{e}>. Please check the code and try again."
                )
            assert isinstance(
                fig, go.Figure
            ), f"Expected chart code to return a plotly go.Figure object, but got {type(fig)}"
            return v

        return create_model(
            "ChartPlanDynamic",
            __validators__={
                "validator1": validator("chart_code", allow_reuse=True)(_test_execute_chart_code),
            },
            __base__=ChartPlanStatic,
        )


if __name__ == "__main__":
    # Write docs
    # Formulate long term todos

    from dotenv import find_dotenv, load_dotenv

    load_dotenv(find_dotenv(usecwd=True))
    from vizro_ai import VizroAI
    from vizro_ai._llm_models import _get_llm_model

    # df = px.data.iris()
    df = px.data.gapminder()

    model = _get_llm_model()

    query = "the trend of gdp over years in the US"
    # query = "show me the geo distribution of life expectancy and set year as animation "
    # query = "describe the composition of gdp in continents in 2007, and add horizontal line for avg gdp in 2007"
    # query = """plot a bubble chart to shows the changes in life expectancy gdp per capita  over time.
    # Animate the chart by year"""

    # print(df.sample(10).to_string())

    # res = _get_pydantic_model(
    # query=query, llm_model=model, response_model=dummy_model, df_info=df.sample(10).to_string())
    # code = res._get_complete_code(lint=True)
    # fig = res._get_fig_object(data_frame=df)
    # fig.show()

    # llm = ChatAnthropic(
    #     model="claude-3-5-sonnet-20240620",
    #     temperature=0,
    #     max_tokens=1024,
    #     timeout=None,
    #     max_retries=2,
    #     api_key = os.environ.get("ANTHROPIC_API_KEY"),
    #     base_url= os.environ.get("ANTHROPIC_API_BASE")
    # )

    ############################################################################################################

    vizro_ai = VizroAI(model=model)
    res2 = vizro_ai.plot(df=df, user_input=query, return_elements=True)
    res2.get_fig_object(data_frame=df).show()
