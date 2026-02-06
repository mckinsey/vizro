# CLAUDE.md for `vizro-core` folder

`vizro-core` contains all code for the core Vizro framework.

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

## Developing with local vizro-dash-components

`vizro-core` depends on `vizro-dash-components`. To use a local (editable) copy:

1. Build the component in `vizro-dash-components/`: `hatch run npm:build`
1. Install it into vizro-core's examples env:
    ```bash
    # From vizro-core/, find the env's Python path:
    hatch run examples:pypath
    # Then install editable:
    uv pip install -e ../vizro-dash-components --python "<path from above>"
    ```
1. Run the scratch dev app: `hatch run example`

After modifying JS/TS source in `vizro-dash-components/`, rebuild (`hatch run npm:build` there) and restart the Vizro app.

## Workspace structure

- `pyproject.toml`: Package configuration for vizro-core with dependencies
- `hatch.toml`: Hatch configuration for the vizro-core folder, with all commands for task automation
