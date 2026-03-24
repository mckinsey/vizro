---
name: dashboard-build
description: Use this skill to build, implement, and test Vizro dashboards (Phase 2). Activate when the user wants to create a working app, says "just build it", or has data ready for implementation. Requires spec files from the dashboard-design skill (Phase 1), or user confirmation to skip design.
---

## Prerequisites

Requires Phase 1 spec files from the **dashboard-design** skill: `spec/1_information_architecture.yaml`, `spec/2_interaction_ux.yaml`, and `spec/3_visual_design.yaml`. If these do not exist, ask the user whether to run Phase 1 first or proceed without specs.

## Guidelines

- Use your native tools to understand the data well, especially if you build custom charts or when you use specific selectors.
- If the user asks for an example, simply copy the [example app](./references/example_app.py) and run it. Do not include your own data or change the example.
- When executing any script mentioned below for the first time, it may take a while to install dependencies. Plan accordingly before taking any rash actions.
- When iterating on the dashboard after completing all steps, do not forget key points from below, especially regarding spec compliance and updating and terminal handling: always keep all specs up to date, and always check if terminal output is clean after each iteration.
- Execute all scripts from this skill, and the `app.py` you will create, with `uv run <script_name>.py` or `uv run app.py` - this will ensure you use the correct dependencies and versions.
- **ABSOLUTELY NEVER** type ANY commands (including `sleep`, `echo`, or anything else) in the terminal where the dashboard app is running, even if you started it with `isBackground=true`. This WILL kill the dashboard process. The dashboard startup takes time - be patient and let it run undisturbed.
- Step 2 (Testing) requires a Playwright MCP server. If unavailable, skip testing and inform the user.

## Spec Files: Documenting Decisions

IMPORTANT: Each step produces a spec file in the `spec/` directory to document reasoning, enable collaboration, and allow resumption in future sessions. Create the `spec/` directory if it is not already present at the root of the project.

## Step 1: Build dashboard

1. You MUST ALWAYS copy the [example app](./references/example_app.py) over, and modify it - this ensures less errors!
1. Investigate about the Vizro model by executing the [schema fetching script](./scripts/get_model_json_schema.py). ALWAYS DO this for all models that you need - do NOT assume you know it. Execute the script like so: `uv run ./scripts/get_model_json_schema.py <model_name> <model_name2> ...` where `<model_name>` is the name of the model you want to get the schema for (prints the full JSON schema for each model to stdout). You can get an overview of what is available by calling the [overview script](./scripts/get_overview_vizro_models.py) like so: `uv run ./scripts/get_overview_vizro_models.py` (prints all available model names with one-line descriptions to stdout).
1. Build the dashboard config by changing the copied [example app](./references/example_app.py). Important: Very often normal plotly express charts will not suffice as they are too simple. In that case, refer to the [custom charts guide](./references/custom_charts_guide.md) to create more complex charts. These MUST be added to the correct section in the python app. Call the custom chart function from the `Graph` model in your dashboard app.
1. Run your dashboard app with `uv run <your_dashboard_app>.py` **CRITICAL**: After running this command, DO NOT run ANY other commands in that terminal. The dashboard takes time to start up (sometimes 10-30 seconds)
1. You MUST read the terminal to check for any errors, but do not put commands like `sleep` in it. Fix any warnings and even more important errors you encounter. ONLY once you see the dashboard running, inform the user. NEVER run any commands in that terminal after starting the dashboard.
1. When you iterate, no need to kill the dashboard, as we are using debug mode. Just save the file and it will reload automatically. Check the terminal occasionally for any failures. Once failed, you need to restart the dashboard.

### Optimizations and common errors

- **Colors**: If `spec/3_visual_design.yaml` defines `color_decisions` or other agreed custom colors, implement them with the **selecting-vizro-charts** skill (Vizro `palettes` / `colors`; no arbitrary hex unless the user supplied them). If the spec omits color sections, do **not** add colors in code — use Plotly Express / Vizro defaults.
- **Data loading**: For dashboards needing data refresh (databases, APIs) or performance optimization, see the [data management guide](./references/data_management.md) for static vs dynamic data, caching, and best practices.
- **KPI cards**: Use built-in `kpi_card` / `kpi_card_reference` in `Figure` model only. Never rebuild as custom charts (exception: dynamic text). See **selecting-vizro-charts** skill.

### REQUIRED OUTPUT: spec/4_implementation.yaml

Save this file BEFORE proceeding to Step 2:

```yaml
# spec/4_implementation.yaml
implementation:
  app_file: <name>.py
  data_files:
    - [list of data files used]
  data_type: static/dynamic  # static for DataFrames, dynamic for data_manager functions
  data_sources:
    - name: [data source name]
      type: csv/database/api/function
      caching: true/false
      refresh_strategy: [if dynamic: cache timeout or refresh trigger]

spec_compliance:
  followed_specs: true/false
  deviations:
    - spec_item: [What was specified]
      actual: [What was implemented]
      reason: [Why the deviation was necessary]

custom_charts:
  - name: [Function name]
    purpose: [What it does]
```

### Validation Checklist

Before proceeding to Step 2, verify against spec files:

- [ ] All specs from `spec/1_information_architecture.yaml`, `spec/2_interaction_ux.yaml` and `spec/3_visual_design.yaml` are implemented if specs exist
- [ ] You have read the terminal output of the dashboard app for errors and warnings, you have not put any commands in the terminal after starting the app
- [ ] Any deviations are documented in `spec/4_implementation.yaml`

## Step 2: Testing (optional)

This requires a Playwright MCP server. If not available, inform the user and skip this step. Look for Playwright-related tools in your available MCP tools (naming varies by client).

When conducting the below tests, feel free to go back to Step 1 to fix any issues you find, then come back here.

### Basic Testing Flow

1. Navigate to dashboard URL
1. Click through all pages
1. Check console for errors

Use your Playwright MCP tools to navigate to `http://localhost:8050`, click through each page, and check the browser console for errors.

### Advanced Testing flow

1. Take a screenshot of each page, compare to specs and especially wireframes
1. Document any discrepancies

Important things to check:

- Line charts are readable, and not a mess due to lack of aggregation
- Graphs are legible and not squashed due to Layout

### REQUIRED OUTPUT: spec/5_test_report.yaml

Save this file to complete the project:

```yaml
# spec/5_test_report.yaml
testing:
  launch:
    successful: true/false
    url: http://localhost:8050
    errors: []

  navigation:
    all_pages_work: true/false
    issues: []

  console:
    no_errors: true/false
    errors_found: []

  screenshot_tests:
    performed: true/false
    pages_tested: []
    discrepancies:
      - page: [Page name]
        issue: [Description of visual issue]
        fixed: true/false
        notes: [Fix details or reason not fixed]

  requirements_met: true/false
  dashboard_ready: true/false
```

### Done When

- Dashboard launches without errors, no console errors
- User confirms requirements are met
- All spec files from this Phase 2 saved in `spec/` directory

---

## Reference Files

| Reference                                                     | When to Load                                            |
| ------------------------------------------------------------- | ------------------------------------------------------- |
| **selecting-vizro-charts** skill                              | Colors, KPI cards, custom charts, Plotly conventions    |
| **writing-vizro-yaml** skill                                  | YAML syntax, component patterns, data_manager, pitfalls |
| [data_management.md](./references/data_management.md)         | Static vs dynamic data, caching, databases, APIs        |
| [custom_charts_guide.md](./references/custom_charts_guide.md) | Implementing custom `@capture("graph")` charts          |
| [example_app.py](./references/example_app.py)                 | Starting template for dashboard implementation          |
