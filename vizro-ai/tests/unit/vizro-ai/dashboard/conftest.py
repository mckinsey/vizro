from typing import Any

import pytest
import vizro.models as vm
from langchain.output_parsers import PydanticOutputParser
from langchain_community.llms.fake import FakeListLLM
from langchain_core.messages import HumanMessage


class MockStructuredOutputLLM(FakeListLLM):
    def bind_tools(self, tools: list[Any]):
        return super().bind(tools=tools)

    def with_structured_output(self, schema):
        llm = self
        output_parser = PydanticOutputParser(pydantic_object=schema)
        return llm | output_parser


@pytest.fixture
def fake_llm():
    response = ['{"text":"this is a card","href":""}']
    return MockStructuredOutputLLM(responses=response)


@pytest.fixture
def component_description():
    return "This is a card"


@pytest.fixture
def expected_card():
    return vm.Card(text="this is a card")


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


@pytest.fixture
def fake_llm_invalid():
    response = ['{"text":"this is a card", "href": "", "icon": "summary"}']
    return MockStructuredOutputLLM(responses=response)
