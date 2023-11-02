import re

import pandas as pd
import pytest
from langchain.llms.fake import FakeListLLM
from vizro_ai.components import GetDataFrameCraft


def dataframe_code():
    return """
            data_frame = data_frame.groupby('continent')['gdpPercap'].sum().reset_index()
            data_frame = data_frame.rename(columns={'gdpPercap': 'total_gdp'})
            data_frame.plot(kind='bar', x='continent', y='total_gdp', color='skyblue', legend=False)"""


@pytest.fixture
def fake_llm():
    dataframe_code_before_postprocess = re.sub(
        r"[\x00-\x1f]", lambda m: "\\u{:04x}".format(ord(m.group(0))), dataframe_code()
    )
    response = ['{{"dataframe_code": "{}"}}'.format(dataframe_code_before_postprocess)]
    return FakeListLLM(responses=response)


@pytest.fixture
def input_df():
    input_df = pd.DataFrame(
        {
            "contintent": ["Asia", "Asia", "America", "Europe"],
            "country": ["China", "India", "US", "UK"],
            "gdpPercap": [102, 110, 300, 200],
        }
    )
    return input_df


class TestDataFrameCraftMethods:
    def test_instantiation(self):
        dataframe_craft = GetDataFrameCraft(llm=fake_llm)
        assert dataframe_craft.llm == fake_llm

    def setup_method(self, fake_llm):
        self.get_dataframe_craft = GetDataFrameCraft(llm=fake_llm)

    def test_pre_process(self, input_df):
        llm_kwargs_to_use, partial_vars = self.get_dataframe_craft._pre_process(df=input_df)
        expected_partial_vars = {
            "df_schema": "contintent: object\ncountry: object\ngdpPercap: int64",
            "df_head": input_df.head().to_markdown(),
        }
        assert partial_vars == expected_partial_vars

    @pytest.mark.parametrize(
        "code_string, expected_code_string",
        [
            (
                "df = pd.DataFrame({'test1': [1, 2], 'test2': [3, 4]})",
                "import pandas as pd\ndf = pd.DataFrame({'test1': [1, 2], 'test2': [3, 4]}).reset_index()",
            ),
            (
                "df = pd.DataFrame({'test1': [1, 2], 'test2': [3, 4]}).reset_index()",
                "import pandas as pd\ndf = pd.DataFrame({'test1': [1, 2], 'test2': [3, 4]}).reset_index()",
            ),
            (
                "data_frame = pd.DataFrame({'test1': [1, 1, 2], 'test2': [3, 4, 5]})\n"
                "data_frame = data_frame.groupby('test1')['test2'].sum()",
                "import pandas as pd\ndata_frame = pd.DataFrame({'test1': [1, 1, 2], 'test2': [3, 4, 5]})\n"
                "df = data_frame.groupby('test1')['test2'].sum().reset_index()",
            ),
            (
                "import pandas as pd\n"
                "df = pd.DataFrame({'test1': [1, 2], 'test2': [3, 4]}).plot(kind='bar', x='test1', y='test2')",
                "import pandas as pd\ndf = pd.DataFrame({'test1': [1, 2], 'test2': [3, 4]}).reset_index()",
            ),
        ],
    )
    def test_post_process(self, code_string, expected_code_string, input_df):
        load_args = {"dataframe_code": code_string}
        df_code = self.get_dataframe_craft._post_process(load_args, input_df)

        assert df_code == expected_code_string


class TestDataFrameCraftResponse:
    def test_fake_response(self, input_df, fake_llm):
        get_dataframe_craft = GetDataFrameCraft(fake_llm)
        df_code = get_dataframe_craft.run(
            chain_input="choose a best chart for describe the composition of gdp in continent, "
            "and horizontal line for avg gdp",
            df=input_df,
        )
        assert (
            df_code == "import pandas as pd\n            "
            "data_frame = data_frame.groupby('continent')['gdpPercap'].sum().reset_index()\n            "
            "data_frame = data_frame.rename(columns={'gdpPercap': 'total_gdp'})\n"
            "df =             data_frame.reset_index()"
        )
