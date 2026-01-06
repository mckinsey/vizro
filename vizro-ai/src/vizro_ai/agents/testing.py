import os
from typing import Annotated

import logfire
from dotenv import load_dotenv
from pydantic import AfterValidator, BaseModel, Field, ValidationError
from pydantic_ai import Agent, ModelRetry
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

# from vizro_ai.plot._response_models import BaseChartPlan, ChartPlan, ChartPlanFactory

agent = Agent(output_type=float, instructions=("Come up with a random number between 40 and 100."), retries=2)


@agent.output_validator
def validate_output(output: float) -> float:
    """Validate the output."""
    print("VALIDATION OUTPUT: ", output)
    if output > 50:
        raise ModelRetry("Output must be less than 50.")
    return output


def check_number(number: float) -> float:
    """Check the number."""
    print("CHECK NUMBER: ", number)
    if number > 50:
        raise ValueError("Number must be less than 50.")
    return number


class DummyModel(BaseModel):
    """Dummy model for testing."""

    number: Annotated[float, AfterValidator(check_number), Field(description="A random number between 40 and 100.")]


agent2 = Agent(output_type=DummyModel)

if __name__ == "__main__":
    load_dotenv()
    # configure logfire
    logfire.configure(token=os.getenv("LOGFIRE_TOKEN"))
    logfire.instrument_pydantic_ai()

    # User can configure model, including usage limits etc
    model = OpenAIChatModel(
        "gpt-4o-mini",
        provider=OpenAIProvider(base_url=os.getenv("OPENAI_BASE_URL"), api_key=os.getenv("OPENAI_API_KEY")),
    )
    # Get some data
    number = agent2.run_sync(model=model, user_prompt="Come up with a number.")
    print(number)
