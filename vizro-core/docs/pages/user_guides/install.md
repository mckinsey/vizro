# How to install Vizro

This guide shows you how to install Vizro. It will provide detailed explanation on how to install, update and verify the current version of vizro.

## Prerequisites

- **Python**: Vizro supports macOS, Linux, and Windows. It is designed to work with Python 3.8 and above. The python
  version can be specified when setting up your virtual environment.
- **Virtual environment**: We suggest to create a new virtual environment for each new Vizro project you work on to
  isolate its Python dependencies from those of other projects. See the following references to learn more about [python virtual environments](https://realpython.com/python-virtual-environments-a-primer/), [conda virtual environments](https://docs.conda.io/projects/conda/en/latest/user-guide/getting-started.html#starting-conda) or [watch an explainer video about them](https://youtu.be/YKfAwIItO7M).


??? tip "Beginners/Code novices"
    If you consider yourself a beginner or coding novice, you can follow the steps in these boxes to completely avoid the terminal usage

    - install the [Anaconda Navigator](https://www.anaconda.com/download)
    - create a new environment as [outlined here](https://docs.anaconda.com/free/navigator/tutorials/manage-environments/), choose a Python version `>=3.8`

## Install

To install Vizro from the Python Package Index (PyPI), use [`pip`](https://pip.pypa.io/en/stable/) in your terminal window:

```bash
pip install vizro
```

You can run any code from the tutorials and user guides using a python script, but it is arguably more convenient to use a Jupyter notebook. In this case you can optionally install `jupyter`:
```bash
pip install jupyter
```

??? tip "Beginners/Code novices"
    If you consider yourself a beginner or coding novice, you can follow the steps in these boxes to completely avoid the terminal usage

    - search `vizro` and subsequently install it [using the Anaconda Navigator package manager](https://docs.anaconda.com/free/navigator/tutorials/manage-packages/ )
    - search `jupyter` and subsequently install it following the same procedure
    - it should now be easy to [launch a jupyter notebook](https://problemsolvingwithpython.com/02-Jupyter-Notebooks/02.04-Opening-a-Jupyter-Notebook/#open-a-jupyter-notebook-with-anaconda-navigator)
    - you can paste any of the examples into a notebook cell, evaluate the cell and inspect the results - happy vizro'ing!


## Verify version

Once Vizro is installed, if you would like to verify the version of Vizro or check if everything worked, simply run the following code from a python script or a Jupyter notebook cell:

```py
import vizro

print(vizro.__version__)
```

You should see a return output of the form `0.1.0`.

## Upgrade

To later upgrade Vizro to a different version, simply run:
```
pip install vizro -U
```

The best way to safely upgrade is to check the [release notes](https://github.com/mckinsey/vizro/blob/main/vizro-core/CHANGELOG.md) for any notable breaking changes before migrating an
existing project.
