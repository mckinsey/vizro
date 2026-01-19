# Vizro-AI

!!! warning "Vizro-MCP may be more suitable in some cases"

    Vizro-AI dashboard generation is no longer actively developed and is superseded by [Vizro-MCP](https://vizro.readthedocs.io/projects/vizro-mcp/). Vizro-AI supports only chart generation from version 0.4.0.

Vizro-AI uses generative AI to extend [Vizro](https://vizro.readthedocs.io) so you can use instructions in English, or other languages, to effortlessly create interactive charts.

Built on [Pydantic AI](https://ai.pydantic.dev/), Vizro-AI provides a flexible agent-based architecture that supports async runs, streaming, dependency injection, and integration with the A2A protocol. The `chart_agent` can be customized and extended just like any Pydantic AI agent.

If you're new to coding, Vizro-AI simplifies the creation of charts with [Plotly](https://plotly.com/python/).

Even if you are an experienced data practitioner, Vizro-AI optimizes how you create visually appealing charts to present detailed insights about your data.

<img src="https://raw.githubusercontent.com/mckinsey/vizro/main/.github/images/toolkit_vizro_ai.gif" alt="Gif to demonstrate vizro-ai">

<div class="grid cards" markdown>

- :fontawesome-regular-map:{ .lg .middle } __New to Vizro-AI?__

    ---

    [:octicons-arrow-right-24: Quickstart chart generation](pages/tutorials/quickstart.md)

    [:octicons-arrow-right-24: Vizro-AI function calls and properties](pages/user-guides/advanced-options.md)

- :fontawesome-solid-keyboard:{ .lg .middle } __Get hands-on__

    ---

    [:octicons-arrow-right-24: Advanced options](pages/user-guides/advanced-options.md)

    [:octicons-arrow-right-24: Add charts to a Vizro dashboard](pages/user-guides/add-generated-chart-usecase.md)

- :fontawesome-solid-book-open-reader:{ .lg .middle } __Find out more__

    ---

    [:octicons-arrow-right-24: FAQs](pages/explanation/faq.md)

    [:octicons-arrow-right-24: Model usage](pages/user-guides/customize-vizro-ai.md)

- :fontawesome-solid-wand-magic-sparkles:{ .lg .middle } __Vizro-MCP and Vizro__

    ---

    [:new: Vizro-MCP](https://github.com/mckinsey/vizro/blob/main/vizro-mcp/README.md)

    [:octicons-arrow-right-24: Vizro documentation](https://vizro.readthedocs.io/)

</div>

!!! notice "Notice"

    Review the [disclaimer](pages/explanation/disclaimer.md) before using the `vizro-ai` package.

    Users must connect to large language models (LLMs) to use Vizro-AI. Please review our [guidelines on the use of LLMs](pages/explanation/safety-in-vizro-ai.md) and the required [safeguarding for dynamic code evaluation](pages/explanation/safeguard.md).
