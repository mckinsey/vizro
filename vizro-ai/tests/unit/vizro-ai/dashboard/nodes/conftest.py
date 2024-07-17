from typing import Any, List

import pytest
from langchain.output_parsers import PydanticOutputParser
from langchain_community.llms.fake import FakeListLLM
from vizro_ai.dashboard.response_models.components import ComponentPlan


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
def component_card():
    return ComponentPlan(
        component_type="Card",
        component_description="This is a card",
        component_id="card_1",
        page_id="page_1",
        df_name="N/A",
    )


@pytest.fixture
def df_cols():
    return ["continent", "country", "population", "gdp"]


@pytest.fixture
def available_components():
    return ["gdp_chart"]


@pytest.fixture
def component_description():
    return "This is a card"
