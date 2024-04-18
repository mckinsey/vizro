# Frequently asked questions

## Which LLMs are supported by Vizro-AI?
Vizro-AI currently supports OpenAI models as follows:

- `gpt-3.5-turbo-0613` (to be deprecated on June 13, 2024)
- `gpt-4-0613`
- `gpt-3.5-turbo-1106` (under testing)
- `gpt-4-1106-preview` (under testing, not suitable for production use)
- `gpt-3.5-turbo-0125`
- `gpt-3.5-turbo`

These models offer different levels of performance and
cost. In general, the `gpt-3.5-turbo` collection provides the most cost-effective models,
which would be a good starting point for most users. `gpt-4` models are more powerful than `gpt-3` models, for example, they use more tokens per request. You can refer to these models' [capabilities](https://platform.openai.com/docs/models/overview)
and [pricing](https://openai.com/pricing) for more information.

We are working on supporting more models and more vendors. Stay tuned!


!!! Warning

    Users are recommended to exercise caution and to research and understand the selected large language model (LLM) before using `vizro_ai`.
    Users should be cautious about sharing or inputting any personal or sensitive information.

    **Data is sent to model vendors if you connect to LLMs via their APIs.**
    For example, if you specify model="gpt-3.5-turbo-0613", your data will be sent to OpenAI via their API.

    Users are also recommended to review the third party API key section of the [disclaimer](../explanation/disclaimer.md) documentation.

## What parameters does Vizro-AI support?
Currently, Vizro-AI supports the following parameters:

`model`: The name of the model  as `str` (see above for [models currently supported by Vizro-AI](#which-llms-are-supported-by-vizro-ai)) or instance of `ChatOpenAI` (see below for configuration options).

!!! example "Config and construct Vizro-AI"

    === "python"
        ```py linenums="1"
        from vizro_ai import VizroAI

        vizro_ai = VizroAI(model="gpt-3.5-turbo-0613")
        ```

## How can I customize my model?

The `model` parameter of `VizroAI` accepts an instantiated `ChatOpenAI` model, allowing users to customize it as needed.

!!! example "model customization"

    === "python"
        ```py linenums="1"
        from vizro_ai import VizroAI
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(
            model_name="gpt-3.5-turbo-1106",
            temperature=1
        )
        vizro_ai = VizroAI(model=llm)
        ```
