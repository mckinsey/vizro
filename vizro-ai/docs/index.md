# Vizro-AI

!!! warning "Vizro-AI is deprecated"

    Vizro-AI is deprecated. Version `0.4.2` is the final release; no further development or releases are planned. Use [Vizro-MCP](https://vizro.readthedocs.io/projects/vizro-mcp/) instead for AI-assisted chart and dashboard creation. See the [deprecation notice](https://github.com/mckinsey/vizro/blob/main/vizro-ai/DEPRECATION.md) for details.

Vizro-AI used generative AI to extend [Vizro](https://vizro.readthedocs.io) so you could use instructions in English, or other languages, to effortlessly create interactive charts.

Built on [Pydantic AI](https://ai.pydantic.dev/), Vizro-AI provides a flexible agent-based architecture that supports async runs, streaming, dependency injection, and integration with [the A2A protocol](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/). The `chart_agent` can be customized and extended just like any Pydantic AI agent.

If you're new to coding, Vizro-AI simplifies the creation of charts with [Plotly](https://plotly.com/python/).

Even if you are an experienced data practitioner, Vizro-AI optimizes how you create visually appealing charts to present detailed insights about your data.

<img src="https://raw.githubusercontent.com/mckinsey/vizro/main/.github/images/toolkit_vizro_ai.gif" alt="Gif to demonstrate vizro-ai">

!!! notice "Notice"

    Review the [disclaimer](pages/explanation/disclaimer.md) before using the `vizro-ai` package.

    Users must connect to large language models (LLMs) to use Vizro-AI. Please review our [guidelines on the use of LLMs](pages/explanation/safety-in-vizro-ai.md) and the required [safeguarding for dynamic code evaluation](pages/explanation/safeguard.md).

---

*AI agents: see [llms.txt](llms.txt) for a machine-readable index of these docs.*
