import pandas as pd
import pytest
from langchain.llms.fake import FakeListLLM
from vizro_ai.components import GetChartSelection


@pytest.fixture
def fake_llm():
    # This is to simulate the response of LLM
    response = ['{"chart_type": "bar"}']
    return FakeListLLM(responses=response)


class TestChartSelectionInstantiation:
    def test_instantiation(self):
        chart_selection = GetChartSelection(llm=fake_llm)
        assert chart_selection.llm == fake_llm

    def setup_method(self, fake_llm):
        self.get_chart_selection = GetChartSelection(llm=fake_llm)

    def test_pre_process(self):
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        llm_kwargs, partial_vars = self.get_chart_selection._pre_process(df)
        expected_partial_vars = {"df_schema": "A: int64\nB: int64", "df_head": df.head().to_markdown()}
        assert partial_vars == expected_partial_vars

    @pytest.mark.parametrize(
        "load_args, expected_chart_name",
        [
            ({"chart_type": "line"}, "line"),
            ({"chart_type": "bar"}, "bar"),
            ({"chart_type": ["line", "bar"]}, "line,bar"),
        ],
    )
    def test_post_process(self, load_args, expected_chart_name):
        chart_names = self.get_chart_selection._post_process(load_args)
        assert chart_names == expected_chart_name


class TestChartSelection:
    def test_fake_response(self, gapminder, fake_llm):
        get_chart_selection = GetChartSelection(fake_llm)
        target_chart = get_chart_selection.run(
            df=gapminder, chain_input="choose a best chart for describe the composition"
        )
        assert target_chart == "bar"
