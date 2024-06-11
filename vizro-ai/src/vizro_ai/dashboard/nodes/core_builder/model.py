from typing import Union

try:
    from pydantic.v1 import BaseModel
except ImportError:  # pragma: no cov
    from pydantic import BaseModel
from typing import Dict, List
from langchain_core.prompts import ChatPromptTemplate


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


def get_model(
        query: str, 
        model, 
        result_model: BaseModel, 
        df_metadata: Dict[str, Dict[str, str]],
        ) -> BaseModel:
    model_component_chain = SINGLE_MODEL_PROMPT | model.with_structured_output(result_model)

    messages = [
        (
            "user",
            query,
        )
    ]

    res = model_component_chain.invoke({"message": messages, "df_metadata": df_metadata})
    return res
