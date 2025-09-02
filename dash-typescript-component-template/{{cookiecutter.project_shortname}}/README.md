# {{cookiecutter.project_name}}

{{cookiecutter.description}}

## Install

```shell
pip install {{cookiecutter.project_shortname}}
```

## Development
### Getting Started

1. Create a new python environment:
   ```shell
   python -m venv venv
   . venv/bin/activate
   ```
   _Note: venv\Scripts\activate for windows_

2. Install python dependencies:
   ```shell
   pip install -r requirements.txt
   ```
3. Install npm packages:
   1. Optional: use [nvm](https://github.com/nvm-sh/nvm) to manage node version:
      ```shell
      nvm install
      nvm use
      ```
   2. Install:
      ```shell
      npm install
      ```
4. Build:
   ```shell
   npm run build
   ```

### Component Code

### Publish

If publish on npm:
```shell
npm build
npm publish
```

### Justfile

Alternatively, use the provided [just](https://github.com/casey/just) commands:

1. Create a Python environment from previous step 1 and install:
   ```shell
   just install
   ```
2. Build
   ```shell
   just build
   ```
3. Publish
   ```shell
   just publish
   ```
4. See all commands with `just -l`
