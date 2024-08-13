# Model usage

## Supported models
Vizro-AI currently supports the following [OpenAI models](https://platform.openai.com/docs/models). We are working on supporting more vendors:

=== "OpenAI"

    To use OpenAI with Vizro-AI, you must have an account with paid-for credits available. None of the free accounts will suffice.

    - gpt-3.5-turbo `default`
    - gpt-4-turbo
    - gpt-4o
    - gpt-4
    - gpt-4-0613
    - gpt-4-1106-preview
    - gpt-4-turbo-2024-04-09
    - gpt-4-turbo-preview
    - gpt-4-0125-preview
    - gpt-3.5-turbo-1106
    - gpt-3.5-turbo-0125
    - gpt-4o-2024-05-13
    - gpt-4o-mini-2024-07-18
    - gpt-4o-mini

=== "Anthropic"

    :octicons-hourglass-24: In development

=== "MistralAI"

    :octicons-hourglass-24: In development


These models offer different levels of performance and cost to Vizro-AI users.

### Chart generation

For basic chart creation with OpenAI, the **gpt-4o-mini** and **gpt-3.5** model series have lower price points and faster speeds, but they do not offer sophisticated charting.

Consider upgrading to the **gpt-4o** and **gpt-4** model series for more demanding tasks. The downside of using these models is that they come at a higher cost.

Refer to the [OpenAI documentation for more about model capabilities](https://platform.openai.com/docs/models/overview) and [pricing](https://openai.com/pricing).

<!-- WE NEED TO ADD SOME MORE ABOUT THE OTHER VENDORS WHEN WE HAVE THAT INFO -->

### Dashboard generation

=== "OpenAI"

    - gpt-3.5-turbo `default`: Ideal for smaller requests and simple specifications. However, due to the complexity of dashboard creation, `gpt-3.5-turbo` often produces incomplete responses for larger tasks.
    - gpt-4o: Most ideal for dashboard generation tasks, providing stable and complete responses. Compared to gpt-4-turbo, it is much faster and cheaper.
    - gpt-4-turbo: Excels in dashboard creation tasks, providing stable and complete responses.
    - gpt-4o-mini: Ideal for smaller requests and simple specifications. Most cost-effective. However, due to the complexity of dashboard creation, its performance is not guaranteed to be reliable.


=== "Anthropic"

    :octicons-hourglass-24: In development


## OpenAI initialization

`VizroAI` can be initialized without any arguments, in which case it uses `"gpt-3.5-turbo"` by default, with a temperature setting of 0. `"gpt-3.5-turbo"` offers enhanced speed and accuracy, and generates responses in requested formats while maintaining cost-effective performance.

### Customization at initialization
To customize the model, you can pass `VizroAI` a single argument named `model`, which can either be a string that specifies the name of a `ChatOpenAI` model or an instantiated [`ChatOpenAI`](https://api.python.langchain.com/en/latest/chat_models/langchain_openai.chat_models.base.ChatOpenAI.html) model.

When specifying a model as a string, you can select any option from the [supported models](#supported-models) listed above.

The example below uses the OpenAI model name in a string form:

!!! example "Customize with string"

    === "python"
        ```py linenums="1"
        from vizro_ai import VizroAI

        vizro_ai = VizroAI(model="gpt-4o")
        ```

The example below customizes the `ChatOpenAI` instance further beyond the chosen default from the string instantiation. We pass the `"gpt-4o"` model from OpenAI as `model_name` for `ChatOpenAI`, which offers improved response accuracy, we also want to increase maximum number of retries.
It's important to mention that any parameter that could be used in the `openai.create` call is also usable in `ChatOpenAI`. For more customization options for `ChatOpenAI`, refer to the [LangChain ChatOpenAI docs](https://api.python.langchain.com/en/latest/chat_models/langchain_openai.chat_models.base.ChatOpenAI.html)

<!-- vale off -->
To ensure a deterministic answer to our queries, we've set the temperature to 0. If you prefer more creative (but potentially more unstable) responses, you can raise the temperature to a maximum of 1.
<!-- vale on -->

!!! example "Customize with instantiated model"

    === "python"
        ```py linenums="1"
        from vizro_ai import VizroAI
        from langchain_openai import ChatOpenAI

        import vizro.plotly.express as px
        df = px.data.gapminder()

        llm = ChatOpenAI(
            model_name="gpt-4o",
            temperature=0,
            max_retries=5,
        )
        vizro_ai = VizroAI(model=llm)
        fig = vizro_ai.plot(df, "describe the composition of gdp in continent")
        fig.show()
        ```

Passing an instantiated model to `VizroAI` lets you customize it, and additionally, it enables you to use an OpenAI model that is not included in the above list of [supported models](#supported-models).
