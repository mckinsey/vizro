from typing import Any, List

import pandas as pd
import pytest
from langchain.output_parsers import PydanticOutputParser
from langchain_community.llms.fake import FakeListLLM
from vizro_ai.dashboard.response_models.components import ComponentPlan
from vizro_ai.dashboard.response_models.layout import LayoutPlan
from vizro_ai.dashboard.response_models.page import PagePlanner
from vizro_ai.dashboard.utils import DfMetadata, AllDfMetadata


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
def fake_llm_layout():
    response = ['{"grid":[[0,1]]}']
    return FakeListLLM(responses=response)


@pytest.fixture
def df_cols():
    return ["continent", "country", "population", "gdp"]


@pytest.fixture
def df_schema():
    return {"continent": "object", "country": "object", "population": "int64", "gdp": "int64"}


@pytest.fixture
def controllable_components():
    return ["gdp_chart"]


@pytest.fixture
def component_description():
    return "This is a card"


@pytest.fixture
def grid_invalid_rows():
    return [[0, 0, 0], [1, 1, 1], [2, 2]]


@pytest.fixture
def grid_invalid_values():
    return [[3, 3, 3], [1, 1, 1], [2, 2, 2]]


@pytest.fixture
def layout_description():
    return "The layout of this page should use `grid=[[0,1]]`"


@pytest.fixture
def layout_description_invalid():
    return "The layout of this page should use `grid=[[]]`"


@pytest.fixture
def filter_prompt():
    return """
        Create a filter from the following instructions: Filter the world demographic table by continent.
        Do not make up things that are optional and DO NOT configure actions, action triggers or action chains.
        If no options are specified, leave them out."""


@pytest.fixture
def fake_llm_filter():
    response = ['{"column": "a", "targets": ["gdp_chart"]}']
    return FakeListLLM(responses=response)


@pytest.fixture
def df_metadata():
    df_metadata = AllDfMetadata({})
    df_metadata.all_df_metadata["gdp_chart"] = DfMetadata(
        df_schema={"a": "int64", "b": "int64"},
        df=pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": [4, 5, 6, 7, 8]}),
        df_sample=pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": [4, 5, 6, 7, 8]}),
    )
    return df_metadata


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
def component_card_2():
    return ComponentPlan(
        component_type="Card",
        component_description="This is a second ard",
        component_id="card_2",
        page_id="page_1",
        df_name="N/A",
    )


@pytest.fixture
def page_plan(component_card):
    return PagePlanner(
        title="Test Page",
        components_plan=[component_card],
        controls_plan=[],
        layout_plan=None,
        page_id="page_1"
    )


@pytest.fixture
def page_plan_2_components(component_card, component_card_2):
    return PagePlanner(
        page_id="page_2_components",
        title="Test Page",
        components_plan=[component_card, component_card_2],
        controls_plan=[],
        layout_plan=LayoutPlan(
            layout_description="Create a layout with a card on the left and a card on the right.",
            layout_grid_template_areas=["card_1", "card_2"],
        ),
    )
