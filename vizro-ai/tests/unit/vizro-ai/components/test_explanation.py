import pytest
from langchain.llms.fake import FakeListLLM
from vizro_ai.components import GetCodeExplanation


@pytest.fixture
def fake_llm():
    # This is to simulate the response of LLM
    responses = [
        '{"business_insights": "The chart shows '
        "the composition of GDP in different continents. The horizontal line represents "
        'the average GDP across all continents.", "code_explanation": "This code groups the DataFrame by '
        "the 'continent' column and calculates the sum of the 'gdpPercap' column for each continent. It then creates "
        "a bar chart using Plotly Express. "
        'It also adds a horizontal line at the average GDP value. Finally, it returns the chart."}'
    ]
    return FakeListLLM(responses=responses)


@pytest.fixture
def code_snippet():
    code_snippet = """
    from vizro.models.types import capture
    import vizro.plotly.express as px
    import pandas as pd

    @capture('graph')
    def custom_chart(data_frame: pd.DataFrame = None):
        if data_frame is None:
            data_frame = pd.DataFrame()
        df = data_frame.groupby('continent')['gdpPercap'].sum().reset_index().rename(columns={'gdpPercap': 'total_gdp'})
        fig = px.bar(df, x='continent', y='total_gdp', color='continent', title='Composition of GDP in Continents')
        fig.add_hline(y=df['total_gdp'].mean(), line_dash='dash', line_color='red', annotation_text='Average GDP')
        return fig

    fig = custom_chart(data_frame=df)
    """
    return code_snippet


@pytest.fixture
def expected_business_insights():
    business_insights = (
        "The chart shows the composition of GDP in different continents. "
        "The horizontal line represents the average GDP across all continents."
    )
    return business_insights


@pytest.fixture
def expected_code_explanation():
    code_explanation = (
        "This code groups the DataFrame by the 'continent' column and calculates the sum of "
        "the 'gdpPercap' column for each continent. It then creates a bar chart using "
        "Plotly Express and Vizro. "
        "It also adds a horizontal line at the average GDP value. Finally, it returns the chart."
        "\n<br>**This customized chart can be directly used in a Vizro dashboard.** "
        "\nClick [custom chart docs]"
        "(https://vizro.readthedocs.io/en/stable/pages/user_guides/custom_charts/) "
        "for more information."
    )
    return code_explanation


@pytest.fixture
def loaded_response():
    loaded_response = {
        "business_insights": "The chart shows the composition of GDP in different continents. "
        "The horizontal line represents the average GDP across all continents.",
        "code_explanation": "This code groups the DataFrame by the 'continent' column and calculates the sum of "
        "the 'gdpPercap' column for each continent. It then creates a bar chart using "
        "Plotly Express. "
        "It also adds a horizontal line at the average GDP value. Finally, it returns the chart.",
    }
    return loaded_response


class TestCodeExplanationInstantiation:
    def test_instantiation(self):
        explanation = GetCodeExplanation(llm=fake_llm)
        assert explanation.llm == fake_llm

    def setup_method(self, fake_llm):
        self.get_code_explanation = GetCodeExplanation(llm=fake_llm)

    def test_pre_process(self, code_snippet):
        llm_kwargs, partial_vars = self.get_code_explanation._pre_process(code_snippet)
        expected_partial_vars = {"code_snippet": code_snippet}
        assert partial_vars == expected_partial_vars

    def test_post_process(self, loaded_response, expected_business_insights, expected_code_explanation):
        business_insights, code_explanation = self.get_code_explanation._post_process(loaded_response)
        assert business_insights == expected_business_insights
        assert code_explanation == expected_code_explanation


class TestChartSelection:
    def test_fake_response(self, code_snippet, fake_llm, expected_business_insights, expected_code_explanation):
        get_code_explanation = GetCodeExplanation(fake_llm)
        business_insights, code_explanation = get_code_explanation.run(
            chain_input="choose a best chart for describe the composition of gdp in continent, "
            "and horizontal line for avg gdp",
            code_snippet=code_snippet,
        )
        assert business_insights == expected_business_insights
        assert code_explanation == expected_code_explanation
