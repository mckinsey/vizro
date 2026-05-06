import json

import plotly.express as px
import pytest
from tests.integration.llm.helpers import llm_judge, wait_for_full_chatbot_answer
from tests.integration.llm.question_and_reference import FRANCE_CAPITAL


@pytest.mark.parametrize(
    "question, reference",
    [
        (FRANCE_CAPITAL["question"], FRANCE_CAPITAL["reference"]),
    ],
    ids=["Capital of France"],
)
def test_openai_streaming_chat(page, chat_app_url, question, reference):
    page.goto(f"{chat_app_url}/example-questions")
    page.locator("#example_chat-example-questions-button").click()
    page.locator('div[class*="chat-example-menu-dropdown"] button:nth-of-type(1)').click()
    page.locator("#example_chat-send-button").click()
    answer_selector = (
        "#example_chat-rendered-messages "
        ".chat-message-wrapper:nth-of-type(2) "
        'div[class="chat-message-bubble chat-assistant-message"] '
        'div[class="assistant-markdown "]'
    )
    answer = wait_for_full_chatbot_answer(page, answer_selector)
    judge_result = json.loads(llm_judge(question, answer, reference=reference))
    print(f"Chatbot answer:\n{answer} \n\nLLM as a judge result:\n{judge_result}")  # noqa
    assert judge_result["score"] >= 7, f"Low score ({judge_result['score']}): {judge_result['reason']}"


def test_chat_with_upload(page, chat_app_url):
    df = px.data.stocks()
    df.to_csv("tests/integration/llm/stocks.csv", index=False)
    page.goto(f"{chat_app_url}/examples--upload")
    page.locator("input[type='file']").set_input_files("tests/integration/llm/stocks.csv")
    page.locator("button[id*='example-questions-button']").click()
    page.locator('div[class*="chat-example-menu-dropdown"] button:nth-of-type(1)').click()
    page.locator("button[id*='send-button']").click()
    plot_answer_selector = page.locator(
        "div[id*='rendered-messages'] "
        ".chat-message-wrapper:nth-of-type(2) "
        'div[class="chat-message-bubble chat-assistant-message"] '
        'div[class="dash-graph"]'
    )
    plot_answer_selector.wait_for(state="attached")
    code_answer_selector = page.locator(
        "div[id*='rendered-messages'] "
        ".chat-message-wrapper:nth-of-type(2) "
        'div[class="chat-message-bubble chat-assistant-message"] '
        "summary"
    )
    code_answer_selector.wait_for(state="attached")
