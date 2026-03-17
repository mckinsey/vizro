# Vizro e2e Flow Plugin

Vizro e2e Flow is a [Claude Code plugin](https://code.claude.com/docs/en/plugins) for end-to-end Vizro dashboard development. It consists of a 2-skill workflow:

- **Skill 1: dashboard-design** - Dashboard design phase covering requirements, layout, and individual chart visualization selection.

- **Skill 2: dashboard-build** - Dashboard implementation and testing phase.

The plugin includes a [Playwright MCP server](https://executeautomation.github.io/mcp-playwright/) delivering browser automation for functional testing.

## Prerequisites

Skills are a new way of working with agentic and generative AI, and have yet to become mainstream. It's likely that you'll be an experienced technical user if you're considering setting these up for Vizro development. You may find these instructions are outdated or that the installation process is bumpy because the Claude Code and Cursor products are still under development. If you experience issues, check their documentation for the latest way to install skills, and check on the status of [Claude](https://status.claude.com/) in case of an outage.

- At the time of writing, you'll need a [Pro, Max, Teams, or Enterprise Claude subscription](https://claude.com/pricing) or a [Claude Console](https://console.anthropic.com/) account or a [paid Cursor plan](https://cursor.com/pricing).
- You'll also need a [GitHub account](https://github.com) with SSH or HTTPS enabled.
- Clone the [Vizro repository](https://github.com/mckinsey/vizro.git) (and give it a star while you're there).

## Installation

### Option 1: Ask Cursor

Open a new chat and ask Cursor to import the Vizro e2e skills. Use Agent mode with a capable Claude model. We used `claude-4.6-opus-high`:

> I want to import 2 skills from the vizro repo at https://github.com/mckinsey/vizro.git, which are in the vizro-e2e-flow directory.

The GIF below shows how Cursor works through the task, shortened for brevity.

![](cursor-import-skills.gif)

Open a second chat window to ask which skills are available and confirm the dashboard design and dashboard build skills are present.

For more details, see [Cursor Skills documentation](https://cursor.com/docs/context/skills#installing-skills-from-github).

Then configure **Playwright MCP** for browser testing. In Cursor, go to **Cursor** > **Settings** > **Cursor Settings** > **Tools & MCP** and click Add Custom MCP to add the following to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest"
      ]
    }
  }
}
```

### Option 2: Claude Code (Plugin Marketplace)

Open your terminal and start Claude Code:

```bash
claude
```

Register the `mckinsey/vizro` repository as a plugin marketplace:

```
/plugin marketplace add mckinsey/vizro
```

Then install the plugin:

```
/plugin install vizro-e2e-flow@vizro-marketplace
```

Validate the installation by running:

```
/plugins
```

You should see `vizro-e2e-flow` listed with its skills (`dashboard-design`, `dashboard-build`) and the Playwright MCP connected:

```
playwright MCP · ✔ connected
```

## Quick Start Tutorial

Once the skills and Playwright MCP are installed, here's how to build your first dashboard end-to-end.

### Step 1: Start the design phase

The skills are automatically triggered when you mention keywords like "dashboard" in your message. For example:

> "I have a CSV of monthly sales data with columns for region, product, revenue, and units sold. I want to build a dashboard to track sales performance."

This invokes the **dashboard-design** skill, which guides you through three sub-steps:

1. **Understand Requirements** - Agent will ask about your analytical questions, data sources, KPIs, and page structure.

1. **Design Layout & Interactions** - Agent proposes a grid layout, navigation structure, and filter strategy. You review and iterate together.

1. **Select Visualizations** - Agent recommends chart types for each metric and establishes a visual hierarchy. You approve or adjust.

At the end of this phase, you'll have a complete design spec ready for implementation.

### Step 2: Build and test the dashboard

Once you're happy with the design, indicate you want to build it. For example:

> "Build the dashboard based on the design spec. Use Playwright MCP to test the dashboard."

This invokes the **dashboard-build** skill, which:

1. **Builds the Dashboard** - Agent writes the Python code using Vizro, integrates your data, and configures layouts based on the design spec from Step 1.

1. **Tests & Verifies** - Agent launches the dashboard and uses the Playwright MCP to automatically test it in a browser: validating navigation, filters, controls, and checking for console errors.

## Requirements

- **dashboard-design skill**: No technical dependencies - pure design guidance
- **dashboard-build skill (build)**: Python environment with [uv](https://docs.astral.sh/uv/) installed
- **dashboard-build skill (test)**: [Node.js](https://nodejs.org/) is required for the Playwright MCP.

## Compatibility

At the time of writing, this plugin is compatible with products which support Claude Agent Skills (https://agentskills.io/). As is often the case with GenAI products, we expect this to work with more products in the future.

## Support

For issues or questions about this skill, please file an issue in the repository.

## Credits

Some of the skill content is based on the following sources:

- FusionCharts: [10 Dashboard Design Mistakes](https://www.fusioncharts.com/blog/10-dashboard-design-mistakes/)
- Geckoboard: [Dashboard Design and Build a Great Dashboard](https://www.geckoboard.com/uploads/geckoboard-dashboard-design-and-build-a-great-dashboard.pdf)
- UXPin: [Dashboard Design Principles](https://www.uxpin.com/studio/blog/dashboard-design-principles/)
