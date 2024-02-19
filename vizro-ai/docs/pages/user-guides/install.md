# How to install Vizro-AI

This guide offers instructions on installing Vizro-AI and provides comprehensive explanation on how to install, update and verify the current version of Vizro-AI.

## Prerequisites

- **Python**: Vizro-AI supports macOS, Linux, and Windows. It is designed to work with Python 3.8 and above. The python
  version can be specified when setting up your virtual environment.
- **Virtual environment**: We recommend creating a new virtual environment for each new Vizro-AI project you work on to
  isolate the Python dependencies from those of other projects. To learn more, please see the following references about [python virtual environments](https://realpython.com/python-virtual-environments-a-primer/), [conda virtual environments](https://docs.conda.io/projects/conda/en/latest/user-guide/getting-started.html#starting-conda) or [watch an explainer video about them](https://youtu.be/YKfAwIItO7M).
- **OpenAI API Key**: Using Vizro-AI requires an API key, which you can get by creating an account [here](https://platform.openai.com/account/api-keys). (Users are recommended to review the third party API key section of the [disclaimer](../explanation/disclaimer.md) documentation.
). Once you have your API key, the next step is to set your environment variable by:
```bash
export OPENAI_API_KEY="..."
```


More details can be found in the [environment setup guide](../user_guides/api_setup.md).

??? tip "Beginners/Code novices"
    If you are a beginner or new to coding and wish to avoid using the terminal, you can follow these steps:

    - Install [Anaconda Navigator](https://www.anaconda.com/download)
    - Create a new environment as detailed [here](https://docs.anaconda.com/free/navigator/tutorials/manage-environments/), and select a Python version `>=3.8`

## Install

To install Vizro-AI from the Python Package Index (PyPI), utilize [`pip`](https://pip.pypa.io/en/stable/) in your terminal with the following command:

```bash
pip install vizro_ai
```

While you can execute code from the tutorials and user guides using a Python script, using a Jupyter notebook is often considered more convenient. You can install `jupyter` with the following command:

```bash
pip install jupyter
```

??? tip "Beginners/Code novices"
    If you're new to coding or consider yourself a beginner, you can follow these following steps to avoid using the terminal:

    - Search `vizro_ai` and install it using the Anaconda Navigator package manager. You can find instructions [here](https://docs.anaconda.com/free/navigator/tutorials/manage-packages/)
    - Similarly, search `jupyter` and install it through the same procedure
    - Once installed, launching a Jupyter notebook becomes straightforward; you can find guidance [here](https://problemsolvingwithpython.com/02-Jupyter-Notebooks/02.04-Opening-a-Jupyter-Notebook/#open-a-jupyter-notebook-with-anaconda-navigator)
    - With Jupyter, you can easily copy and paste any of the provided examples into a notebook cell, evaluate the cell, and examine the results

## Verify version

After successfully installing Vizro-AI, to verify the version or confirm the installation, you can run the following code from a Python script or a Jupyter notebook cell:

```py
import vizro_ai

print(vizro_ai.__version__)
```

You should see a return output of the current version.

## Upgrade

If you want to upgrade Vizro-AI to a different version later on, you can do so by running the following command:
```
pip install vizro_ai -U
```

The best way to safely upgrade is to check the [release notes]() for any notable breaking changes before migrating an
existing project.
