# CLAUDE.md for `vizro-core` folder

`vizro-core` contains all code for the core Vizro framework.

## For AI agents and LLMs building Vizro apps

If you are an AI agent or LLM writing Python (or YAML / JSON) that uses the `vizro` package to build a dashboard, **your primary reference is the [Vizro for LLMs cheatsheet](https://vizro.readthedocs.io/en/stable/pages/for-llms/)**. It is a single page covering:

- The minimum runnable app.
- The `vizro.models` index (every public model, one-liner, link to guide).
- The `vizro.actions` index (built-in actions).
- Selector auto-selection rules for `Filter` and `Parameter`.
- The `@capture` decorator matrix.
- Features that only work in Python (not YAML / JSON).
- Top errors and their fixes.

Additional resources for authoring agents:

- [`docs/llms.txt`](docs/llms.txt) — curated `/llms.txt`-standard index of the full documentation.
- Every documentation page returns clean Markdown when fetched with the `Accept: text/markdown` request header.
- Published JSON Schemas per Vizro version: <https://github.com/mckinsey/vizro/tree/main/vizro-core/schemas>.

The rest of this file is for agents **contributing to `vizro-core` itself**.

## Development

### Working Directory

**Important**: All Hatch commands must be run from the `vizro-core/` directory.

### Additional Hatch Commands for vizro-core only

- `hatch run example` - Run the scratch dev example on port 8050 (hot-reloads)
- `hatch run example scratch_dev/yaml_version` - Run the scratch_dev yaml example on port 8050 (hot-reloads)
- `hatch run example dev` - Run the feature example dashboard on port 8050 (hot-reloads)

## Project Architecture

### Key concepts

- Vizro is based on Pydantic models to create a config driven dashboard framework.
- The Pydantic driven config layer abstract away the underlying plotly/dash implementation.

### Core Vizro usage example

```python
import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm

df = px.data.iris()

page = vm.Page(
    title="My first dashboard",
    components=[
        vm.Graph(figure=px.scatter(df, x="sepal_length", y="petal_width", color="species")),
        vm.Graph(figure=px.histogram(df, x="sepal_width", color="species")),
    ],
    controls=[
        vm.Filter(column="species"),
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
```

### Important implementation notes

- Add Vizro model must be derived from `VizroBaseModel`
- Anything Dash related must only appear in the `build` method of a model

### Main folders

- Source code: `src/vizro/`
- Vizro models: `src/vizro/models/`
- Tests: `tests/`
- Documentation: `docs/`
- Examples: `examples/`
- Changelog: `changelog.d/` and `CHANGELOG.md`

## Workspace structure

- `pyproject.toml`: Package configuration for vizro-core with dependencies
- `hatch.toml`: Hatch configuration for the vizro-core folder, with all commands for task automation
