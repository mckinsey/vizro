# Contribution guidelines

Thank you for your interest in contributing to Vizro! Our development follows a standard [GitHub flow](https://docs.github.com/en/get-started/using-github/github-flow). We have aimed to make the contribution process as frictionless as possible by having only one direct development dependency, [Hatch](https://hatch.pypa.io/).

There are two ways to develop on Vizro:
* [GitHub Codespaces](https://docs.github.com/en/codespaces). This is the recommended method if you are a new contributor and is the quickest and easiest way to get started with development on Vizro. All development can be done in your browser in an ephemeral environment; you do not need to set up anything on your computer. Read [Develop on GitHub Codespaces](#develop-on-github-codespaces) for full instructions on how to do this.
* Local machine. If you are more experienced then you might prefer to develop on your own computer. Read [Develop locally](#develop-locally) for full instructions on how to do this.

!!! note

    With both routes, Hatch is the _only development dependency_. You do not need to manually install Python or create any virtual environments; all this will be handled for you behind the scenes by Hatch. We have configured our codespace to pre-install Hatch, so if you develop on GitHub Codespaces then you don't need to install _anything_ at all!


## Develop on GitHub Codespaces

To develop on [GitHub Codespaces](https://docs.github.com/en/codespaces), follow the below steps:

1. Use our [GitHub issues](https://github.com/mckinsey/vizro/issues) to discuss your contribution.
2. Create a codespace for our repository by clicking the following badge: [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/mckinsey/vizro). This should take 1-2 minutes to complete and will automatically start an example dashboard on port 8050.
3. Make changes in your codespace and [create a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork). See the [GitHub Codespaces documentation on developing in a codebase](https://docs.github.com/en/codespaces/developing-in-a-codespace/developing-in-a-codespace) for more information.
4. Add your name to the [authors.md](list of code contributors) (source file `vizro-core/docs/pages/explanation/authors.md`).
5. Before it can be merged, your pull request must meet all the following requirements:
  * Two approving reviews (including a code owner).
  * Continuous Integration (CI) checks pass.
  * Up-to-date with `main`.

!!! note

    There is no need to manually create a fork if you use GitHub Codespaces; a fork is [created automatically for you](https://docs.github.com/en/codespaces/developing-in-a-codespace/using-source-control-in-your-codespace#about-automatic-forking)).
    
## Develop locally

1. Use our [GitHub issues](https://github.com/mckinsey/vizro/issues) to discuss your contribution.
2. Install Hatch. There are [several ways to do this](https://hatch.pypa.io/latest/install/). 
3. [Create a fork of the repository](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo) and clone it to your local machine.
4. Make changes in your fork and [create a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork).
5. Add your name to the [authors.md](list of code contributors) (source file `vizro-core/docs/pages/explanation/authors.md`).
6. Before it can be merged, your pull request must meet all the following requirements:
  * Two approving reviews (including a code owner).
  * Continuous Integration (CI) checks pass.
  * Up-to-date with `main`.

## How to use Hatch

Regardless of whether you are developing locally or in a codespace, everything you need to develop on Vizro is provided by Hatch through the [`hatch run`](https://hatch.pypa.io/latest/cli/reference/#hatch-run) command. The first time you use this command it will install all the required dependencies, including Python.

The commands you might need are as follows. These must be executed with `vizro-core` directory as your current working directory. Click on the command to read more detailed information about it. 

* [`hatch run pypath`](#hatch-run-pypath) shows the path to the Python interpeter.
* [`hatch run example`](#hatch-run-example) runs a hot-reloading example dashboard on port 8050. On GitHub codespaces, this runs automatically on startup.
* [`hatch run lint`](#hatch-run-lint) checks and fix code quality and formatting. This is included in CI checks.
* [`hatch run changelog:add`](#hatch-run-changelogadd) generates a new changelog fragment. This is included in CI checks and required for all changes outside documentation.
* [`hatch run test-unit`](#hatch-run-test-unit) runs the test suite. This is included in CI checks.
* [`hatch run docs:serve`](#hatch-run-docsserve) shows hot-reloading documentation. Documentation is also built automatically in your pull request and can be previewed on Read The Docs.
* [`hatch run pip`](#hatch-run-pip) provides a [pip-compatible interface using uv](https://docs.astral.sh/uv/pip/). You should not need to use this much.

To save yourself from repeatedly typing `hatch run` you might like to [set up an alias](https://www.tecmint.com/create-alias-in-linux/):

```bash
alias hr="hatch run"
```

This enables you to run, for example, `hr lint`, instead of `hatch run lint`. On GitHub codespaces, this alias is already set up for you.

### `hatch run pypath`

`hatch run pypath` show the path to the Python interpreter. This is useful for setting a Python interpreter in your development environment to help navigate the codebase. For example, in GitHub Codespaces and VS Code:
* Run `hatch run pypath` and copy the output to your clipboard.
* Open the Command Palette (Ctrl+Shift+P).
* Run the "Python: Select Interpreter" command and select the "Enter interpreter path..." option.
* Paste the path.

### `hatch run example`

`hatch run example` runs a hot-reloading example dashboard on port 8050. On GitHub Codespaces, this runs automatically on startup. On your local machine, you can access the dashboard by pointing your browser to [http://localhost:8050](http://localhost:8050). 

By default, this command runs the dashboard specified in `vizro-core/examples/scratch_dev`. This dashboard is used as a temporary playground during development and can be merged to `main` in any form. Since it is opened automatically in GitHub Codespaces, it's the perfect place to demonstrate or test out a new feature you're developing. Pull request reviewers can then immediately see exactly what your changes do by opening a codespace on your branch.

You can run any example in `vizro-core/examples` or its subdirectories by running `hatch run example <example_path>`. For example, `hatch run example dev` runs a dashboard located at `vizro-core/examples/dev/app.py` that demonstrates a full set of Vizro features. This is also [hosted on Hugging Face](https://huggingface.co/spaces/vizro/demo-features).

Examples are run with the following settings:
* [Dash dev tools](https://dash.plotly.com/devtools) enabled. This includes hot reloading, so that any changes to the example app or Vizro source code should automatically show in your dashboard without needing refresh or restart anything.
* `VIZRO_LOG_LEVEL = "DEBUG"` to show log messages of level `DEBUG` and above.

### `hatch run lint`

`hatch run lint` checks and fixes code quality and formatting. This is included in CI checks. All linting and associated dependencies is controlled by [pre-commit](https://pre-commit.com/) hooks. We use [`pre-commit ci`](https://pre-commit.ci/) to automatically fix all the linting checks that we can when a pull request is pushed. Other linting failures (such as `mypy`) need manual intervention from the developer.

`hatch run lint` runs the `pre-commit` hooks on all (not just staged) files. You can run an individual hook, for example `mypy`, by running `hatch run lint mypy`.

!!! note

    The first time you run `hatch run lint` it may take a couple of minutes, since pre-commit needs to setup linting environments. Subsequent runs re-use these environments and will be much faster. 

Our Hatch environment specifies `pre-commit` as a dependency but otherwise does not specify dependencies for linting tools. The versions of these are pinned in `.pre-commit-config.yaml`, and `pre-commit ci` raises a monthly pull request to update them.

We use [gitleaks](https://github.com/gitleaks/gitleaks) for secret scanning, which may require an [installation of `go`](https://go.dev/doc/install). By default, `hatch run lint` skips the secret scans so that it can function out of the box on all machines. To run a secret-scan, run `hatch run secrets`. When executing the secret scan, there are two modes: `protect`, which can discover secrets in staged files, and `detect`, which does so in the commit history.

### `hatch run changelog:add`

`hatch run changelog:add` generates a new changelog fragment. This is included in CI checks and required for all changes outside documentation.

The format of our changelog is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/). We use [scriv](https://pypi.org/project/scriv/) to build and maintain `CHANGELOG.md`. When raising a pull request, you  must ensure that a changelog fragment has been created. This fragment is a small `.md` file describing your changes.

Run `hatch run changelog:add` to create a changelog fragment and then uncomment the relevant section(s). If you are uncertain about what to add or whether to add anything at all, refer to [Keep a Changelog](https://keepachangelog.com/en/1.0.0/). The rule of thumb is that if Vizro users would be affected in any way then the changes should be described in the changelog.

!!! note

    Changes that only affect documentation do not need a changelog fragment. This facilitates simple modifications to documentation [made directly on GitHub](https://docs.github.com/en/repositories/working-with-files/managing-files/editing-files) or with the [github.dev](https://docs.github.com/en/codespaces/the-githubdev-web-based-editor), where no terminal is available to run hatch commands. Any changes outside documentation require a changelog fragment to be generated. If your changes do not require a changelog entry then you still need to generate the fragment but can leave it all scommented out.

### `hatch run test-unit`

`hatch run test-unit` runs the test suite. This is included in CI checks.

Tests are handled using [`pytest`](https://docs.pytest.org/) and arguments are passed through to the underlying `pytest` command. For example, to rerun only failures from the last `pytest` invocation, you could do:
```console
hatch run test-unit --last-failed
```

In CI, we test across multiple Python versions and also [check for code coverage](https://coverage.readthedocs.io/). If required, you can also run this locally. For example, to run unit tests with Python 3.10 and check for code coverage, you would run:
```console
hatch run all.py3.10:test-unit-coverage
```

CI also does the following:
* `hatch run test-integration` runs integration tests that includes checking the example apps in `vizro-core/examples` run.
* `hatch run test-js` runs Javascript tests using [`jest`](https://jestjs.io/) frameworks. Arguments are passed through to the underlying `npx jest` command, for example `hatch run test-js --help`.
* QA tests. These are run on a separate private `vizro-qa` repository and not triggered by pull requests coming from forks.

### `hatch run docs:serve`

[`hatch run docs:serve`](#hatch-run-docsserve) shows hot-reloading documentation. Documentation is also built automatically in your pull request and can be previewed on Read The Docs. To do this, scroll to the bottom of your pull request where all the checks are listed and click the "Details" link next to the Read the Docs build.

For more information on our documentation style, refer to our [style guide](documentation-style-guide.md).

### `hatch run pip`

[`hatch run pip`](#hatch-run-pip) provides a [pip-compatible interface using uv](https://docs.astral.sh/uv/pip/). You should not need to use this much.

Vizro's dependencies are described by the `dependencies` section of in `vizro-core/pyproject.toml`. There is no need to manually install or update the dependencies in your environment; they will be handled automatically for you when you next do `hatch run`. This means that there is generally no need to `pip install` anything.

We have [configured Hatch to use uv](https://hatch.pypa.io/1.12/how-to/environment/select-installer/) for virtual environment creation, dependency resolution and installation. This is extremely fast. If you have installed unwanted dependencies in your Hatch environment then the simplest solution is to delete the environment (`hatch env remove` to remove one environment or `hatch env prune` to remove all environments). Your next `hatch run` command will quickly recreate the environment and all the install dependencies it needs.

If you do need use `pip` then the correct way to do so is through `hatch run pip`. For example, you could run `hatch run pip show plotly`. This will use the version of uv that Hatch itself uses under the hood. If you already have uv installed globally then `uv pip show plotly` would also work.

You _should not_ try to interact with Vizro dependencies using a global `pip`. For example, running `pip show plotly` without the `hatch run` prefix will not work correctly.

## Code of conduct

The Vizro team pledges to foster and maintain a friendly community. We enforce a [Code of Conduct](https://github.com/mckinsey/vizro/tree/main/CODE_OF_CONDUCT.md) to ensure every Vizro contributor is welcomed and treated with respect.
