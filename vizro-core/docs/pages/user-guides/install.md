# How to install Vizro

Thanks to [PyCafe](https://py.cafe/) you can create Vizro dashboards without installing Vizro locally, as you can see from the [first dashboard tutorial](../tutorials/first-dashboard.md) (you can find out more about [working with PyCafe and Vizro](https://py.cafe/docs/apps/vizro) from the PyCafe documentation).

If you prefer to work locally, this guide shows you how to install Vizro, how to verify the installation succeeded and find the version of Vizro, and how to update Vizro.

We recommend that you create a virtual environment for each Vizro project you work on to isolate its Python dependencies from other projects. If you already have a virtual environment you can skip the next section and [install Vizro](#install-vizro). Otherwise, read on!

## Prerequisites to working locally

* **Python**: Vizro supports macOS, Linux, and Windows. It works with Python 3.9 and later.
* **Virtual environment**: You specify the version of Python to use with Vizro when you set up the virtual environment. See the following references to learn more about [Python virtual environments](https://realpython.com/python-virtual-environments-a-primer/), [Conda virtual environments](https://docs.conda.io/projects/conda/en/latest/user-guide/getting-started.html#starting-conda) or [watch an explainer video about them](https://youtu.be/YKfAwIItO7M).

### How to create a virtual environment for your Vizro project

The simplest way to create a virtual environment in Python is `venv`, which is included in the Python standard library. Create a directory for your project and navigate to it. For example:

```bash
mkdir vizro-project
cd vizro-project
```

Next, create and activate a new virtual environment in this directory with `venv`:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

You might like to use [`conda` as your virtual environment manager](https://docs.conda.io/projects/conda/en/latest/user-guide/install/). Once installed, you can create and activate a virtual environment from the terminal as follows:

```bash
conda create --name vizro-environment
conda activate vizro-environment
```

## Install Vizro

To install Vizro, use [`pip`](https://pip.pypa.io/en/stable/) in your terminal window:

```bash
pip install vizro
```

## Confirm a successful installation

To confirm the installation was successful and verify the version of Vizro installed, call the following. You can do this from within a Jupyter Notebook cell, or run the following as a Python script:

```py
import vizro

print(vizro.__version__)
```

You should see a return output of the form `x.y.z`.

## Upgrade

Check the [release notes](https://github.com/mckinsey/vizro/blob/main/vizro-core/CHANGELOG.md) for any notable breaking changes before migrating an existing project.

To change the version of Vizro installed:

```bash
pip install -U vizro
```
