## Contributing guidelines

Contributions of all experience levels are welcome! There are many ways to contribute, and we appreciate all of them. We are still defining a detailed process, but for the time being, please use our [issues page](https://github.com/mckinsey/vizro/issues) to discuss any contributions.

### Found a bug

Great! We would appreciate if you could head to our [issues page](https://github.com/mckinsey/vizro/issues) and raise a ticket in the category `bug report`. We would appreciate if you searched the existing issues for a similar description before raising a new ticket. We will try to reproduce your reported bug as soon as possible before getting back to you on next steps.

### Request a feature

Splendid! In order to raise a feature request, please head to our [issues page](https://github.com/mckinsey/vizro/issues) and raise a ticket in the category `feature request`. We would appreciate if you searched the existing issues for a similar description before raising a new ticket. We will get back to you as soon as possible with an estimate of whether and when this feature could be released.

## How to interact with the repository

The easiest way to get up and running quickly is to [open the repository in GitHub Codespaces](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=626855142). This will create a temporary development environment with all the necessary configurations, making it especially convenient for tasks like reviewing pull requests.

We use [Hatch](https://hatch.pypa.io/) as a project management tool. To get started on your own machine, you should complete the following steps. Note there is _no need to set up your own virtual environment_ since Hatch takes care of that for you.

1. [Install `hatch`](https://hatch.pypa.io/latest/install/) by running `brew install hatch` or `pipx install hatch` (preferable to `pip install hatch`).
2. Clone this repository.
3. Run `hatch -v env create` from the `vizro-core` folder of your cloned repository. This creates Hatch's `default` environment with dependencies installed and the project installed in development mode (i.e. using `pip install --editable`). It will take a few minutes to complete. All following commands should be executed from this folder as well.
4. Run `hatch run example` to open an [example Vizro dashboard](#examples) with [Dash dev tools](https://dash.plotly.com/devtools) enabled.
5. Edit the code to your heart's desire! Thanks to Dash dev tools' hot reloading, any changes to the example app or `vizro` source code should automatically show in your dashboard without needing refresh or restart any process.

!!!note

    The above steps are all automated in GitHub Codespaces thanks to the [devcontainer configuration](.devcontainer/devcontainer.json), and the example dashboard should already be running on port `8050`.

    If you haven't used Hatch before, it's well worth skimming through [their documentation](https://hatch.pypa.io/), in particular the page on [environments](https://hatch.pypa.io/latest/environment/). Run `hatch env show` to show all of Hatch's environments and available scripts, and take a look at [`hatch.toml`](https://github.com/mckinsey/vizro/tree/main/vizro-core/hatch.toml) to see our Hatch configuration. It is useful handy to [Hatch's tab completion](https://hatch.pypa.io/latest/cli/about/#tab-completion) to explore the Hatch CLI.

---

## Examples

Several example dashboards are given in [examples](https://github.com/mckinsey/vizro/tree/main/vizro-core/examples). To run, for instance, the `from_dict` example, execute:

```console
hatch run example from_dict
```

If no example is specified (`hatch run example`) then the [default example](https://github.com/mckinsey/vizro/tree/main/vizro-core/examples/default/app.py) is used.

## Debugging tips

- [Dash dev tools](https://dash.plotly.com/devtools) are enabled in all the Hatch environments by setting environment variable `DASH_DEBUG = "true"`, and so there is no need to specify `debug=True` when calling `Vizro.run` to enable them. The reload functionality, callback graph and in-browser error messages are particularly useful.
- All Hatch environments also have `VIZRO_LOG_LEVEL = "DEBUG"` to show log messages of level `DEBUG` and above.

## Testing

Tests are handled using the [`pytest`](https://docs.pytest.org/) framework, and test environments are managed by Hatch. To run all tests, run

```console
hatch run test
```

To run only unit tests, run `hatch run test-unit` and for integration tests only, run `hatch run test-integration`. Note that the latter executes all examples in separate testing sessions due to [this](https://github.com/mckinsey/vizro/issues/10) issue by providing the `-k` tag per example.

Arguments are passed through to the underlying `pytest` command, e.g.

```console
hatch run test -vv
```

executes `pytest -vv` using the Python version in your `default` environment. To run tests against multiple Python versions, use the `all` environment by running:

```console
hatch run all:test -vv
```

To run tests against a particular Python version, specify the particular Hatch environment for that version:

```console
hatch run all.py3.10:test -vv
```

The script executed by `hatch run cov` measures test coverage and generates a report.

<!-- ## Documentation

The diagram `docs/assets/diagram.png` is generated with `hatch run docs:diagram` (currently commented out). The documentation (and current changes) can be served locally by running `hatch run docs:serve`. -->

## Schema

The JSON schema in [`schemas`](https://github.com/mckinsey/vizro/tree/main/vizro-core/schemas) is generated with `hatch run schema`. We ensure this is kept up to date with a check in CI.

## Pre-commit hooks (for linting etc.)

All linting and associated dependencies are controlled by [pre-commit](https://pre-commit.com/) hooks and specified in [.pre-commit-config.yaml](https://github.com/mckinsey/vizro/blob/main/.pre-commit-config.yaml). Configuration for tools is additionally given in [`pyproject.toml`](https://github.com/mckinsey/vizro/blob/main/pyproject.toml), e.g.

```toml
[tool.black]
target-version = ["py37"]
line-length = 120
```

Linting checks are enforced in CI. To run pre-commit hooks locally, there are two options:

1. Run `hatch run pre-commit install` to automatically run the hooks on every commit (you can always skip the checks with `git commit --no-verify`). In case this fails due to `gitleaks`, please read below for an explanation and how to install `go`.
2. Run `hatch run lint` to run `pre-commit` hooks on all files. (You can run eg `hatch run lint mypy` to only run specific linters, here mypy.)

Note that Hatch's `default` environment specifies `pre-commit` as a dependency but otherwise _does not_ specify dependencies for linting tools such as `black`. These are controlled by [.pre-commit-config.yaml](https://github.com/mckinsey/vizro/blob/main/.pre-commit-config.yaml) and can be updated when required with `pre-commit autoupdate`.

## Secret scans

We use [gitleaks](https://github.com/gitleaks/gitleaks) for secret scanning. We do this via `pre-commit`, however there are a few things to note:

1. Using `gitleaks` may require an installation of `go` on the developer machine. This is easy and explained [here](https://go.dev/doc/install).
2. For that reason `hatch run lint` skips the secret scans, to function on all machines.
3. To run a secret-scan, simply run `hatch run secrets`.
4. Secret scans will run on CI, but it is highly recommended to check for secrets **before pushing to the remote repository** and ideally also before even committing.

When executing the secret scan, there are two modes: `protect` can discover secrets in staged files, `detect` does so in the commit history.

## Snyk and `requirements.txt`

[Snyk](https://snyk.io/) is used to scan for vulnerabilities in dependencies. This
is done by scanning the `requirements.txt` file. As Hatch manages the dependencies by
`pyproject.toml`, we need to convert the dependencies to `requirements.txt` before Snyk
can scan them. This is done by running `hatch run update-snyk-requirements`. The outputs are
written to `snyk/requirements.txt`, which can be used by Snyk to scan for vulnerabilities.

We also validate whether the dependencies in `requirements.txt` are up-to-date. This
is done in CI.

Note that `requirements.txt` is not used by Hatch, and so it should not be edited
manually for dependency management. Instead, edit `pyproject.toml` or `hatch.toml` when
adding or removing dependencies.

## Changelog

Vizro uses [scriv](https://pypi.org/project/scriv/) to build and maintain a meaningful `CHANGELOG.md`. When creating a PR, the developer needs to ensure that
a changelog fragment has been created in the folder `changelog.d`. This fragment is a small `.md` file describing the changes of the current PR that should be mentioned in the `CHANGELOG.md` entry of the next release.

You can easily create such a fragment by running

```bash
hatch run docs:changelog
```

and then uncommenting the relevant section(s) you want to describe. In case your PR does not contain `CHANGELOG.md` relevant changes, leave everything commented out.

## Releases

Vizro's version is given by `__version__` in [`src/vizro/__init__.py`](https://github.com/mckinsey/vizro/blob/main/vizro-core/src/vizro/__init__.py). To bump the version, run, e.g. `hatch version minor`. See [Hatch's documentation](https://hatch.pypa.io/latest/version/) for more details.

To build the source distribution and wheel, run `hatch build`.

## Code of conduct

The Vizro team pledges to foster and maintain a friendly community. We enforce a [Code of Conduct](https://github.com/mckinsey/vizro/tree/main/CODE_OF_CONDUCT.md) to ensure every Vizro contributor is welcomed and treated with respect.

## FAQ

### How do I add a dependency?

Add it to the list of `dependencies` in `hatch.toml` (if you are adding a dependency for development) or in `pyproject.toml` (if you are adding a dependency for the actual package). The next time the `default` environment is used (e.g. with `hatch shell`), the dependency will be automatically installed.

### What about a lock file?

We do not have and should not need a dependency lock file (see [this Hatch FAQ](https://hatch.pypa.io/latest/meta/faq/#libraries-vs-applications)). If one is for some reason eventually required, good options would be [pip-tools](https://github.com/jazzband/pip-tools), [`hatch-pip-deepfreeze`](https://github.com/sbidoul/hatch-pip-deepfreeze) or just `pip freeze`.

### How do I find the path to the Python executable used?

`hatch run pypath` displays the path to the Python executable used in the `default` environment. This is useful e.g. for setting up a run configuration in PyCharm.

### Why are we using a line length of 120 characters?

This is the default value set in the Hatch template, and it feels sensible in the era of big screens. Line lengths can be discussed endlessly but ultimately this number should be agreed on by the Vizro team. See also [this article](https://knox.codes/posts/line-length-limits).

## Further reading and credits

Our toolchain and repo structure is influenced by the following templates:

- `hatch new` template
- [`copier-pylib`](https://github.com/astrojuanlu/copier-pylib)
- [`cookiecutter-hypermodern-python`](https://github.com/cjolowicz/cookiecutter-hypermodern-python) and associated [user guide](https://cookiecutter-hypermodern-python.readthedocs.io/)
- [`scikit-hep/cookie`](https://github.com/scikit-hep/cookie) and associated [developer guidelines](https://scikit-hep.org/developer)

Further useful articles:

- [The basics of Python packaging in early 2023](https://drivendata.co/blog/python-packaging-2023)

Special thanks to [Juan Luis Cano Rodríguez](https://github.com/astrojuanlu) for useful discussions.
