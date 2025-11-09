# Vizro Flow Plugin

This folder contains a Claude Code plugin for end-to-end dashboard development. It includes two skills:

- **dashboard-design**: End-to-end dashboard design workflow from concept through wireframing
- **dashboard-implementation**: Vizro implementation guidance with MCP setup and Python quickstart

and the configuration for the Vizro MCP for implementation support.

## Installation

### Option 1: Install from repository as a plugin

Install using the plugin command with the `mckinsey/vizro` repository:

```
/plugin marketplace add mckinsey/vizro
/plugin install vizro-e2e-flow
```

This works well when using Claude Code. It automatically adds the Vizro MCP server for implementation support.

### Option 2: Upload skills folders

Zip the individual skill folders (`/vizro-e2e-flow-plugin/skills/dashboard-design/` and `/vizro-e2e-flow-plugin/skills/dashboard-implementation/`) and upload them directly to Claude apps, e.g. Claude Desktop.

Note that this doesn't automatically add the Vizro MCP server for implementation support. You need to [add it manually](https://vizro.readthedocs.io/projects/vizro-mcp/en/latest/pages/tutorials/first-dashboard-tutorial/).

## Usage

The skills work together for a complete dashboard workflow:

1. **Design Phase**: Use `dashboard-design` skill for:

    - Defining purpose and audience
    - Selecting and prioritizing metrics
    - Choosing chart types
    - Designing layout and hierarchy
    - Creating wireframes

1. **Implementation Phase**: Use `dashboard-implementation` skill for:

    - Deciding if Vizro is appropriate
    - Checking if Vizro MCP is available
    - Building the dashboard with either Vizro MCP or Python

For more information about these skills:

- See individual `SKILL.md` files in `skills/dashboard-design/` and `skills/dashboard-implementation/`

## Requirements

- **dashboard-design**: No dependencies (pure design guidance)
- **dashboard-implementation**: Python environment for local Vizro implementation OR public datasets for remote PyCafe previews. For any other implementation approach, a suitable technology stack and implementation guide is required.

## Compatibility

At the time of writing, this plugin is compatible with Anthropic products. However, as is often the case with genAI products, we expect this to work with other products in the future.

## Support

For issues or questions about these skills, please file an issue in the repository.

## Credits

Some of the skills content is based on the following sources:

- FusionCharts: [10 Dashboard Design Mistakes](https://www.fusioncharts.com/blog/10-dashboard-design-mistakes/)
- Geckoboard: [Dashboard Design and Build a Great Dashboard](https://www.geckoboard.com/uploads/geckoboard-dashboard-design-and-build-a-great-dashboard.pdf)
- UXPin: [Dashboard Design Principles](https://www.uxpin.com/studio/blog/dashboard-design-principles/)
