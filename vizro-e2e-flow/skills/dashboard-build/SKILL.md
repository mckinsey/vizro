---
name: dashboard-build
description: A skill that should be invoked whenever a user wants to build a Dashboard or simple app. This skill is Phase 2 of an e2e process that covers the actual build and testing. For Phase 1 (requirements, layout design, visualization selection), use the dashboard-design skill.
---

## CRITICAL Guidelines for Dashboard Building

- Ideally, do NOT skip Phase 1 (dashboard-design skill) as that ensures a much smoother build process. If the user just wants to build it, explain the value of a design phase first. Check if there is any existing `/spec` directory from Phase 1. If yes, use that to guide your build.
- Use your native tools to understand the data well, especially if you build custom charts or when you use specific selectors.
- If the user asks for an example, simply copy the [example app](./references/example_app.py) and run it. Do not include your own data or change the example.
- When executing any script mentioned below for the first time, it may take a while to install dependencies. Plan accordingly before taking any rash actions.
- When iterating on the dashboard after completing all steps, do not forget key points from below, especially regarding spec compliance and updating and terminal handling: always keep all specs up to date, and always check if terminal output is clean after each iteration.
- Execute all scripts from this skill, and the `app.py` you will create, with `uv run <script_name>.py` or `uv run app.py` - this will ensure you use the correct dependencies and versions.
- **ABSOLUTELY NEVER** type ANY commands (including `sleep`, `echo`, or anything else) in the terminal where the dashboard app is running, even if you started it with `isBackground=true`. This WILL kill the dashboard process. The dashboard startup takes time - be patient and let it run undisturbed.

## Spec Files: Documenting Decisions

IMPORTANT: Each step produces a spec file in the `spec/` directory to document reasoning, enable collaboration, and allow resumption in future sessions. Create the `spec/` directory if it is not already present at the root of the project.

## Step 1: Build dashboard

1. You MUST ALWAYS copy the [example app](./references/example_app.py) over, and modify it - this ensures less errors!
1. Investigate about the Vizro model by executing the [schema fetching script](./scripts/get_model_json_schema.py). ALWAYS DO this for all models that you need - do NOT assume you know it. Execute the script like so: `uv run ./scripts/get_model_json_schema.py <model_name> <model_name2> ...` where `<model_name>` is the name of the model you want to get the schema for. You can get an overview of what is available by calling the [overview script](./scripts/get_overview_vizro_models.py) like so: `uv run ./scripts/get_overview_vizro_models.py`. This will print out all available models and their brief descriptions.
1. Build the dashboard config by changing the copied [example app](./references/example_app.py). Important: Very often normal plotly express charts will not suffice as they are too simple. In that case, refer to the [custom charts guide](./references/custom_charts_guide.md) to create more complex charts. These MUST be added to the correct section in the python app. Call the custom chart function from the `Graph` model in your dashboard app.
1. Run your dashboard app with `uv run <your_dashboard_app>.py` **CRITICAL**: After running this command, DO NOT run ANY other commands in that terminal. The dashboard takes time to start up (sometimes 10-30 seconds)
1. You MUST read the terminal to check for any errors, but do not put commands like `sleep` in it. Fix any warnings and even more important errors you encounter. ONLY once you see the dashboard running, inform the user. NEVER run any commands in that terminal after starting the dashboard.
1. When you iterate, no need to kill the dashboard, as we are using debug mode. Just save the file and it will reload automatically. Check the terminal occasionally for any failures. Once failed, you need to restart the dashboard.

### Optimizations and common errors

- **Data loading**: For dashboards needing data refresh (databases, APIs) or performance optimization, see the [data management guide](./references/data_management.md) for static vs dynamic data, caching, and best practices.
- **KPI cards**: Use `kpi_card()` for simple metrics, `kpi_card_reference()` for comparisons. Use `reverse_color=True` when lower is better (costs, errors). NEVER put `kpi_card` or `kpi_card_reference` as a custom chart, use the built-in `kpi_card` and `kpi_card_reference` (imported from `vizro.figures`) in `Figure` model instead.

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

This requires the Playwright MCP server to be running. If not available, inform the user and skip this step. Look for `mcp__*playwright__*` tools.

When conducting the below tests, feel free to go back to Step 1 to fix any issues you find, then come back here.

### Basic Testing Flow

1. Navigate to dashboard URL
1. Click through all pages
1. Check console for errors

```
Use: playwright:browser_navigate(url="http://localhost:8050")
Use: playwright:browser_click(element="Page Name", ref="...")
Use: playwright:browser_console_messages()
```

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

| File                                                          | When to Read                                                                      |
| ------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| [data_management.md](./references/data_management.md)         | Optimizations: Data loading patterns, static vs dynamic, caching, databases, APIs |
| [custom_charts_guide.md](./references/custom_charts_guide.md) | Step 1: Creating complex custom charts when plotly express isn't enough           |
| [example_app.py](./references/example_app.py)                 | Step 1: Starting template for dashboard implementation                            |
