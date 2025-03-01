"""Contains the _get_pydantic_model for the Vizro AI dashboard."""

# ruff: noqa: F821

import logging
from inspect import signature
from typing import Any, Optional

import plotly.express as px
import vizro.models as vm
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

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


def _get_pydantic_model(
    query: str,
    llm_model: BaseChatModel,
    response_model: BaseModel,
    df_info: Optional[Any] = None,  # TODO: this should potentially not be part of this function.
    max_retry: int = 2,
) -> BaseModel:
    # TODO: fix typing similar to instructor library, ie the return type should be the same as response_model
    # At the very least it should include the string type of the validation error
    """Get the pydantic output from the LLM model with retry logic."""
    for attempt in range(max_retry):
        attempt_is_retry = attempt > 0
        prompt = _create_prompt(retry=attempt_is_retry)
        message_content = _create_message_content(
            query, df_info, str(last_validation_error) if attempt_is_retry else None, retry=attempt_is_retry
        )

        try:
            kwargs = {}
            # Only pass `method` parameter if the model's with_structured_output accepts it
            # This is determined by checking the signature of the method
            # By the time this code written, the `method` parameter is supported by
            # model providers like OpenAI, MistralAI, VertexAI, etc.
            try:
                sig = signature(llm_model.with_structured_output)
                if "method" in sig.parameters:
                    kwargs["method"] = "function_calling"  # method 'json_schema' does not work with `pattern` in Field
            except (ValueError, AttributeError):
                pass

            pydantic_llm = prompt | llm_model.with_structured_output(response_model, **kwargs)
            return pydantic_llm.invoke(message_content)

        except ValidationError as validation_error:
            last_validation_error = validation_error
    # TODO: should this be shifted to logging so that that one can control what output gets shown (e.g. in public demos)
    raise last_validation_error


if __name__ == "__main__":
    import plotly.express as px
    import vizro.models as vm

    from vizro_ai._llm_models import _get_llm_model
    from vizro_ai.plot._response_models import ChartPlanStatic

    llm = _get_llm_model()

    import os

    from langchain_mistralai import ChatMistralAI

    llm = ChatMistralAI(
        name="codestral-latest",
        temperature=0,
        max_retries=2,
        endpoint=os.environ.get("MISTRAL_BASE_URL"),
        mistral_api_key=os.environ.get("ANTHROPIC_API_KEY"),
        # other params...
    )

    # Easy
    component_description = "Create a card with the following content: 'Hello, world!'"
    res = _get_pydantic_model(query=component_description, llm_model=llm, response_model=vm.Card)
    print(res.__repr__())  # noqa: T201
    print(type(res))  # noqa: T201

    # Harder
    df = px.data.gapminder().sample(5).to_markdown()
    component_description2 = "the trend of gdp over years in the US"
    res2 = _get_pydantic_model(query=component_description2, df_info=df, llm_model=llm, response_model=ChartPlanStatic)
    print(res2.__repr__())  # noqa: T201
    print(type(res2))  # noqa: T201
