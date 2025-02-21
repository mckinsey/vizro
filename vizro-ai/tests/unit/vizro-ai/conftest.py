"""Fixtures to be shared across several tests."""

from typing import Any

import pytest
import vizro.plotly.express as px
from langchain.output_parsers import PydanticOutputParser
from langchain_community.llms.fake import FakeListLLM


@pytest.fixture
def gapminder():
    return px.data.gapminder()


# TODO add more common fixtures here


class MockStructuredOutputLLM(FakeListLLM):
    def bind_tools(self, tools: list[Any]):
        return super().bind(tools=tools)

    def with_structured_output(self, schema, **kwargs):
        llm = self
        output_parser = PydanticOutputParser(pydantic_object=schema)
        return llm | output_parser


@pytest.fixture
def fake_llm():
    response = ['{"text":"this is a card","href":""}']
    return MockStructuredOutputLLM(responses=response)


@pytest.fixture
def fake_llm_card():
    response = ['{"text":"this is a card","href":""}']
    return MockStructuredOutputLLM(responses=response)


@pytest.fixture
def fake_llm_layout():
    response = ['{"grid":[[0,1]]}']
    return MockStructuredOutputLLM(responses=response)


@pytest.fixture
def fake_llm_filter():
    response = ['{"column": "a", "targets": ["bar_chart"]}']
    return MockStructuredOutputLLM(responses=response)


@pytest.fixture
def fake_llm_invalid():
    response = ['{"text":"this is a card", "href": "", "icon": "summary"}']
    return MockStructuredOutputLLM(responses=response)
