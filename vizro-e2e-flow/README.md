# Vizro Flow Plugin

This folder contains a Claude Code plugin for end-to-end Vizro dashboard development with a 2-skill workflow:

**Skill 1: dashboard-design** - Design phase covering requirements, layout, and visualization selection
**Skill 2: dashboard-build** - Implementation and testing phase

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

Zip the skill folders and upload them directly to Claude apps (e.g., Claude Desktop):

- `/vizro-e2e-flow/skills/dashboard-design/`
- `/vizro-e2e-flow/skills/dashboard-build/`

**Important**: This option only uploads the skill files, not the MCP configuration. You'll need to manually configure the MCP servers by adding the `.mcp.json` configuration to your MCP client. See the [.mcp.json file](https://github.com/mckinsey/vizro/blob/main/vizro-e2e-flow/.mcp.json) for the configuration needed for both MCP servers (Vizro MCP, Playwright MCP).

## Usage

The plugin includes two skills that work together:

### Skill 1: dashboard-design

Use this skill first to design your dashboard. It enforces a 3-step workflow:

**Step 1 - Understand Requirements**:
- Define analytical questions and business context
- Inventory data sources and map KPIs
- Design page structure and information flow

**Step 2 - Design Layout & Interactions**:
- Design navigation structure and grid layouts
- Define filter strategy and placement
- Create wireframes for complex pages

**Step 3 - Select Visualizations**:
- Select appropriate chart types for each metric
- Establish visual hierarchy and color strategy
- Identify custom chart needs

### Skill 2: dashboard-build

Use this skill after completing dashboard-design to implement and test:

**Step 1 - Build Dashboard**:
- Use Vizro MCP tools or Python implementation
- Build, integrate data, and configure layouts
- Implement custom charts as needed

**Step 2 - Test & Verify**:
- Validate launch and navigation
- Test filter and control functionality
- Check for console errors

**Flexible Entry Points:**

- Full development: Start with dashboard-design skill
- Have wireframes: Validate Step 1, proceed from Step 2
- Have designs: Validate Steps 1-2, proceed from Step 3
- Iterate existing dashboard: Use dashboard-build skill directly

For detailed guidance, see:
- `skills/dashboard-design/SKILL.md` and reference files in `skills/dashboard-design/references/`
- `skills/dashboard-build/SKILL.md` and reference files in `skills/dashboard-build/references/`

## Requirements

- **dashboard-design skill** (Steps 1-3: Requirements, Layout, Visualization): No technical dependencies - pure design guidance
- **dashboard-build skill** (Step 1: Implementation): Python environment for local Vizro OR public datasets for remote PyCafe previews
- **dashboard-build skill** (Step 2: Testing):
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
