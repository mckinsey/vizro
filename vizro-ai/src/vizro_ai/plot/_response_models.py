"""Code powering the plot command."""

try:
    from pydantic.v1 import BaseModel, Field, PrivateAttr, create_model, validator
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, Field, PrivateAttr, create_model, validator
import logging
from typing import Optional, Union

import autoflake
import black
import pandas as pd
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


def _strip_markdown(code_string: str) -> str:
    """Strip markdown code block from the code string."""
    prefixes = ["```python\n", "```py\n", "```\n"]
    for prefix in prefixes:
        if code_string.startswith(prefix):
            code_string = code_string[len(prefix) :]
            break
    if code_string.endswith("```"):
        code_string = code_string[: -len("```")]
    return code_string.strip()


def _format_and_lint(code_string: str) -> str:
    # Tracking https://github.com/astral-sh/ruff/issues/659 for proper Python API
    # Good example: https://github.com/astral-sh/ruff/issues/8401#issuecomment-1788806462
    # While we wait for the API, we can autoflake and black to process code strings.

    removed_imports = autoflake.fix_code(code_string, remove_all_unused_imports=True)
    # Black doesn't yet have a Python API, so format_str might not work at some point in the future.
    # https://black.readthedocs.io/en/stable/faq.html#does-black-have-an-api
    formatted = black.format_str(removed_imports, mode=black.Mode())
    return formatted


def _exec_code(code: str, namespace: dict) -> dict:
    """Execute code and return the local dictionary."""
    # Need the global namespace for the imports to work for executed code
    # Tried just handling it in local scope, ie getting the import statement into ldict, but it didn't work
    # TODO: ideally in future we properly handle process and namespace separation, or even Docke execution
    # TODO: this is also important as it can affect unit-tests influencing one another, which is really not good!
    ldict = {}
    exec(code, namespace, ldict)  # nosec
    namespace.update(ldict)
    return namespace


class ChartPlan(BaseModel):
    """Chart plan model."""

    chart_type: str = Field(
        ...,
        description="""
        Describes the chart type that best reflects the user request.
        """,
    )
    imports: list[str] = Field(
        ...,
        description="""
        List of import statements required to render the chart defined by the `chart_code` field. Ensure that every
        import statement is a separate list/array entry: An example of valid list of import statements would be:

        [`import pandas as pd`,
        `import plotly.express as px`]
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

    _additional_vizro_imports: list[str] = PrivateAttr(ADDITIONAL_IMPORTS)

    @validator("chart_code")
    def _check_chart_code(cls, v):
        v = _strip_markdown(v)

        # TODO: add more checks: ends with return, has return, no second function def, only one indented line
        if f"def {CUSTOM_CHART_NAME}(" not in v:
            raise ValueError(f"The chart code must be wrapped in a function named `{CUSTOM_CHART_NAME}`")

        first_line = v.split("\n")[0].strip()
        if "data_frame" not in first_line:
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

    def get_fig_object(self, data_frame: Union[pd.DataFrame, str], chart_name: Optional[str] = None, vizro=True):
        """Execute code to obtain the plotly go.Figure object. Be sure to check code to be executed before running.

        Args:
            data_frame: Dataframe or string representation of the dataframe.
            chart_name: Name of the chart function. Defaults to `None`,
                in which case it remains as `custom_chart`.
            vizro: Whether to add decorator to make it `vizro-core` compatible. Defaults to `True`.


        """
        chart_name = chart_name or CUSTOM_CHART_NAME
        code_to_execute = self._get_complete_code(chart_name=chart_name, vizro=vizro)
        namespace = globals()
        namespace = _exec_code(code_to_execute, namespace)
        chart = namespace[f"{chart_name}"]
        return chart(data_frame)

    @property
    def code(self):
        return self._get_complete_code()

    @property
    def code_vizro(self):
        return self._get_complete_code(vizro=True)


class ChartPlanFactory:
    def __new__(cls, data_frame: pd.DataFrame) -> ChartPlan:  # TODO: change to ChartPlanDynamic
        def _test_execute_chart_code(v, values):
            """Test the execution of the chart code."""
            imports = "\n".join(values.get("imports", []))
            code_to_validate = imports + "\n\n" + v
            try:
                _safeguard_check(code_to_validate)
            except Exception as e:
                raise ValueError(
                    f"Produced code failed the safeguard validation: <{e}>. Please check the code and try again."
                )
            try:
                namespace = globals()
                namespace = _exec_code(code_to_validate, namespace)
                custom_chart = namespace[f"{CUSTOM_CHART_NAME}"]
                fig = custom_chart(data_frame.sample(10, replace=True))
            except Exception as e:
                raise ValueError(
                    f"Produced code execution failed the following error: <{e}>. Please check the code and try again, "
                    f"alternatively try with a more powerful model."
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
            __base__=ChartPlan,
        )
