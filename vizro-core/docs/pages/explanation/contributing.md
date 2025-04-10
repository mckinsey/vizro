# Contributing

Contributions of all experience levels are welcome! There are many ways to contribute, and we appreciate any help: it doesn't have to be a pull request (PR) on our code. You can also [report a bug](faq.md#how-can-i-report-a-bug), [request a feature](faq.md#how-can-i-request-a-feature), or [ask and answer community questions](faq.md#i-still-have-a-question-where-can-i-ask-it). Before making significant changes to Vizro code, you should first use [GitHub issues](https://github.com/mckinsey/vizro/issues) to discuss your contribution.

Our development follows a standard [GitHub flow](https://docs.github.com/en/get-started/using-github/github-flow). To be merged, your PR must meet all the following requirements:

- two approving reviews (including a code owner)
- Continuous Integration (CI) checks pass
- code is up-to-date with `main`

If you are a first-time contributor with a new GitHub account then you may also need to [wait for CI workflows to be approved](https://docs.github.com/en/actions/managing-workflow-runs-and-deployments/managing-workflow-runs/approving-workflow-runs-from-public-forks).

We aim to make the contribution process as easy as possible by having only one direct development dependency: [Hatch](https://hatch.pypa.io/). There are two ways to develop on Vizro:

- [GitHub Codespaces](https://docs.github.com/en/codespaces). This is the recommended method if you are a new contributor. It is the quickest and easiest way to get started. All development can be done in your browser in a temporary environment; you do not need to set up anything on your computer. The [Develop on GitHub Codespaces](#develop-on-github-codespaces) section has full instructions on how to do this.
- Local machine. If you are more experienced then you might prefer to develop on your own computer. The [Develop locally](#develop-locally) section has full instructions on how to do this.

!!! note

    For either method, Hatch is the _only development dependency_. You do not need to manually install Python or create any virtual environments to develop Vizro; all this will be handled for you behind the scenes by Hatch. We have also configured our codespace to pre-install Hatch. If you develop on GitHub Codespaces you don't need to install anything at all!

## Develop on GitHub Codespaces

There is no need to manually create a fork of the Vizro code if you use GitHub Codespaces. A fork is [automatically created for you](https://docs.github.com/en/codespaces/developing-in-a-codespace/using-source-control-in-your-codespace#about-automatic-forking).

To develop on [GitHub Codespaces](https://docs.github.com/en/codespaces), follow the below steps:

1. [Create a codespace for our repository](https://codespaces.new/mckinsey/vizro). Leave the settings on their defaults and click "Create codespace" to start your codespace. It should take 1-2 minutes to fully launch and automatically start an example dashboard on port 8050. In the rare event that the codespace fails to start correctly and enters recovery mode, you should [rebuild the container](https://docs.github.com/en/codespaces/developing-in-a-codespace/rebuilding-the-container-in-a-codespace#rebuilding-a-container) or start a whole new codespace.
1. Make changes to Vizro code in your codespace. See the [GitHub Codespaces documentation on developing in a codespace](https://docs.github.com/en/codespaces/developing-in-a-codespace/developing-in-a-codespace) for more information.
1. Add your name to the [list of contributors](authors.md) (source file `vizro-core/docs/pages/explanation/authors.md`).
1. [Create a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork).

## Develop locally

1. Install Hatch. There are [several ways to do this](https://hatch.pypa.io/latest/install/).
1. [Fork the Vizro repository](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo) and clone it to your local machine.
1. Make changes to Vizro code in your fork.
1. Add your name to the [list of contributors](authors.md) (source file `vizro-core/docs/pages/explanation/authors.md`).
1. [Create a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork).

## How to use Hatch

Regardless of whether you are developing locally or in a codespace, everything you need to develop on Vizro is provided by Hatch through the [`hatch run`](https://hatch.pypa.io/latest/cli/reference/#hatch-run) command. The first time you use this command it will install all the required dependencies, including Python.

The Hatch commands you need most commonly are as follows. These must be executed with `vizro-core` as your current working directory:

- [`hatch run pypath`](#hatch-run-pypath) shows the path to the Python interpreter.
- [`hatch run example`](#hatch-run-example) runs an example dashboard on port 8050 that hot-reloads while you edit it. On GitHub Codespaces, this runs automatically on startup.
- [`hatch run lint`](#hatch-run-lint) checks and fixes code quality and formatting. This is included in CI checks.
- [`hatch run changelog:add`](#hatch-run-changelogadd) generates a new changelog fragment. Changelog inclusion is checked by CI and required for all changes to source code.
- [`hatch run test-unit`](#hatch-run-test-unit) runs the test suite. This is included in CI checks.
- [`hatch run docs:serve`](#hatch-run-docsserve) builds and displays documentation that hot-reloads while you edit it. Documentation is also built automatically in your PR and can be previewed on Read The Docs.
- [`hatch run pip`](#hatch-run-pip) provides a [pip-compatible interface using uv](https://docs.astral.sh/uv/pip/). You should not need to use this much.

<!-- vale off-->

To save yourself from repeatedly typing `hatch run` you might like to [set up an alias](https://www.tecmint.com/create-alias-in-linux/):

<!-- vale on-->

```console
alias hr="hatch run"
```

This enables you to run, for example, `hr lint` instead of `hatch run lint`. On GitHub Codespaces, this alias is already set up for you.

### `hatch run pypath`

`hatch run pypath` shows the path to the Python interpreter. This is useful for setting a Python interpreter in your IDE to navigate the codebase. For example, in GitHub Codespaces and VS Code:

- Run `hatch run pypath` and copy the output to your clipboard.
- Open the Command Palette (++ctrl+shift+p++).
- Run the "Python: Select Interpreter" command and select the "Enter interpreter path..." option.
- Paste the path.

### `hatch run example`

`hatch run example` runs an example dashboard on port 8050 that hot-reloads while you edit it. On GitHub Codespaces, this [runs automatically on startup](https://docs.github.com/en/codespaces/developing-in-a-codespace/forwarding-ports-in-your-codespace) and is labeled as `scratch_dev example`. On your local machine, you can access the dashboard by pointing your browser to [http://127.0.0.1:8050](http://127.0.0.1:8050).

By default, this command runs the dashboard configured in `vizro-core/examples/scratch_dev/app.py`. This dashboard is used as a temporary "scratch" playground during development. Since it is opened automatically in GitHub Codespaces, it's the perfect place to show, or test out, a new feature you're developing. PR reviewers can then immediately see exactly what your changes do by opening a codespace on your branch.

You can run any example in `vizro-core/examples` or its subdirectories by running `hatch run example <example_path>`, where `<example_path>` is the path to the directory containing the `app.py` file relative to `vizro-core/examples`. For example, `hatch run example dev` runs a dashboard located at `vizro-core/examples/dev/app.py`. This dashboard demonstrates a full set of Vizro features and is also [hosted on Hugging Face](https://huggingface.co/spaces/vizro/demo-features).

Examples are run with the following settings:

- [Dash dev tools](https://dash.plotly.com/devtools) enabled. This includes hot reloading, so that any changes to the example app or Vizro source code should automatically show in your dashboard without needing refresh or restart anything.
- The environment variable `VIZRO_LOG_LEVEL = "DEBUG"` to show log messages of level `DEBUG` and above.

### `hatch run lint`

`hatch run lint` checks and fixes code quality and formatting. This is included in CI checks. All linting and associated dependencies are controlled by [pre-commit](https://pre-commit.com/) hooks. We use the [pre-commit.ci](https://pre-commit.ci/) to automatically fix all the linting checks that we can when a PR is pushed. Other linting failures (such as `mypy`) need manual intervention from the developer.

!!! note

    The first time you run `hatch run lint` it may take a couple of minutes, since pre-commit needs to setup linting environments. Further runs reuse these environments and are much faster.

`hatch run lint` runs the pre-commit hooks on all (not only staged) files. You can run an individual hook, for example `mypy`, on all files by running `hatch run lint mypy`.

Our Hatch environment specifies `pre-commit` as a dependency but otherwise does not specify dependencies for linting tools. Instead, the versions of these are pinned in `.pre-commit-config.yaml`, and `pre-commit ci` raises a monthly PR to update them.

### `hatch run changelog:add`

`hatch run changelog:add` generates a new changelog fragment. Changelog inclusion is checked by CI and required for all changes to source code.

The format of our changelog is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/). We use [scriv](https://pypi.org/project/scriv/) to build and maintain [our changelog](https://github.com/mckinsey/vizro/blob/main/vizro-core/CHANGELOG.md). When raising a PR, you must ensure that a changelog fragment has been created. This fragment is a small `.md` file describing your changes.

Run `hatch run changelog:add` to create a changelog fragment and then uncomment the relevant section(s). If you are uncertain about what to add or whether to add anything at all, refer to [Keep a Changelog](https://keepachangelog.com/en/1.0.0/). The rule of thumb is that if Vizro users would be affected in any way then the changes should be described in the changelog.

!!! note

    Changes that do not affect source code do not need a changelog fragment. This simplifies modifications to documentation [made directly on GitHub](https://docs.github.com/en/repositories/working-with-files/managing-files/editing-files) or within the [github.dev](https://docs.github.com/en/codespaces/the-githubdev-web-based-editor), where no terminal is available to run `hatch changelog:add`. Any changes to source code require a changelog fragment to be generated. If your changes do not require a changelog entry then you still need to generate the fragment but can leave it all commented out.

### `hatch run test-unit`

`hatch run test-unit` runs the test suite. This is included in CI checks.

Tests are handled using [pytest](https://docs.pytest.org/) and arguments are passed through to the underlying `pytest` command. For example, to rerun only failures from the last `pytest` invocation, you could run:

```console
hatch run test-unit --last-failed
```

In CI, we test across multiple Python versions and also [check for code coverage](https://coverage.readthedocs.io/). If required, you can also run this locally. For example, to run unit tests with Python 3.10 and check for code coverage, you would run:

```console
hatch run all.py3.10:test-unit-coverage
```

In addition to running unit tests with code coverage, CI also performs the following checks:

- `hatch run test-integration` runs integration tests that include checking that the example apps in `vizro-core/examples` run.
- `hatch run test-js` runs Javascript tests using [jest](https://jestjs.io/). Arguments are passed through to the underlying `npx jest` command, for example `hatch run test-js --help`.
- QA tests. These are run on a separate private `vizro-qa` repository and not triggered by PRs coming from forks.

### `hatch run docs:serve`

`hatch run docs:serve` builds and displays documentation that hot-reloads while you edit it. Documentation is also built automatically in your PR and can be previewed on Read The Docs. To do this, scroll to the bottom of your PR where all the checks are listed and click the "Details" link next to the Read the Docs build.

For more information on our documentation style, refer to our [style guide](documentation-style-guide.md).

### `hatch run pip`

`hatch run pip` provides a [pip-compatible interface using uv](https://docs.astral.sh/uv/pip/). You should not need to use this often.

Vizro's dependencies are described by the `dependencies` section in `vizro-core/pyproject.toml`. There is no need to manually install or update the dependencies in your environment; they will be handled automatically for you when you do `hatch run`. This means that there is usually no need to `pip install` anything.

We have [configured Hatch to use uv](https://hatch.pypa.io/1.12/how-to/environment/select-installer/) for rapid virtual environment creation, dependency resolution and installation.

!!! note

    If you have installed unwanted dependencies in your Hatch environment then the simplest solution is to delete the environment (`hatch env remove` to remove one environment or `hatch env prune` to remove all environments). Your next `hatch run` command will recreate the environment and install all the dependencies it needs.

If for some reason you do need to use `pip` then the correct way to do so is through `hatch run pip`. For example, you could run `hatch run pip show plotly`. This will use the version of uv that Hatch itself uses under the hood. If you already have uv installed globally then `uv pip show plotly` would also work.

!!! warning

    You should not try to interact with Vizro dependencies using a global `pip`. For example, running `pip show plotly` without the `hatch run` prefix will not work correctly.

## Code of conduct

The Vizro team pledges to foster and maintain a friendly community. We enforce a [Code of Conduct](https://github.com/mckinsey/vizro/tree/main/CODE_OF_CONDUCT.md) to ensure every Vizro contributor is welcomed and treated with respect.
