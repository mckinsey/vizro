# Vizro-AI deprecation notice

**Vizro-AI is deprecated. Version 0.4.2 is the final release; no further development or releases are planned.**

## What this means

- `0.4.2` is the last release of the `vizro-ai` package. No new features, chart-agent improvements, or bug fixes will be shipped.
- Bug and security fixes are not guaranteed going forward.
- Existing installs of `vizro-ai` continue to work as before — nothing is being pulled from PyPI, and no runtime behavior changes.
- The documentation at [vizro.readthedocs.io/projects/vizro-ai](https://vizro.readthedocs.io/projects/vizro-ai/) remains available as a historical reference for the final release.

## What to use instead

Use **[Vizro-MCP](https://vizro.readthedocs.io/projects/vizro-mcp/)**, a [Model Context Protocol](https://modelcontextprotocol.io/) server that works with MCP-enabled LLM clients (such as Claude Desktop or Cursor) to create Vizro charts and dashboards.


## Questions or issues

For questions about migrating to Vizro-MCP, or about existing `vizro-ai` behavior, use [GitHub Issues](https://github.com/mckinsey/vizro/issues).
