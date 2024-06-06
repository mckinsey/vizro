from typing import Union

from langchain.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel
from pydantic.v1 import BaseModel as BaseModelV1
from typing import List
from langchain_core.prompts import ChatPromptTemplate


MODEL_PROMPT = (
    """
    Answer the user query. Remember to only respond with JSON and NOTHING else.\n{format_instructions}\n{query}\n
    These are the dataframes available to you:\n{cleaned_df_names}\n
    """
)
MODEL_REPROMPT = MODEL_PROMPT + "Pay special attention to the following error\n{validation_error}\n"


def get_model(
        query: str, 
        model, 
        result_model: Union[BaseModel, BaseModelV1], 
        cleaned_df_names: List[str],
        max_retry: int = 3,
        ) -> BaseModel:
    parser = PydanticOutputParser(pydantic_object=result_model)

    for i in range(max_retry):
        try:
            prompt = PromptTemplate(
                template=MODEL_PROMPT if i == 0 else MODEL_REPROMPT,
                input_variables=["query", "cleaned_df_names"],
                partial_variables={"format_instructions": parser.get_format_instructions()},
            )

            chain = prompt | model | parser

            res = (
                chain.invoke({"query": query, "cleaned_df_names": cleaned_df_names})
                if i == 0
                else chain.invoke({"query": query, "cleaned_df_names":cleaned_df_names, "validation_error": str(validation_error)})
            )
            return res
        except OutputParserException as e:
            validation_error = e
    return validation_error


SINGLE_MODEL_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a data assistant with expertise pydantic and a vizualization library named Vizro. \n
            Summarize the user \n
            question and response with instructed format. \n
            Here is the user question:""",
        ),
        ("placeholder", "{message}"),
    ]
)


def get_component_model(
        query: str, 
        model, 
        result_model: Union[BaseModel, BaseModelV1], 
        data_frame: str,
        max_retry: int = 3,
        ) -> BaseModel:
    model_component_chain = SINGLE_MODEL_PROMPT | model.with_structured_output(result_model)

    messages = [
        (
            "user",
            query,
        )
    ]

    res = model_component_chain.invoke({"message": messages})
    return res
