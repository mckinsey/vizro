try:
    from pydantic.v1 import BaseModel, Field, ValidationError
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, Field
from typing import Dict

from langchain_core.prompts import ChatPromptTemplate


class ProxyVizroBaseModel(BaseModel):
    id: str = Field(
        "",
        description="ID to identify model. Must be unique throughout the whole dashboard."
        "When no ID is chosen, ID will be automatically generated.",
    )


SINGLE_MODEL_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a data assistant with expertise pydantic and a vizualization library named Vizro. \n
            Summarize the user \n
            question and response with instructed format. \n
            This is the data you have access to: {df_metadata}\n
            Here is the user question:""",
        ),
        ("placeholder", "{message}"),
    ]
)


def _get_model(
    query: str,
    model,
    result_model: BaseModel,
    df_metadata: Dict[str, Dict[str, str]],
) -> BaseModel:
    vizro_model_chain = SINGLE_MODEL_PROMPT | model.with_structured_output(result_model)

    messages = [
        (
            "user",
            query,
        )
    ]

    res = vizro_model_chain.invoke({"message": messages, "df_metadata": df_metadata})

    # try:
    #     # This is most useful when the response is incomplete
    #     # https://api.python.langchain.com/en/latest/runnables/langchain_core.runnables.retry.RunnableRetry.html#langchain_core.runnables.retry.RunnableRetry.with_retry
    #     res = vizro_model_chain.with_retry(
    #         stop_after_attempt=2,
    #         retry_if_exception_type=(ValidationError,),
    #     ).invoke({"message": messages, "df_metadata": df_metadata})
    # except ValidationError:
    #     pass
    #     # res = ProxyVizroBaseModel(id="")

    return res
