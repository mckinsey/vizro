"""Contains the _get_structured_output for the Vizro AI dashboard."""

# ruff: noqa: F821
try:
    from pydantic.v1 import BaseModel, ValidationError
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, ValidationError

from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate

SINGLE_MODEL_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a data assistant with expertise pydantic and a visualization library named Vizro. \n
            Summarize the user request and response with instructed format. \n
            This is the data you have access to: \n{df_info}\n
            Here is the user question:""",
        ),
        ("placeholder", "{message}"),
    ]
)

MODEL_REPROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a data assistant with expertise pydantic and a visualization library named Vizro. \n
            Summarize the user request and response with instructed format. \n
            This is the data you have access to: \n{df_info}\n
            Pay special attention to the following error: \n{validation_error}\n
            Here is the user question:""",
        ),
        ("placeholder", "{message}"),
    ]
)


def _get_structured_output(
    query: str,
    llm_model: BaseChatModel,
    result_model: BaseModel,
    df_info: Any = None,
    max_retry: int = 2,
) -> BaseModel:
    for i in range(max_retry):
        try:
            prompt = SINGLE_MODEL_PROMPT if i == 0 else MODEL_REPROMPT
            vizro_model_chain = prompt | llm_model.with_structured_output(result_model)

            user_requirements = [HumanMessage(content=query)]

            res = (
                vizro_model_chain.invoke({"message": user_requirements, "df_info": df_info})
                if i == 0
                else vizro_model_chain.invoke(
                    {
                        "message": user_requirements,
                        "df_info": df_info,
                        "validation_error": str(validation_error),
                    }
                )
            )
            return res
        except ValidationError as e:
            validation_error = e
    return validation_error
