# Frequently asked questions

## Should I use Vizro-AI or Vizro-MCP?

Dashboard generation in Vizro-AI has largely been replaced by [Vizro-MCP](https://vizro.readthedocs.io/projects/vizro-mcp/). Starting with version `0.4.0`, Vizro-AI only supports chart generation, but is based on [Pydantic AI](https://ai.pydantic.dev/) and supports async execution, streaming, dependency injection, and integration with [the A2A protocol](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/).

For dashboard generation, we recommend using Vizro-MCP, which can be used without an API key. Vizro-MCP works within familiar development environments like VS Code, Cursor, or Claude Desktop, for ease of us

## Who works on Vizro-AI?

### Current team members

[Alexey Snigir](https://github.com/l0uden), [Antony Milne](https://github.com/antonymilne), [Dan Dumitriu](https://github.com/dandumitriu1), [Huong Li Nguyen](https://github.com/huong-li-nguyen), [Jo Stichbury](https://github.com/stichbury), [Joseph Perkins](https://github.com/Joseph-Perkins), [Lingyi Zhang](https://github.com/lingyielia), [Maximilian Schulz](https://github.com/maxschulz-COL), [Nadija Graca](https://github.com/nadijagraca), [Petar Pejovic](https://github.com/petar-qb), [Stephanie Kaiser](https://github.com/stephkaiser).

With thanks to Sam Bourton and Stephen Xu for sponsorship, inspiration and guidance, plus everyone else who helped to test, guide, support and encourage development.

## Which large language models are supported by vizro-ai?

Vizro-AI uses [Pydantic AI](https://ai.pydantic.dev/) for LLM integration and supports models from multiple vendors including OpenAI, Anthropic, Google, and Mistral. Refer to [supported models](../user-guides/customize-vizro-ai.md#supported-models) in `vizro-ai` docs for details.

## Can I use async/streaming with chart_agent?

Yes! Since `chart_agent` is a Pydantic AI agent, you can use all Pydantic AI features including async execution, streaming, and event handling. See the [advanced options guide](../user-guides/advanced-options.md) for examples.

## Migration guide for versions prior to `0.4.0`?

### Changes to `VizroAI`

Various method names and the overall API structure have been changed in version `0.4.0`. The `VizroAI` class has been deprecated in favor of the `chart_agent` for chart generation. Where possible, we have retained the deprecated methods with their old names to help ease migration, but calling them will emit deprecation warnings and raise `RuntimeError`.

| Vizro-AI < 0.4.0 | Vizro-AI ≥ 0.4.0 |
|------------------|------------------|
| `VizroAI.plot()` | `chart_agent.run_sync()` |
| `VizroAI.dashboard()` | `chart_agent` (for charts) + [Vizro-MCP](https://vizro.readthedocs.io/projects/vizro-mcp/) (for dashboards) |
| `VizroAI(model=model)` | `chart_agent.run_sync(model=model, ...)` |
| Synchronous only | `chart_agent.run_sync()` (sync) or `chart_agent.run()` (async) |

### Chart generation migration

**Before (deprecated):**
```py
from vizro_ai import VizroAI

vizro_ai = VizroAI(model="gpt-4")
fig = vizro_ai.plot(df=df, user_input="create a bar chart")
fig.show()
```

**After (current):**
```py
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from vizro_ai.agents import chart_agent

model = OpenAIChatModel("gpt-4", provider=OpenAIProvider(api_key="your-key"))
result = chart_agent.run_sync(model=model, user_prompt="create a bar chart", deps=df)
fig = result.output.get_fig_object(df)
fig.show()
```

### Dashboard generation migration

**Before (deprecated):**
```py
from vizro_ai import VizroAI

vizro_ai = VizroAI(model="gpt-4")
dashboard = vizro_ai.dashboard(dfs=[df1, df2], user_input="create a dashboard")
```

**After (current):**
Dashboard generation is no longer supported in Vizro-AI. Use [Vizro-MCP](https://vizro.readthedocs.io/projects/vizro-mcp/) instead, which doesn't require an API key and works with familiar LLM applications like VS Code, Cursor, or Claude Desktop.



## Why do I get `RuntimeError: This event loop is already running` in Jupyter Notebooks?

This error occurs due to conflicts between Jupyter's event loop and Pydantic AI's event loop. To fix this, add the following two lines at the beginning of your notebook:

```py
import nest_asyncio
nest_asyncio.apply()
```

This fix also applies to Google Colab and Marimo. For more information, see the [Pydantic AI troubleshooting guide](https://ai.pydantic.dev/troubleshooting/#jupyter-notebook-errors).
