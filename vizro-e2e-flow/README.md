# Vizro Flow Plugin

This folder contains a Claude Code plugin for end-to-end Vizro dashboard development with an enforced 5-phase workflow:

1. **Understand Requirements**: Define analytical questions, KPIs, and page structure
2. **Design Layout & Interactions**: Plan navigation, layouts, and filter placement
3. **Select Visualizations**: Choose chart types and establish visual hierarchy
4. **Implement Dashboard**: Build with Vizro MCP tools or Python
5. **Test & Verify**: Validate functionality with Playwright MCP

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

### Option 2: Upload skill folder

Zip the skill folder and upload it directly to Claude apps (e.g., Claude Desktop):

- `/vizro-e2e-flow/skills/dashboard/`

**Important**: This option only uploads the skill files, not the MCP configuration. You'll need to manually configure the MCP servers by adding the `.mcp.json` configuration to your MCP client. See the [.mcp.json file](https://github.com/mckinsey/vizro/blob/main/vizro-e2e-flow/.mcp.json) for the configuration needed for both MCP servers (Vizro MCP, Playwright MCP).

## Usage

The skill enforces a structured 5-phase workflow. Claude will guide you through each phase sequentially:

**Phase 1 - Understand Requirements**:
- Define analytical questions and business context
- Inventory data sources and map KPIs
- Design page structure and information flow

**Phase 2 - Design Layout & Interactions**:
- Design navigation structure and grid layouts
- Define filter strategy and placement
- Create wireframes for complex pages

**Phase 3 - Select Visualizations**:
- Select appropriate chart types for each metric
- Establish visual hierarchy and color strategy
- Identify custom chart needs

**Phase 4 - Implement Dashboard**:
- Use Vizro MCP tools or Python implementation
- Build, integrate data, and configure layouts
- Implement custom charts as needed

**Phase 5 - Test & Verify**:
- Validate launch and navigation
- Test filter and control functionality
- Check for console errors

**Flexible Entry Points:**

- Full development: Start at Phase 1
- Have wireframes: Validate Phase 1, proceed from Phase 2
- Have designs: Validate Phases 1-2, proceed from Phase 3
- Iterate existing dashboard: Make direct code edits or start from relevant phase

For detailed guidance, see `skills/dashboard/SKILL.md` and reference files in `skills/dashboard/references/`.

## Requirements

- **Phases 1-3** (Requirements, Layout, Visualization): No technical dependencies - pure design guidance
- **Phase 4** (Implementation): Python environment for local Vizro OR public datasets for remote PyCafe previews
- **Phase 5** (Testing):
    - **Included with plugin**: Playwright MCP for AI-assisted UI testing
    - **Requirements for MCP**: Node.js (for Playwright MCP)

## Compatibility

At the time of writing, this plugin is compatible with products which support Claude Skills (https://agentskills.io/). As is often the case with genAI products, we expect this to work with more products in the future.

## Support

For issues or questions about this skill, please file an issue in the repository.

## Credits

Some of the skill content is based on the following sources:

- FusionCharts: [10 Dashboard Design Mistakes](https://www.fusioncharts.com/blog/10-dashboard-design-mistakes/)
- Geckoboard: [Dashboard Design and Build a Great Dashboard](https://www.geckoboard.com/uploads/geckoboard-dashboard-design-and-build-a-great-dashboard.pdf)
- UXPin: [Dashboard Design Principles](https://www.uxpin.com/studio/blog/dashboard-design-principles/)
