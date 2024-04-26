# How to customize model usage

## Supported models
Vizro-AI currently supports [OpenAI models](https://platform.openai.com/docs/models) as follows:

- `gpt-3.5-turbo-0613` (to be deprecated on June 13, 2024)
- `gpt-4-0613`
- `gpt-3.5-turbo-1106` (under testing)
- `gpt-4-1106-preview` (under testing, not suitable for production use)
- `gpt-3.5-turbo-0125`
- `gpt-3.5-turbo`

We are working on supporting more models and more vendors. Stay tuned!

These models Vizro-AI supports offer different levels of performance and
cost:

* The **gpt-3.5** model series are good in both general tasks and chat-specific applications. These models have lower price point and higher speeds for providing answers.

* Consider upgrading to the **gpt-4** models for more demanding tasks. While they are part of a more capable GPT model series, their response time is slower than gpt-3.5 models, and they come at a higher cost.

Refer to the [OpenAI documentation for more about model capabilities](https://platform.openai.com/docs/models/overview) and [pricing](https://openai.com/pricing).

## Default initialization
`VizroAI`can be initialized without any arguments, in which case it uses `"gpt-3.5-turbo"` by default, with a temperature setting of 0. `"gpt-3.5-turbo"` offers enhanced speed and accuracy, and generates responses in requested formats while maintaining cost-effective performance.

## Customization at initialization
To customize the model, you can pass `VizroAI` a single argument named `model`, which can either be a string that specifies the name of a `ChatOpenAI` model or an instantiated `ChatOpenAI` model.

The example below uses the OpenAI model name in a string form:

!!! example "Customize with string"

    === "python"
        ```py linenums="1"
        from vizro_ai import VizroAI

        vizro_ai = VizroAI(model="gpt-3.5-turbo-0125")
        ```

The example below customizes the `ChatOpenAI` instance further beyond the chosen default from the string instantiation. We pass the `"gpt-3.5-turbo-0125"` model from OpenAI as `model_name` for `ChatOpenAI`, which offers improved response accuracy.

<!-- vale off -->
To ensure a deterministic answer to our queries, we've set the temperature to 0. If you prefer more creative (but potentially more unstable) responses, you can raise the temperature to a maximum of 1.
<!-- vale on -->

!!! example "Customize with instantiated model"

    === "python"
        ```py linenums="1"
        from vizro_ai import VizroAI
        from langchain_openai import ChatOpenAI

        import plotly.express as px
        df = px.data.gapminder()

        llm = ChatOpenAI(
            model_name="gpt-3.5-turbo-0125",
            temperature=0
        )
        vizro_ai = VizroAI(model=llm)
        vizro_ai.plot(df, "describe the composition of gdp in continent")
        ```

## Azure OpenAI models
To set up Azure OpenAI with VizroAI, you'll need to configure the AzureOpenAI instance by specifying your deployment name and model name using langchain. You can also set your environment variables for API configuration,
such as `OPENAI_API_TYPE`, `OPENAI_API_VERSION`, `OPENAI_API_BASE` and `OPENAI_API_KEY`.
Authentication can be done via an API key directly or through Azure Active Directory (AAD) for enhanced security.
For a detailed walk-through, refer to the [Langchain documentation](https://python.langchain.com/docs/integrations/llms/azure_openai/) directly.

Here is an example of how to set the LLM model to be an AzureOpenAI model:
!!! example  "Use Azure OpenAI model"

    === "python"
        ```py linenums="1"
        from langchain_openai import AzureOpenAI
        from vizro_ai import VizroAI

        # Create an instance of Azure OpenAI
        # Replace the deployment name with your own
        llm = AzureOpenAI(
            deployment_name="td2",
            model_name="gpt-3.5-turbo-instruct",
        )
        vizro_ai = VizroAI(model=llm)
        ```
