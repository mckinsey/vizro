import pytest
from langchain.llms.fake import FakeListLLM
from vizro_ai.components import GetCustomChart


@pytest.fixture
def output_visual_component_1():
    return """import vizro.plotly.express as px
import pandas as pd

df = df.groupby('continent')['gdpPercap'].sum().reset_index().rename(columns={'gdpPercap': 'total_gdp'})
fig = px.bar(df, x='continent', y='total_gdp', color='continent', title='Composition of GDP in Continents')
fig.add_hline(y=df['total_gdp'].mean(), line_dash='dash', line_color='red', annotation_text='Average GDP')
fig.show()"""


@pytest.fixture
def output_custom_chart_LLM_1():
    return """import vizro.plotly.express as px
import pandas as pd

def custom_chart(data_frame):
    df = data_frame.groupby('continent')['gdpPercap'].sum().reset_index().rename(columns={'gdpPercap': 'total_gdp'})
    fig = px.bar(df, x='continent', y='total_gdp', color='continent', title='Composition of GDP in Continents')
    fig.add_hline(y=df['total_gdp'].mean(), line_dash='dash', line_color='red', annotation_text='Average GDP')
    return fig"""


@pytest.fixture
def expected_final_output_1():
    return """from vizro.models.types import capture
import vizro.plotly.express as px
import pandas as pd

@capture('graph')
def custom_chart(data_frame):
    df = data_frame.groupby('continent')['gdpPercap'].sum().reset_index().rename(columns={'gdpPercap': 'total_gdp'})
    fig = px.bar(df, x='continent', y='total_gdp', color='continent', title='Composition of GDP in Continents')
    fig.add_hline(y=df['total_gdp'].mean(), line_dash='dash', line_color='red', annotation_text='Average GDP')
    return fig

fig = custom_chart(data_frame=df)"""


@pytest.fixture
def output_custom_chart_LLM_2():
    return """
import vizro.plotly.express as px
import pandas as pd
def custom_chart(data_frame):
    df = data_frame.groupby('continent')['gdpPercap'].sum().reset_index().rename(columns={'gdpPercap': 'total_gdp'})
    fig = px.bar(df, x='continent', y='total_gdp', color='continent', title='Composition of GDP in Continents')
    fig.add_hline(y=df['total_gdp'].mean(), line_dash='dash', line_color='red', annotation_text='Average GDP')
    return fig"""


@pytest.fixture
def expected_final_output_2():
    return """from vizro.models.types import capture
import vizro.plotly.express as px
import pandas as pd
@capture('graph')
def custom_chart(data_frame):
    df = data_frame.groupby('continent')['gdpPercap'].sum().reset_index().rename(columns={'gdpPercap': 'total_gdp'})
    fig = px.bar(df, x='continent', y='total_gdp', color='continent', title='Composition of GDP in Continents')
    fig.add_hline(y=df['total_gdp'].mean(), line_dash='dash', line_color='red', annotation_text='Average GDP')
    return fig

fig = custom_chart(data_frame=df)"""


@pytest.fixture
def output_custom_chart_LLM_3():
    return """import vizro.plotly.express as px
import pandas as pd

def some_chart_name(data_frame):
    df = data_frame.groupby('continent')['gdpPercap'].sum().reset_index().rename(columns={'gdpPercap': 'total_gdp'})
    fig = px.bar(df, x='continent', y='total_gdp', color='continent', title='Composition of GDP in Continents')
    fig.add_hline(y=df['total_gdp'].mean(), line_dash='dash', line_color='red', annotation_text='Average GDP')
    return fig"""


@pytest.fixture
def fake_llm(output_custom_chart_LLM_1):
    """Simulate the response of LLM."""
    response = ['{{"custom_chart_code": "{}"}}'.format(output_custom_chart_LLM_1)]
    return FakeListLLM(responses=response)


class TestGetCustomChartMethods:
    def test_instantiation(self):
        """Test initialization of GetCustomChart."""
        get_custom_chart = GetCustomChart(llm=fake_llm)
        assert get_custom_chart.llm == fake_llm

    def setup_method(self, fake_llm):
        self.get_custom_chart = GetCustomChart(llm=fake_llm)

    def test_pre_process(self):
        llm_kwargs, partial_vars = self.get_custom_chart._pre_process()
        assert partial_vars == {}
        assert isinstance(llm_kwargs, dict)

    @pytest.mark.parametrize(
        "input,output",
        [
            ("output_custom_chart_LLM_1", "expected_final_output_1"),
            ("output_custom_chart_LLM_2", "expected_final_output_2"),
        ],
    )
    def test_post_process(self, input, output, request):
        input = request.getfixturevalue(input)
        output = request.getfixturevalue(output)
        loaded_args = {"custom_chart_code": input}
        processed_code = self.get_custom_chart._post_process(loaded_args)
        assert processed_code == output

    def test_post_process_fail(self, output_custom_chart_LLM_3):
        loaded_args = {"custom_chart_code": output_custom_chart_LLM_3}
        with pytest.raises(ValueError, match="def custom_chart is not added correctly by the LLM. Try again."):
            self.get_custom_chart._post_process(loaded_args)


class TestGetCustomChartRun:
    def test_fake_run(self, fake_llm, expected_final_output_1):
        get_custom_chart = GetCustomChart(fake_llm)
        # Note that the chain input is not used in this component as we fake the LLM response
        processed_code = get_custom_chart.run(chain_input="XXX")
        assert processed_code == expected_final_output_1
