from typing import List, Union, Literal
import os

from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field, validator
from langchain_openai import ChatOpenAI
from langchain_core.exceptions import OutputParserException
from pydantic.v1 import BaseModel as BaseModelV1

MODEL_PROMPT = "Answer the user query. Remember to only respond with JSON and NOTHING else.\n{format_instructions}\n{query}\n"
MODEL_REPROMPT = MODEL_PROMPT + "Pay special attention to the following error\n{validation_error}\n"

def get_model(query: str, model, result_model: Union[BaseModel, BaseModelV1], max_retry: int = 3) -> BaseModel:
    parser = PydanticOutputParser(pydantic_object=result_model)

    for i in range(max_retry):
        try:
            prompt = PromptTemplate(
                template=MODEL_PROMPT if i == 0 else MODEL_REPROMPT,
                input_variables=["query"],
                partial_variables={"format_instructions": parser.get_format_instructions()},
            )

            chain = prompt | model | parser

            res = chain.invoke({"query": query}) if i == 0 else chain.invoke(
                {"query": query, "validation_error": str(validation_error)})
            return res
        except OutputParserException as e:
            validation_error = e
    return validation_error


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    import vizro.models as vm

    query = "I want a card with some random text that starts with quack"
    model = ChatOpenAI()
    result_model = vm.Card

    res = get_model(query, model, result_model)
    print(repr(res))