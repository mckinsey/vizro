# How to customize VizroAI

This guide explains how to customize `VizroAI`.

`VizroAI` accepts a single argument named `model`. This `model` argument can either be a string that specifies the name of the `ChatOpenAI` model or an instantiated `ChatOpenAI` model.
We'll delve into customizing the `ChatOpenAI` model later; for now, let's concentrate on the default usage of `VizroAI`.

## Default usage

`VizroAI` can be initialized without any arguments, in which case the default OpenAI model used is `"gpt-3.5-turbo"`, and temperature is set to 0. `"gpt-3.5-turbo"` points to the latest model, it has improved speed and accuracy at responding in requested formats. 
It’s both good at completing both general tasks and chat-specific ones. - add cost eficiency while mantaining performance. for more complex upgrade. 

## Choosing OpenAI model

You can customize `VizroAI` by providing OpenAI model name in a string form.

!!! example "Customize with string"

    === "python"
        ```py linenums="1"
        from vizro_ai import VizroAI

        vizro_ai = VizroAI(model="gpt-3.5-turbo-0125")
        ```
We support the following OpenAI models:

| model                | description                                                                                        |
|----------------------|----------------------------------------------------------------------------------------------------|
| `gpt-3.5-turbo-0613` | Deprecated on June 13, 2024                                                                        |
| `gpt-4-0613`         | The most capable GPT model series to date. Able to do complex tasks, but slower at giving answers. |
| `gpt-3.5-turbo-1106` | under testing                                                                                      |
| `gpt-4-1106-preview` | under testing, not suitable for production use                                                     |
| `gpt-3.5-turbo-0125` | The latest GPT-3.5 Turbo mode                                                                      |
| `gpt-3.5-turbo`      | Currently points at `gpt-3.5-turbo-0125`                                                           |

## Customize ChatOpenAI instance

The `model` parameter in `VizroAI` can take an initialized `ChatOpenAI` model, allowing for flexible customization by users.
In the example below, we'll be customizing the `ChatOpenAI` instance.
The `"gpt-3.5-turbo-0125"` model from OpenAI as `model_name` for `ChatOpenAI`, which offers improved response accuracy. To ensure a deterministic answer to our queries, we've set the temperature to 0. If you prefer more creative responses, you can raise the temperature to a maximum of 1.


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
