from typing import Any, List

import pytest
from langchain.output_parsers import PydanticOutputParser
from langchain_community.llms.fake import FakeListLLM
from langchain_core.messages import HumanMessage


class FakeListLLM(FakeListLLM):
    def bind_tools(self, tools: List[Any]):
        return super().bind(tools=tools)

    def with_structured_output(self, schema):
        llm = self
        output_parser = PydanticOutputParser(pydantic_object=schema)
        return llm | output_parser


@pytest.fixture
def fake_llm():
    response = ['{"text":"this is a card","href":""}']
    return FakeListLLM(responses=response)


@pytest.fixture
def component_description():
    return "This is a card"


@pytest.fixture
def query():
    return "I need a page with one card saying: Simple card."


@pytest.fixture
def message_output_valid():
    return {"message": [HumanMessage(content="I need a page with one card saying: Simple card.")], "df_info": None}


@pytest.fixture
def message_output_error():
    return {
        "message": [HumanMessage(content="I need a page with one card saying: Simple card.")],
        "df_info": None,
        "validation_error": "ValidationError",
    }
