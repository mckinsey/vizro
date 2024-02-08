import pytest
from langchain.llms.fake import FakeListLLM
from vizro_ai.components import GetDebugger


@pytest.fixture
def fake_llm():
    """Simulate the response of LLM."""
    response = ['{{"fixed_code": "{}"}}'.format("print(df[['country', 'continent']])")]
    return FakeListLLM(responses=response)


@pytest.fixture
def fake_code_snippet():
    return "print(df['country', 'continent'])"


@pytest.fixture
def fake_error_msg():
    return "KeyError: ('country', 'continent')"


class TestCodeValidationInstantiation:
    def test_instantiation(self):
        chart_selection = GetDebugger(llm=fake_llm)
        assert chart_selection.llm == fake_llm

    def setup_method(self, fake_llm):
        self.get_debugger = GetDebugger(llm=fake_llm)

    def test_pre_process(self):
        llm_kwargs, partial_vars = self.get_debugger._pre_process(fake_code_snippet)
        assert partial_vars == {"code_snippet": fake_code_snippet}

    @pytest.mark.parametrize(
        "load_args, expected_fixed_code",
        [
            (
                {"fixed_code": "print('unit test for expected fixed code')"},
                "print('unit test for expected fixed code')",
            ),
            (
                {"fixed_code": "import pandas as pd\n" "\n" "print(df[['country', 'continent']])\n"},
                "import pandas as pd\n" "\n" "print(df[['country', 'continent']])\n",
            ),
        ],
    )
    def test_post_process(self, load_args, expected_fixed_code):
        fixed_code = self.get_debugger._post_process(load_args)
        assert fixed_code == expected_fixed_code


class TestChartSelection:
    def test_fake_response(self, fake_llm, fake_code_snippet, fake_error_msg):
        get_debugger = GetDebugger(fake_llm)
        fixed_code = get_debugger.run(chain_input=fake_error_msg, code_snippet=fake_code_snippet)
        assert fixed_code == "print(df[['country', 'continent']])"
