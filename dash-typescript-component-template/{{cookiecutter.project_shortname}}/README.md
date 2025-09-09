# {{cookiecutter.project_name}}

{{cookiecutter.description}}

## Development
### Getting Started

1. Create a new python environment:
   ```shell
   uv venv
   source .venv/bin/activate
   ```
   _Note: venv\Scripts\activate for windows_

2. Install python dependencies:
   ```shell
   uv pip install -r requirements.txt
   ```
3. Install npm packages:
   1. Optional: use [nvm](https://github.com/nvm-sh/nvm) to manage node version:
      ```shell
      nvm install
      nvm use
      ```
   2. Install npm dependencies:
      ```shell
      npm install
      npm install echarts
      ```
4. Build the component:
   ```shell
   npm run build
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
- JavaScript bundle with ECharts (`{{cookiecutter.project_shortname}}.js` - 816KB)
- PropTypes validation (`proptypes.js`)
- Component metadata and package info