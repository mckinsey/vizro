# How to install Vizro

This guide shows you how to install Vizro, how to verify the installation succeeded and find the version of Vizro, and how to update Vizro.

If you already have a virtual environment setup in Python then you can skip this page and install Vizro straight away by running:
```bash
pip install vizro
```

## Prerequisites

**Python**: Vizro supports macOS, Linux, and Windows. It works with Python 3.8 and later. You can specify the version of Python to use with Vizro when you set up a virtual environment.


**Virtual environment**: You should create a virtual environment for each Vizro project you work on to
  isolate its Python dependencies from those of other projects. See the following references to learn more about [Python virtual environments](https://realpython.com/python-virtual-environments-a-primer/), [Conda virtual environments](https://docs.conda.io/projects/conda/en/latest/user-guide/getting-started.html#starting-conda) or [watch an explainer video about them](https://youtu.be/YKfAwIItO7M).

!!! tip "Prefer to use Vizro without opening a terminal window?"

    If you are a beginner or coding novice, you may prefer to avoid using a terminal to work with Vizro. Skip to the ["Use Vizro inside Anaconda" section](#use-vizro-inside-anaconda-navigator) below.



??? information "How to create a virtual environment for your Vizro project"

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

    Alternatively, you might like to use [`conda` as your virtual environment manager](https://docs.conda.io/projects/conda/en/latest/user-guide/install/). Once installed, you can create and activate a virtual environment from the terminal as follows:

    ```bash
    conda create --name vizro-environment
    conda activate vizro-environment
    ```


## Install Vizro

To install Vizro, use [`pip`](https://pip.pypa.io/en/stable/) in your terminal window:

```bash
pip install vizro
```

## Use Vizro inside Anaconda Navigator

To completely avoid terminal usage, follow these steps to work with Vizro:


1. Install [Anaconda Navigator](https://www.anaconda.com/download).

2. Create a new environment as [outlined in the Anaconda documentation](https://docs.anaconda.com/free/navigator/tutorials/manage-environments/). Choose a Python version `>=3.8`.

3. Search `vizro` and install it [using the Anaconda Navigator package manager](https://docs.anaconda.com/free/navigator/tutorials/manage-packages/).

4. Similarly, search `jupyter` and install it.

5. [Launch a Jupyter Notebook](https://problemsolvingwithpython.com/02-Jupyter-Notebooks/02.04-Opening-a-Jupyter-Notebook/#open-a-jupyter-notebook-with-anaconda-navigator) to work with Vizro.


## Confirm a successful installation

To confirm the installation was successful, and verify the version of Vizro installed, call the following. You can do this from within a Jupyter Notebook cell, or run the following as a Python script:

```py
import vizro

print(vizro.__version__)
```

You should see a return output of the form `x.y.z`.

## Upgrade

To change the version of Vizro installed:

```bash
pip install -U vizro
```

!!! tip Check the Vizro release notes

    To upgrade safely, check the [release notes](https://github.com/mckinsey/vizro/blob/main/vizro-core/CHANGELOG.md) for any notable breaking changes before migrating an existing project.
