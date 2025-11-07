# Vizro Dashboard Skills

Two complementary skills for designing and implementing data visualization dashboards:

- **dashboard-design**: End-to-end dashboard design workflow from concept through wireframing
- **dashboard-implementation**: Vizro implementation guidance with MCP setup and Python quickstart

## Installation

### Option 1: Install from Repository

Install using the plugin command with the mckinsey/vizro repository:

```
/plugin marketplace add mckinsey/vizro
/plugin install vizro-e2e-flow
```

### Option 2: Upload Folders

Zip the individual skill folders (`dashboard-design/` and `dashboard-implementation/`) and upload them directly to Claude

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
    - Installing and configuring Vizro MCP
    - Building the dashboard with Python

## Requirements

- **dashboard-design**: No dependencies (pure design guidance)
- **dashboard-implementation**: Python environment for Vizro implementation OR public datasets for PyCafe previews

## Documentation

For more information about these skills:

- See individual `SKILL.md` files in each skill directory
- Reference files in `references/` folders provide detailed guidance
- Vizro documentation: https://vizro.readthedocs.io

## Support

For issues or questions about these skills, please file an issue in the repository.

## Credits

Some of the skills content is based on the following sources:

- FusionCharts: [10 Dashboard Design Mistakes](https://www.fusioncharts.com/blog/10-dashboard-design-mistakes/)
- Geckoboard: [Dashboard Design and Build a Great Dashboard](https://www.geckoboard.com/uploads/geckoboard-dashboard-design-and-build-a-great-dashboard.pdf)
- UXPin: [Dashboard Design Principles](https://www.uxpin.com/studio/blog/dashboard-design-principles/)
