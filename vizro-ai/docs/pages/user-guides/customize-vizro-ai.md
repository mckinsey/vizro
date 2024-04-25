# How to customize VizroAI

This guide explains how to customize `VizroAI`.

`VizroAI` accepts a single argument named `model`. This `model` argument can either be a string that specifies the name of the `ChatOpenAI` model or an instantiated `ChatOpenAI` model.

We'll delve into customizing the `ChatOpenAI` model later; for now, let's concentrate on the default usage of `VizroAI`.

## Default usage

`VizroAI`can be initialized without any arguments, in which case it will, by default, use OpenAI model `"gpt-3.5-turbo"` with a temperature setting of 0.
`"gpt-3.5-turbo"` points to the latest model offering enhanced speed and accuracy in generating responses in requested formats, while maintaining cost-effective performance.


## Choosing OpenAI model

When choosing OpenAI model, there are few things to keep in mind; the complexity of the task, cost associated with it and the desired response time.

**gpt-3.5** model series are good in both general tasks and chat-specific applications. These models have lower price point and higher speeds for providing answers.

However, for more demanding tasks, consider upgrading to the **gpt-4** models. While they are part of a more capable GPT model series, their response time is slower than gpt-3.5 models, and they come at a higher cost.

In the example below, we customized `VizroAI` by providing OpenAI model name in a string form. ( see for [models currently supported by Vizro-AI](../explanation/faq.md#which-llms-are-supported-by-vizro-ai)).

!!! example "Customize with string"

    === "python"
        ```py linenums="1"
        from vizro_ai import VizroAI

        vizro_ai = VizroAI(model="gpt-3.5-turbo-0125")
        ```

## Customize ChatOpenAI instance

The `model` parameter in `VizroAI` can also take an initialized `ChatOpenAI` model, allowing for flexible customization by users. In the example below, we'll be customizing the `ChatOpenAI` instance.
The `"gpt-3.5-turbo-0125"` model from OpenAI as `model_name` for `ChatOpenAI`, which offers improved response accuracy. To ensure a deterministic answer to our queries, we've set the temperature to 0.
If you prefer more creative (but potentially more unstable) responses, you can raise the temperature to a maximum of 1.


!!! example "model customization"

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
