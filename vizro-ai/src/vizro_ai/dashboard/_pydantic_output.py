"""Contains the _get_pydantic_output for the Vizro AI dashboard."""

# ruff: noqa: F821

try:
    from pydantic.v1 import BaseModel, ValidationError
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, ValidationError

from typing import Any, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate

BASE_PROMPT = """
You are a front-end developer with expertise in Plotly, Dash, and the visualization library named Vizro.
Your goal is to summarize the given specifications into the given Pydantic schema.
IMPORTANT: Please always output your response by using a tool.

This is the task context:
{df_info}

Additional information:
{additional_info}

Here is the user request:
"""


def _create_prompt_template(additional_info: str) -> ChatPromptTemplate:
    """Create the ChatPromptTemplate from the base prompt and additional info."""
    return ChatPromptTemplate.from_messages(
        [
            ("system", BASE_PROMPT.format(df_info="{df_info}", additional_info=additional_info)),
            ("placeholder", "{message}"),
        ]
    )


SINGLE_MODEL_PROMPT = _create_prompt_template("")
MODEL_REPROMPT = _create_prompt_template("Pay special attention to the following error: {validation_error}")


def _create_prompt(retry: bool = False) -> ChatPromptTemplate:
    """Create the prompt message for the LLM model."""
    return MODEL_REPROMPT if retry else SINGLE_MODEL_PROMPT


def _create_message_content(
    query: str, df_info: Any, validation_error: Optional[str] = None, retry: bool = False
) -> dict:
    """Create the message content for the LLM model."""
    message_content = {"message": [HumanMessage(content=query)], "df_info": df_info}

    if retry:
        message_content["validation_error"] = validation_error

    return message_content


def _get_pydantic_output(
    query: str,
    llm_model: BaseChatModel,
    response_model: BaseModel,
    df_info: Optional[Any] = None,
    max_retry: int = 2,
) -> BaseModel:
    """Get the pydantic output from the LLM model with retry logic."""
    for attempt in range(max_retry):
        try:
            prompt = _create_prompt(retry=(attempt > 0))
            message_content = _create_message_content(
                query, df_info, str(last_validation_error) if attempt > 0 else None, retry=(attempt > 0)
            )
            pydantic_llm = prompt | llm_model.with_structured_output(response_model)
            res = pydantic_llm.invoke(message_content)
            return res
        except ValidationError as validation_error:
            last_validation_error = validation_error
    raise last_validation_error


if __name__ == "__main__":
    import vizro.models as vm
    from vizro_ai.chains._llm_models import _get_llm_model

    model = _get_llm_model()
    component_description = "Create a card with the following content: 'Hello, world!'"
    res = _get_pydantic_output(query=component_description, llm_model=model, response_model=vm.Card)
    print(res)  # noqa: T201
