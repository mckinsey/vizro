# Frequently asked questions

## Should I use Vizro-AI or Vizro-MCP?

Dashboard generation in Vizro-AI has largely been replaced by [Vizro-MCP](https://vizro.readthedocs.io/projects/vizro-mcp/). Starting with version 0.4.0, Vizro-AI only supports chart generation, but is based on Pydantic AI and supports async execution, streaming, dependency injection, and integration with the A2A protocol.

For dashboard generation, we recommend using Vizro-MCP, since it doesn’t require an API key and works with familiar LLM applications like VS Code, Cursor, or Claude Desktop, making it simpler to use.

## Who works on Vizro-AI?

### Current team members

[Alexey Snigir](https://github.com/l0uden), [Antony Milne](https://github.com/antonymilne), [Dan Dumitriu](https://github.com/dandumitriu1), [Huong Li Nguyen](https://github.com/huong-li-nguyen), [Jo Stichbury](https://github.com/stichbury), [Joseph Perkins](https://github.com/Joseph-Perkins), [Lingyi Zhang](https://github.com/lingyielia), [Maximilian Schulz](https://github.com/maxschulz-COL), [Nadija Graca](https://github.com/nadijagraca), [Petar Pejovic](https://github.com/petar-qb).

With thanks to Sam Bourton and Stephen Xu for sponsorship, inspiration and guidance, plus everyone else who helped to test, guide, support and encourage development.

## Which large language models are supported by vizro-ai?

Vizro-AI uses [Pydantic AI](https://ai.pydantic.dev/) for LLM integration and supports models from multiple vendors including OpenAI, Anthropic, Google, and Mistral. Refer to [supported models](../user-guides/customize-vizro-ai.md#supported-models) in `vizro-ai` docs for details.

## Can I use async/streaming with chart_agent?

Yes! Since `chart_agent` is a Pydantic AI agent, you can use all Pydantic AI features including async execution, streaming, and event handling. See the [Vizro-AI function calls and properties](../user-guides/advanced-options.md) for examples.

## What happened to VizroAI.plot() and VizroAI.dashboard()?

`VizroAI.plot()` and `VizroAI.dashboard()` have been deprecated in version 0.4.0. Use `chart_agent` instead for chart generation. For dashboard generation, use [Vizro-MCP](https://vizro.readthedocs.io/projects/vizro-mcp/).

## Why do I get `RuntimeError: This event loop is already running` in Jupyter Notebooks?

This error occurs due to conflicts between Jupyter's event loop and Pydantic AI's event loop. To fix this, add the following two lines at the beginning of your notebook:

```py
import nest_asyncio
nest_asyncio.apply()
```

This fix also applies to Google Colab and Marimo. For more information, see the [Pydantic AI troubleshooting guide](https://ai.pydantic.dev/troubleshooting/#jupyter-notebook-errors).
