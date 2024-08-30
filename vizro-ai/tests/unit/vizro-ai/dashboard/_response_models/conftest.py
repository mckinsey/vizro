from typing import Any, List

import pandas as pd
import pytest
import vizro.models as vm
import vizro.plotly.express as px
from langchain.output_parsers import PydanticOutputParser
from langchain_community.llms.fake import FakeListLLM
from vizro_ai.dashboard._response_models.components import ComponentPlan
from vizro_ai.dashboard._response_models.page import PagePlan
from vizro_ai.dashboard.utils import AllDfMetadata, DfMetadata
from vizro_ai.utils.helper import PlotOutputs


class MockStructuredOutputLLM(FakeListLLM):
    def bind_tools(self, tools: List[Any]):
        return super().bind(tools=tools)

    def with_structured_output(self, schema):
        llm = self
        output_parser = PydanticOutputParser(pydantic_object=schema)
        return llm | output_parser


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
def controllable_components():
    return ["bar_chart"]


@pytest.fixture
def layout_description():
    return "The layout of this page should use `grid=[[0,1]]`"


@pytest.fixture
def df():
    return pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": [4, 5, 6, 7, 8]})


@pytest.fixture
def df_cols():
    return ["a", "b"]


@pytest.fixture
def df_sample(df):
    return df.sample(5, replace=True, random_state=19)


@pytest.fixture
def df_schema():
    return {"a": "int64", "b": "int64"}


@pytest.fixture
def df_metadata(df, df_schema, df_sample):
    df_metadata = AllDfMetadata({})
    df_metadata.all_df_metadata["bar_chart"] = DfMetadata(
        df_schema=df_schema,
        df=df,
        df_sample=df_sample,
    )
    return df_metadata


@pytest.fixture
def component_plan_card():
    return ComponentPlan(
        component_type="Card",
        component_description="This is a card",
        component_id="card_1",
        df_name="N/A",
    )


@pytest.fixture
def component_plan_graph():
    return ComponentPlan(
        component_type="Graph",
        component_description="Scatter chart with x-axis as 'a' and y-axis as 'b'",
        component_id="graph_1",
        df_name="bar_chart",
    )


@pytest.fixture
def component_plan_ag_grid():
    return ComponentPlan(
        component_type="AgGrid",
        component_description="Ag grid showing columns 'a' and 'b' of dataframe",
        component_id="ag_grid_1",
        df_name="bar_chart",
    )


@pytest.fixture
def mock_vizro_ai_return(df):
    return PlotOutputs(
        code="""
from vizro.models.types import capture
import vizro.plotly.express as px
import pandas as pd

@capture('graph')
def custom_chart(data_frame=None):
    scatter_df = data_frame[['lifeExp', 'gdpPercap', 'continent', 'country']]
    scatter_df.reset_index(drop=True, inplace=True)

    fig = px.scatter(
        scatter_df,
        x='gdpPercap',
        y='lifeExp',
        title='Life Expectancy vs. GDP per Capita by Country',
    )

    return fig

fig = custom_chart(data_frame=df)
""",
        figure=px.scatter(
            data_frame=df,
            x="a",
            y="b",
        ),
        business_insights="business_insights",
        code_explanation="code_explanation",
    )


@pytest.fixture
def component_card_2():
    return ComponentPlan(
        component_type="Card",
        component_description="This is a second card",
        component_id="card_2",
        df_name="N/A",
    )


@pytest.fixture
def page_plan(component_plan_card):
    return PagePlan(title="Test Page", components_plan=[component_plan_card], controls_plan=[], layout_plan=None)


@pytest.fixture
def filter_prompt():
    return """
        Create a filter from the following instructions: Filter the bar chart by column `a`.
        Do not make up things that are optional and DO NOT configure actions, action triggers or action chains.
        If no options are specified, leave them out."""


@pytest.fixture
def layout():
    return vm.Layout(grid=[[0, 1]])


@pytest.fixture
def expected_filter():
    return vm.Filter(targets=["bar_chart"], column="a")
