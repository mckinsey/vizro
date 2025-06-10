# Model usage

This guide shows how to set up a large language model (LLM) for use with Vizro-AI. Setting up a LLM is required for the package to generate charts and dashboards based on natural language queries. To ensure responsible use, review the vendor’s guidelines on risk mitigation before using the model to understand potential model limitations and best practices.

## Supported models

Vizro-AI supports **any** model that is available via [Langchain's `BaseChatModel` class](https://api.python.langchain.com/en/latest/language_models/langchain_core.language_models.chat_models.BaseChatModel.html#langchain_core.language_models.chat_models.BaseChatModel), and that has the [`with_structured_output` method](https://python.langchain.com/v0.2/docs/how_to/structured_output/#the-with_structured_output-method) implemented. An overview of the [most common vendor models supporting this functionality](https://python.langchain.com/v0.2/docs/integrations/chat/) can be found in Langchain's documentation. For ease of use one can also choose some models via a string parameter.

### Setting model via string for ease of use

We have created shortcuts with sensible defaults (mainly setting `temperature=0`) for some common vendors. These models can be chosen by using the string format in the tabs below. If no model is supplied, the default (currently `"gpt-4o-mini"`) is selected.

```py
vizro_ai = VizroAI(model="<chosen model>")
```

!!! note

    For the string settings to work, you must supply your API key via environment variables. The relevant variable names to be set are noted in each vendor tab.

=== "OpenAI"

    | Environment variable | Name(s)           |
    | -------------------- | ----------------- |
    | API key              | `OPENAI_API_KEY`  |
    | Base API URL         | `OPENAI_API_BASE` |

    To use OpenAI with Vizro-AI, you must have an account with paid-for credits available. None of the free accounts will suffice. [Check the OpenAI models and pricing on their website](https://platform.openai.com/docs/models). Before using a model, please review OpenAI's guidelines on risk mitigation to understand potential model limitations and best practices. [See the OpenAI site for more details on responsible usage](https://platform.openai.com/docs/guides/safety-best-practices).

    - `gpt-4o-mini` **default**
    - `gpt-4-turbo`
    - `gpt-4o`

=== "Anthropic"

    This currently works only for `VizroAI.plot` - we are working on making it available for `VizroAI.dashboard`.

    | Environment variable | Name(s)                                  |
    | -------------------- | ---------------------------------------- |
    | API key              | `ANTHROPIC_API_KEY`                      |
    | Base API URL         | `ANTHROPIC_API_URL`,`ANTHROPIC_BASE_URL` |

    To use Anthropic with Vizro-AI, you must have an account with paid-for credits available. None of the free accounts will suffice. [Check the Anthropic models and pricing on their website](https://docs.anthropic.com/en/docs/about-claude/models). Before using a model, please review Anthropic guidelines on risk mitigation to understand potential model limitations and best practices. [See the Anthropic site for more details on responsible usage](https://support.anthropic.com/en/collections/4078535-trust-safety/).

    - `claude-3-5-sonnet-latest`
    - `claude-3-opus-latest`
    - `claude-3-sonnet-20240229`
    - `claude-3-haiku-20240307`

    Install `vizro_ai` with optional `langchain-anthropic`:

    ```bash
    pip install -U vizro_ai[anthropic]
    ```

=== "MistralAI"

    This currently works only for `VizroAI.plot` - we are working on making it available for `VizroAI.dashboard`.

    | Environment variable | Name(s)            |
    | -------------------- | ------------------ |
    | API key              | `MISTRAL_API_KEY`  |
    | Base API URL         | `MISTRAL_BASE_URL` |

    To use Mistral with Vizro-AI, you can either use their API, which comes with an associated cost, or you could use their models for free under the Apache 2.0 license. In the latter case you need to set up the model API yourself. [Check for available Mistral models and pricing on their website](https://docs.mistral.ai/getting-started/models/models_overview).

    The documentation also explains the values to use for the following strings.

    - `mistral-large-latest`
    - `open-mistral-nemo`
    - `codestral-latest`

    Before using Mistral, review the guidelines on risk mitigation to understand potential model limitations and best practices. [See the Mistral site for more details on responsible usage](https://help.mistral.ai/en/).

    Install `vizro_ai` with optional `langchain_mistralai`:

    ```bash
    pip install -U vizro_ai[mistral]
    ```

    At the time of writing, we found that even the best Mistral models struggled to produce more than the simplest charts, but these outcomes can change drastically overtime.

!!! note

    When choosing the string representation, it sometimes can be tricky to have the correct environment variable set for the API key (and potential base URL). In case you cannot get this to work, we recommend instantiating the model directly (see below) and providing the API key via the models parameters.

<!--vale off-->

### Setting model via class for additional configuration

<!--vale on-->

Beyond passing a string, you can pass **any** model derived from [Langchain's `BaseChatModel` class](https://api.python.langchain.com/en/latest/language_models/langchain_core.language_models.chat_models.BaseChatModel.html#langchain_core.language_models.chat_models.BaseChatModel) that has the [`with_structured_output` method](https://python.langchain.com/v0.2/docs/how_to/structured_output/#the-with_structured_output-method) implemented. An overview of the [most common vendor models supporting this functionality](https://python.langchain.com/v0.2/docs/integrations/chat/) can be found in Langchain's documentation.

When choosing this approach, you can customize your model beyond the chosen default from the string instantiation. The choice of available arguments depends on the specific vendor implementation, but usually the main parameter to tweak is the temperature.

<!-- vale off -->

To ensure a deterministic answer to our queries, we've set the temperature to 0 in the string instantiation. If you prefer more creative (but potentially more unstable) responses, you can raise the temperature to a maximum of 1.

<!-- vale on -->

Below you can find an example where a custom model is instantiated with various custom parameters. Note that we manually set the API key and base URL, which is the easiest way to get it set up.

```py
import os
from langchain_openai import AzureChatOpenAI

llm = AzureChatOpenAI(
    azure_deployment="gpt-4-1106-preview",
    api_version="2024-04-01-preview",
    temperature=0.4,
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"]
)

vizro_ai = VizroAI(model=llm)
```

Passing an instantiated model to `VizroAI` lets you customize it, and also, it enables you to use a model or vendor that is not included in the above list of [string model names](#setting-model-via-string-for-ease-of-use).

## What model to choose?

### Chart generation

At the time of writing, we found that for chart creation, the leading vendor's "cheaper" models, for example OpenAI's `gpt-4o-mini`, are suitable for basic charting despite their relatively low price points.

Consider upgrading to, in the case of OpenAI the `gpt-4o` and `gpt-4` model series, or in the case of Anthropic the `Claude 3.5` model series, for more demanding tasks. The downside of using these models is that they come at a higher cost.

### Dashboard generation

At the time of writing we find that cheaper models only work for basic dashboards. For a reasonably complex dashboard we recommend the flagship models of the leading vendors, for example `gpt-4o`.
