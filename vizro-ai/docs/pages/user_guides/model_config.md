# How to configure Vizro-AI parameters

!!! Warning

    Users are recommended to exercise caution and to research and understand the selected Large Language Model (LLM) before using `vizro_ai`.
    Users should be cautious about sharing or inputting any personal or sensitive information.

    **Data is sent to model vendors if you connect to LLMs via their APIs.**
    For example, if you specify model_name="gpt-3.5-turbo-0613", your data will be sent to OpenAI via their API.

    Users are also recommended to review the third party API key section of the [disclaimer](../explanation/disclaimer.md) documentation.

## Supported parameters
Currently, Vizro-AI supports the following parameters:

- `temperature`: A parameter for tuning the randomness of the output. It is set to 0 by
  default. We recommend setting it to 0 for Vizro-AI usage, as it's mostly
  deterministic.
- `model_name`: The name of the model to use. Please refer to the section
  [Models currently supported by Vizro-AI](#supported-models) for available
  model options.

!!! example "Config and construct Vizro-AI"
    === "python"
        ```py linenums="1"
        from vizro_ai import VizroAI

        vizro_ai = VizroAI(model_name="gpt-3.5-turbo-0613", temperature=0)
        ```



## Supported models
Vizro-AI currently supports the following LLMs:

### OpenAI models

- gpt-3.5-turbo-0613 (to be deprecated on June 13, 2024)
- gpt-4-0613
- gpt-3.5-turbo-1106 (under testing)
- gpt-4-1106-preview (under testing, not suitable for production use)

These models provide different levels of performance and
cost. In general, the `gpt-3.5-turbo` collection provides the most cost-effective models,
which would be a good starting point for most users. `gpt-4` models are more powerful than `gpt-3` models, e.g. they allow for more tokens per request. You can refer to these models' [capabilities](https://platform.openai.com/docs/models/overview)
and [pricing](https://openai.com/pricing) for more information.

We are working on supporting more models and more vendors. Please stay tuned!
