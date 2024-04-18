# Frequently asked questions

## Which LLMs are supported by Vizro-AI?
Vizro-AI currently supports OpenAI models as follows:

- gpt-3.5-turbo-0613 (to be deprecated on June 13, 2024)
- gpt-4-0613
- gpt-3.5-turbo-1106 (under testing)
- gpt-4-1106-preview (under testing, not suitable for production use)

These models offer different levels of performance and
cost. In general, the `gpt-3.5-turbo` collection provides the most cost-effective models,
which would be a good starting point for most users. `gpt-4` models are more powerful than `gpt-3` models, for example, they use more tokens per request. You can refer to these models' [capabilities](https://platform.openai.com/docs/models/overview)
and [pricing](https://openai.com/pricing) for more information.

We are working on supporting more models and more vendors. Stay tuned!


!!! Warning

    Users are recommended to exercise caution and to research and understand the selected large language model (LLM) before using `vizro_ai`.
    Users should be cautious about sharing or inputting any personal or sensitive information.

    **Data is sent to model vendors if you connect to LLMs via their APIs.**
    For example, if you specify model_name="gpt-3.5-turbo-0613", your data will be sent to OpenAI via their API.

    Users are also recommended to review the third party API key section of the [disclaimer](../explanation/disclaimer.md) documentation.

## What parameters does Vizro-AI support?
Currently, Vizro-AI supports the following parameters:

- `temperature`: A parameter for tuning the randomness of the output. It is set to 0 by
  default. We recommend setting it to 0 for Vizro-AI usage, as it's mostly
  deterministic.
- `model_name`: The name of the model to use. See above for [models currently supported by Vizro-AI](#which-llms-are-supported-by-vizro-ai) for the models supported.

!!! example "Config and construct Vizro-AI"

    === "python"
        ```py linenums="1"
        from vizro_ai import VizroAI

        vizro_ai = VizroAI(model_name="gpt-3.5-turbo-0613", temperature=0)
        ```

## Who works on Vizro-AI?

### Current team members
[Alexey Snigir](https://github.com/l0uden),
[Anna Xiong](https://github.com/Anna-Xiong),
[Antony Milne](https://github.com/antonymilne),
[Dan Dumitriu](https://github.com/dandumitriu1),
[Huong Li Nguyen](https://github.com/huong-li-nguyen),
[Jo Stichbury](https://github.com/stichbury),
[Joseph Perkins](https://github.com/Joseph-Perkins),
[Lingyi Zhang](https://github.com/lingyielia),
[Maximilian Schulz](https://github.com/maxschulz-COL),
[Nadija Graca](https://github.com/nadijagraca),
[Petar Pejovic](https://github.com/petar-qb).

With thanks to Sam Bourton and Stephen Xu for sponsorship, inspiration and guidance, plus everyone else who helped to test, guide, support and encourage development.
