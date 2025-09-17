# {{cookiecutter.project_name}}

{{cookiecutter.description}}

## Development
### Getting Started

1. Create a new python environment:
   ```shell
   uv venv
   source .venv/bin/activate
   ```
2. Install python dependencies:
   ```shell
   uv pip install -r requirements.txt
   ```
3. Install npm packages:
   1. Install `nvm` to get the appropriate node version:
   
      Latest nvm_version can be found [here](https://github.com/nvm-sh/nvm)
      ```shell
      curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/<nvm_version>/install.sh | bash
      ```
   2. Install latest NodeJS using `nvm`:
   
      Find latest LTS NodeJS version
      ```shell
      nvm list-remote
      ```
      Install latest LTS NodeJS version
      ```shell
      nvm install <NodeJS_LTS_version>
      ```
   3. Install npm dependencies:
      ```shell
      npm install
      ```
4. Put TypeScrit component code to the `{{cookiecutter.project_shortname}}.tsx` file located under `{{cookiecutter.project_name}}/src/ts/components`
5. Build the component:
   ```shell
   npm run build
   ```
6. Code Formatting

   This project uses:

   - [Black](https://black.readthedocs.io/) for code formatting
   - [isort](https://pycqa.github.io/isort/) for import sorting
   - [Ruff](https://docs.astral.sh/ruff/) for linting

   Run:

   ```bash
   black .
   isort .
   ruff check . --fix
   ````
7. Install component
   ```shell
   uv pip install {{cookiecutter.project_shortname}}
   ```
8. Run the demo:

   Edit `app.py` to use newly created component in `Vizro` and run it
   ```shell
   python app.py
   ```

### Build and Package

#### Build Wheel Package with Hatch

To build a distributable Python wheel package:

# Build wheel and source distribution
source .venv/bin/activate && hatch build

This creates:
- `dist/{{cookiecutter.project_shortname}}-1.0.0-py2.py3-none-any.whl` - Python wheel package
- `dist/{{cookiecutter.project_shortname}}-1.0.0.tar.gz` - Source distribution

#### Install the Built Package

```shell
# Install from local wheel
pip install dist/{{cookiecutter.project_shortname}}-1.0.0-py2.py3-none-any.whl
```

#### Package Contents

The wheel includes:
- Python component (`{{cookiecutter.component_name}}.py`)
- JavaScript bundle with ECharts (`{{cookiecutter.project_shortname}}.js`)
- PropTypes validation (`proptypes.js`)
- Component metadata and package info