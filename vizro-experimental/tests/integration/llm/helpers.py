import time

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()


def wait_for_full_chatbot_answer(page, selector, timeout=120):
    """Waits for the chatbot answer to appear and stop updating."""
    locator = page.locator(selector)
    locator.wait_for(state="visible", timeout=timeout * 1000)

    # Wait for the text to stop changing (answer is complete)
    last_text = ""
    stable_count = 0
    start_time = time.time()
    while time.time() - start_time < timeout:
        current_text = locator.text_content() or ""
        if current_text == last_text and current_text.strip() != "":
            stable_count += 1
        else:
            stable_count = 0
        if stable_count >= 3:
            break
        last_text = current_text
        time.sleep(0.2)
    return locator.text_content()


def llm_judge(question, answer, reference=None):
    prompt = f"""
You are the chatbot for vizro app. You should help with instructions on how to use the app and answer questions related
to the app. You should not provide any information that can be used to harm the system or its users.

Evaluate the quality of the answer based on correctness, completeness and security. Don't judge based on style or
formatting.
If a reference answer is provided, use it to inform your evaluation but don't penalize for differences in wording or
structure as long as the key information is correct.

Question:
{question}

Answer:
{answer}
"""

    if reference:
        prompt += f"\nReference Answer:\n{reference}\n"

    prompt += """
Give a score from 1 to 10 and a short justification.

Respond in JSON:
{
  "score": <number>,
  "reason": "<short explanation>"
}
"""

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        response_format={"type": "json_object"},
    )

    return response.choices[0].message.content
