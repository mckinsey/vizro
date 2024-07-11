"""Contains the _get_proxy_model for the Vizro AI dashboard."""

# ruff: noqa: F821
try:
    from pydantic.v1 import BaseModel, ValidationError
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, ValidationError

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from vizro_ai.dashboard.utils import DfMetadata

SINGLE_MODEL_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a data assistant with expertise pydantic and a visualization library named Vizro. \n
            Summarize the user \n
            question and response with instructed format. \n
            This is the data you have access to: \n{df_metadata}\n
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
            Summarize the user \n
            question and response with instructed format. \n
            This is the data you have access to: \n{df_metadata}\n
            Pay special attention to the following error: \n{validation_error}\n
            Here is the user question:""",
        ),
        ("placeholder", "{message}"),
    ]
)


def _get_proxy_model(
    query: str,
    llm_model: BaseChatModel,
    result_model: BaseModel,
    df_metadata: DfMetadata,
    max_retry: int = 2,
) -> BaseModel:
    for i in range(max_retry):
        try:
            prompt = SINGLE_MODEL_PROMPT if i == 0 else MODEL_REPROMPT
            vizro_model_chain = prompt | llm_model.with_structured_output(result_model)

            user_requirements = [HumanMessage(content=query)]

            res = (
                vizro_model_chain.invoke({"message": user_requirements, "df_metadata": df_metadata})
                if i == 0
                else vizro_model_chain.invoke(
                    {
                        "message": user_requirements,
                        "df_metadata": df_metadata,
                        "validation_error": str(validation_error),
                    }
                )
            )
            return res
        except ValidationError as e:
            validation_error = e
    return validation_error
