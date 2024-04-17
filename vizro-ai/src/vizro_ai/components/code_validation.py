"""Code Validation Component."""

import traceback
from typing import Dict, Tuple

try:
    from pydantic.v1 import BaseModel, Field
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, Field

from vizro_ai.chains._chain_utils import _log_time
from vizro_ai.chains._llm_models import LLM_MODELS
from vizro_ai.components import VizroAiComponentBase
from vizro_ai.schema_manager import SchemaManager

# 1. Define schema
openai_schema_manager = SchemaManager()


@openai_schema_manager.register
class CodeDebug(BaseModel):
    """Fixed code snippet after handling the error."""

    fixed_code: str = Field(
        ..., description="Complete code snippet after fixing the bug, Full snippet after fix, NOT only the fix line"
    )


# 2. Define prompt
debugging_prompt = (
    "Return the full code snippet after fixing the bug in the code snippet {code_snippet}, this is the error message "
    "{input},"
)


# 3. Define Component
class GetDebugger(VizroAiComponentBase):
    """Get Visual code.

    Attributes
        prompt (str): Prompt visual code.

    """

    prompt: str = debugging_prompt

    def __init__(self, llm: LLM_MODELS):
        """Initialization of Chart Selection components.

        Args:
            llm: LLM model wrapped with Langchain wrapper

        """
        super().__init__(llm)

    def _pre_process(self, code_snippet: str, *args, **kwargs) -> Tuple[Dict, Dict]:
        """Preprocess for code debugging.

        It should return llm_kwargs and partial_vars_map.
        """
        llm_kwargs_to_use = openai_schema_manager.get_llm_kwargs("CodeDebug")
        partial_vars_map = {"code_snippet": code_snippet}

        return llm_kwargs_to_use, partial_vars_map

    def _post_process(self, response: Dict, *args, **kwargs) -> str:
        """Post process for visual code.

        Insert df code and clean up with vizro import.
        """
        return response.get("fixed_code")

    @_log_time
    def run(self, code_snippet: str, chain_input: str = "") -> str:
        """Run chain to get visual code.

        Args:
            chain_input: Error message as input here.
            code_snippet: Code snippet.

        Returns:
            Visual code snippet.

        """
        return super().run(chain_input=chain_input, code_snippet=code_snippet)


if __name__ == "__main__":
    import plotly.express as px

    from vizro_ai.chains._llm_models import _get_llm_model

    llm_to_use = _get_llm_model()

    df = px.data.gapminder()
    test_code_snippet = "import numpy as np\n" "import pandas as pd\n" "\n" "print(df['country', 'continent'])\n"

    try:
        exec(test_code_snippet)  # nosec
    except Exception:
        error_msg = f"{traceback.format_exc()}"

    test = GetDebugger(llm=llm_to_use)

    res = test.run(chain_input=error_msg, code_snippet=test_code_snippet)
    print(res)  # noqa: T201
