import pandas as pd
import pytest
from langchain_community.llms.fake import FakeListLLM
from vizro_ai.plot.components import GetVisualCode


@pytest.fixture
def chart_type():
    return "bar"


@pytest.fixture
def input_df():
    input_df = pd.DataFrame(
        {
            "contintent": ["Asia", "Asia", "America", "Europe", "Europe"],
            "country": ["China", "India", "US", "UK", "Germany"],
            "gdpPercap": [102, 110, 300, 200, 250],
        }
    )
    return input_df


@pytest.fixture
def df_schema():
    return "contintent: object\ncountry: object\ngdpPercap: int64"


@pytest.fixture
def df_sample():
    return """|    | contintent   | country   |   gdpPercap |
|---:|:-------------|:----------|------------:|
|  2 | America      | US        |         300 |
|  0 | Asia         | China     |         102 |
|  3 | Europe       | UK        |         200 |
|  4 | Europe       | Germany   |         250 |
|  2 | America      | US        |         300 |"""


@pytest.fixture
def df_code_1():
    return """import pandas as pd
df = df.groupby('continent')['gdpPercap'].sum().reset_index()"""


@pytest.fixture
def output_visual_code_LLM_1():
    return """import plotly.express as px

fig = px.bar(df, x='continent', y='total_gdpPercap', title='Composition of GDP by Continent')
fig.add_hline(y=df['total_gdpPercap'].mean(), line_dash='dash', line_color='red', annotation_text='Average GDP')
fig.show()"""


@pytest.fixture
def expected_final_output_1():
    return """import vizro.plotly.express as px
import pandas as pd
df = df.groupby('continent')['gdpPercap'].sum().reset_index()

fig = px.bar(df, x='continent', y='total_gdpPercap', title='Composition of GDP by Continent')
fig.add_hline(y=df['total_gdpPercap'].mean(), line_dash='dash', line_color='red', annotation_text='Average GDP')
fig.show()"""


@pytest.fixture
def df_code_2():
    return """import pandas as pd
df = df.query('year == 2007').groupby('continent')['pop'].sum().reset_index(name='total_pop')"""


@pytest.fixture
def output_visual_code_LLM_2():
    return """import plotly.graph_objects as go

# Create a bar chart
fig = go.Figure(data=[go.Bar(x=df['continent'], y=df['total_pop'])])

# Update the layout
fig.update_layout(title='Increase in Population by Continent', xaxis_title='Continent', yaxis_title='Total Population')

# Show the chart
fig.show()"""


@pytest.fixture
def expected_final_output_2():
    return """import plotly.graph_objects as go
import pandas as pd
df = df.query('year == 2007').groupby('continent')['pop'].sum().reset_index(name='total_pop')

# Create a bar chart
fig = go.Figure(data=[go.Bar(x=df['continent'], y=df['total_pop'])])

# Update the layout
fig.update_layout(title='Increase in Population by Continent', xaxis_title='Continent', yaxis_title='Total Population')

# Show the chart
fig.show()"""


@pytest.fixture
def fake_llm(output_visual_code_LLM_1):
    """Simulate the response of LLM."""
    response = ['{{"visual_code": "{}"}}'.format(output_visual_code_LLM_1)]
    return FakeListLLM(responses=response)


class TestGetVisualCodeInstantiation:
    def test_instantiation(self):
        chart_selection = GetVisualCode(llm=fake_llm)
        assert chart_selection.llm == fake_llm

    def setup_method(self, fake_llm):
        self.get_visual_code = GetVisualCode(llm=fake_llm)

    def test_pre_process(self, chart_type, input_df, df_code_1, df_schema, df_sample):
        _, partial_vars = self.get_visual_code._pre_process(chart_type=chart_type, df_code=df_code_1, df=input_df)
        assert partial_vars == {
            "chart_type": chart_type,
            "df_code": df_code_1,
            "df_schema": df_schema,
            "df_sample": df_sample,
        }

    @pytest.mark.parametrize(
        "input,output,df_code",
        [
            ("output_visual_code_LLM_1", "expected_final_output_1", "df_code_1"),
            ("output_visual_code_LLM_2", "expected_final_output_2", "df_code_2"),
        ],
    )
    def test_post_process(self, input, output, df_code, request):
        input = request.getfixturevalue(input)
        output = request.getfixturevalue(output)
        df_code = request.getfixturevalue(df_code)
        loaded_args = {"visual_code": input}
        processed_code = self.get_visual_code._post_process(loaded_args, df_code=df_code)
        assert processed_code == output


class TestGetVisualCodeRun:
    def test_fake_run(  # noqa: PLR0913
        self,
        fake_llm,
        output_visual_code_LLM_1,
        expected_final_output_1,
        df_code_1,
        chart_type,
        input_df,
    ):
        get_visual_code = GetVisualCode(fake_llm)
        processed_code = get_visual_code.run(
            chain_input=output_visual_code_LLM_1, df_code=df_code_1, chart_type=chart_type, df=input_df
        )
        assert processed_code == expected_final_output_1
