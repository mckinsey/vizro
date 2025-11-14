# Vizro Flow Plugin

This folder contains a Claude Code plugin for end-to-end dashboard development through a comprehensive 5-stage workflow:

1. **information-architecture**: Define the overall information structure, analytical questions, and KPI organization
1. **interaction-ux-design**: Design navigation, layouts, filter placement, and create wireframes
1. **visual-data-design**: Select chart types, establish visual hierarchy, and apply design principles
1. **development-implementation**: Build the dashboard with Vizro, integrate data, and optimize performance
1. **test-iterate**: Validate correctness, usability, and performance through systematic testing

The plugin includes pre-configured MCP servers for a seamless workflow:

- **Vizro MCP**: Dashboard implementation support
- **Playwright MCP**: Browser automation for functional testing

## Installation

### Option 1: Install from repository as a plugin

Install using the plugin command with the `mckinsey/vizro` repository:

```
/plugin marketplace add mckinsey/vizro
/plugin install vizro-e2e-flow
```

This works well when using Claude Code. It automatically configures both MCP servers (Vizro, Playwright) for the complete workflow.

### Option 2: Upload skills folders

Zip the individual skill folders and upload them directly to Claude apps, e.g. Claude Desktop:

- `/vizro-e2e-flow/skills/information-architecture/`
- `/vizro-e2e-flow/skills/interaction-ux-design/`
- `/vizro-e2e-flow/skills/visual-data-design/`
- `/vizro-e2e-flow/skills/development-implementation/`
- `/vizro-e2e-flow/skills/test-iterate/`

**Important**: This option only uploads the skill files, not the MCP configuration. You'll need to manually configure the MCP servers by adding the `.mcp.json` configuration to your MCP client. See the [.mcp.json file](https://github.com/mckinsey/vizro/blob/main/vizro-e2e-flow/.mcp.json) in this repository for the exact configuration needed for both MCP servers (Vizro MCP, Playwright MCP).

## Usage

The skills can be used individually or as a complete 5-stage workflow:

1. **Stage 1 - Information Architecture**: Use `information-architecture` skill to:

    - Define analytical questions and business context
    - Inventory data sources and map KPIs
    - Design page structure and information flow

1. **Stage 2 - Interaction/UX Design**: Use `interaction-ux-design` skill to:

    - Design navigation structure and layout grids
    - Define filter strategy and interaction patterns
    - Create wireframes (ASCII and HTML)

1. **Stage 3 - Visual/Data Design**: Use `visual-data-design` skill to:

    - Select appropriate chart types
    - Establish visual hierarchy and color strategy
    - Create high-fidelity visual mockups

1. **Stage 4 - Development/Implementation**: Use `development-implementation` skill to:

    - Decide if Vizro is appropriate
    - Set up MCP or Python implementation
    - Build, test, and optimize the dashboard

1. **Stage 5 - Test & Iterate**: Use `test-iterate` skill to:

    - Validate data accuracy and functionality
    - Conduct usability and performance testing
    - Monitor and iterate based on feedback

**Flexible Entry Points:**

- Full development: Start at Stage 1
- Have wireframes? Start at Stage 3
- Have designs? Start at Stage 4
- Iterate existing dashboard? Start at any stage if extra context required for iteration. Otherwise, make direct code edits

For more information, see individual `SKILL.md` files in each skill folder

## Requirements

- **Stages 1-3** (Information Architecture, UX Design, Visual Design): No technical dependencies - pure design guidance
- **Stage 4** (Development/Implementation): Python environment for local Vizro implementation OR public datasets for remote PyCafe previews
- **Stage 5** (Test & Iterate):
    - **Included with plugin**: Playwright MCP for AI-assisted UI testing
    - **Requirements for MCP**: Node.js (for Playwright MCP)
    - **Alternative**: Testing tools (pytest, selenium) for manual test script writing

## Compatibility

At the time of writing, this plugin is compatible with Anthropic products. However, as is often the case with genAI products, we expect this to work with other products in the future.

## Support

For issues or questions about these skills, please file an issue in the repository.

## Credits

Some of the skills content is based on the following sources:

- FusionCharts: [10 Dashboard Design Mistakes](https://www.fusioncharts.com/blog/10-dashboard-design-mistakes/)
- Geckoboard: [Dashboard Design and Build a Great Dashboard](https://www.geckoboard.com/uploads/geckoboard-dashboard-design-and-build-a-great-dashboard.pdf)
- UXPin: [Dashboard Design Principles](https://www.uxpin.com/studio/blog/dashboard-design-principles/)
