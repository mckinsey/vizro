# Model usage

This guide shows how to set up a large language model (LLM) for use with Vizro-AI. Setting up a LLM is required for the package to generate charts based on natural language queries. To ensure responsible use, review the vendor's guidelines on risk mitigation before using the model to understand potential model limitations and best practices.

## Supported models

Vizro-AI uses [Pydantic AI](https://ai.pydantic.dev/) for LLM integration and supports models from multiple vendors including OpenAI, Anthropic, Google, and Mistral. The `chart_agent` accepts any Pydantic AI compatible model.

## Setting up models

Models are passed directly to the `chart_agent.run_sync()` or `chart_agent.run()` methods. You can configure models with various parameters including API keys, base URLs, and other vendor-specific settings.

### OpenAI

To use OpenAI models, first install the OpenAI optional dependency:

```bash
pip install vizro_ai[openai]
```

Then set up the model:

```py
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from vizro_ai.agents import chart_agent
import plotly.express as px

# Set up the model
model = OpenAIChatModel(
    "gpt-5-nano-2025-08-07",
    provider=OpenAIProvider(api_key="your-api-key-here"),
)

# Use with chart_agent
df = px.data.gapminder()
result = chart_agent.run_sync(
    model=model,
    user_prompt="Create a bar chart showing GDP by continent",
    deps=df,
)
```

You can also set the API key via environment variable `OPENAI_API_KEY` (see [Using environment variables](#using-environment-variables) below).

For custom base URLs (e.g., Azure OpenAI or custom endpoints):

```py
model = OpenAIChatModel(
    "gpt-5-nano-2025-08-07",
    provider=OpenAIProvider(
        base_url="your-base-url-here",
        api_key="your-api-key-here",
    ),
)
```

To use OpenAI with Vizro-AI, you must have an account with paid-for credits available. None of the free accounts will suffice. [Check the OpenAI models and pricing on their website](https://platform.openai.com/docs/models). Before using a model, please review OpenAI's guidelines on risk mitigation to understand potential model limitations and best practices. [See the OpenAI site for more details on responsible usage](https://platform.openai.com/docs/guides/safety-best-practices).

### Other model providers

Vizro-AI supports all Pydantic AI compatible models. You can install the most common providers (Google, Anthropic, Mistral and OpenAI) directly via an optional dependency as follows (pick any single one or multiple together):

```bash
pip install vizro_ai[google,anthropic,mistral,openai]
```

or you can choose to install _any_ provider listed on the [Pydantic AI model providers documentation](https://ai.pydantic.dev/models/overview/) via `pydantic-ai-slim`, e.g. Bedrock:

```bash
pip install pydantic-ai-slim[bedrock]
```

## Advanced configuration

### Custom model parameters

You can customize model parameters when instantiating models. For example, with OpenAI you can set temperature and other parameters:

```py
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

model = OpenAIChatModel(
    "gpt-5-nano-2025-08-07",
    provider=OpenAIProvider(api_key="your-api-key-here"),
    temperature=0.7,  # Adjust creativity (0-1)
    max_tokens=2000,  # Maximum response length
)
```

### Using environment variables

The easiest way to manage API keys is through environment variables. Once you have the API key, you can set it as an environment variable:

```bash
export OPENAI_API_KEY='your-api-key'
```

You can set them in your `.env` file using `python-dotenv` (see the [installation guide](install.md) for more details) or export them in your terminal.

Once the environment variable is set, you can use `OpenAIChatModel` with just the model name:

```py
from pydantic_ai.models.openai import OpenAIChatModel

model = OpenAIChatModel("gpt-5-nano-2025-08-07")
```

By default, the `OpenAIChatModel` uses the `OpenAIProvider` with the `base_url` set to `https://api.openai.com/v1`.

## What model to choose?

### Chart generation

At the time of writing, we found that for chart creation, the leading vendor's "cheaper" models, are suitable for basic charting despite their relatively low price points.

Consider upgrading to higher-tier models for more demanding tasks. The downside of using these models is that they come at a higher cost.

## Learn more

For more information on Pydantic AI models and capabilities, see the [Pydantic AI documentation](https://ai.pydantic.dev/models/).
