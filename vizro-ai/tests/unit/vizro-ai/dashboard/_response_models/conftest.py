import pandas as pd
import pytest
import vizro.models as vm

from vizro_ai.dashboard._response_models.components import ComponentPlan
from vizro_ai.dashboard._response_models.page import PagePlan
from vizro_ai.dashboard.utils import AllDfMetadata, DfMetadata
from vizro_ai.plot._response_models import ChartPlan


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
    df_metadata = AllDfMetadata()
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
    return ChartPlan(
        chart_type="scatter",
        imports=["import plotly.express as px\nimport pandas as pd"],
        chart_code="""def custom_chart(data_frame):
    fig = px.scatter(
            data_frame=data_frame,
            x="a",
            y="b",
        )

    return fig""",
        chart_insights="business_insights",
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
