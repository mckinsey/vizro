# How to install Vizro

This guide shows you how to install Vizro, how to verify the installation succeeded and find the version of Vizro, and how to update Vizro.

## Prerequisites

**Python**: Vizro supports macOS, Linux, and Windows. It works with Python 3.8 and later. You can specify the version of Python to use with Vizro when you set up a virtual environment.


**Virtual environment**: You should create a virtual environment for each Vizro project you work on to
  isolate its Python dependencies from those of other projects. See the following references to learn more about [Python virtual environments](https://realpython.com/python-virtual-environments-a-primer/), [Conda virtual environments](https://docs.conda.io/projects/conda/en/latest/user-guide/getting-started.html#starting-conda) or [watch an explainer video about them](https://youtu.be/YKfAwIItO7M). 

!!! tip "Prefer to use Vizro without opening a terminal window?"
    
    If you are a beginner or coding novice, you may prefer to avoid using a terminal to work with Vizro. Skip to the ["Use Vizro inside Anaconda" section](#use-vizro-inside-anaconda-navigator) below.

    

??? information "How to create a virtual environment for your Vizro project"

    ### Using `conda`
    We strongly recommend [installing `conda` as your virtual environment manager](https://docs.conda.io/projects/conda/en/latest/user-guide/install/) if you don't already use it. Once installed, create a virtual environment from the terminal as follows:

    ```bash
    conda create --name vizro-environment python=3.10 -y
    ```

    (This example uses Python 3.10, and creates a virtual environment called `vizro-environment`. You can opt for a different version of Python (any version >= 3.8 and <3.12), and name it anything you choose).

    Activate your virtual environment from any directory:

    ```bash
    conda activate kedro-environment
    ```

    To confirm that a valid version of Python is installed in your virtual environment, type the following in your terminal (macOS and Linux):

    ```bash
    python3 --version
    ```

    On Windows:

    ```bash
    python --version
    ```

    ??? information "How to create a virtual environment without using conda"

        ### How to create a new virtual environment without using `conda`

        You can alternatively create virtual environments using `venv` or `pipenv` instead of `conda`.

        #### `venv`
    
        You should already have the `venv` module installed with the Python 3 standard library. Create a directory for working with your project and navigate to it. For example:

        ```bash
        mkdir vizro-environment && cd vizro-environment
        ```

        Next, create a new virtual environment in this directory with `venv`:

        ```bash
        python -m venv .venv
        ```

        To activate:

        ```bash
        source .venv/bin/activate # macOS / Linux
        .\.venv\Scripts\activate  # Windows
        ```


        ####`pipenv`

        From any directory:
    
        ```bash
        pip install pipenv
        ```

        Create a directory for working with your project and navigate to it. For example:

        ```bash
        mkdir vizro-environment && cd vizro-environment
        ```

        To start a session with the correct virtual environment activated:

        ```bash
        pipenv shell
        ```



## Install vizro

To install Vizro, use [`pip`](https://pip.pypa.io/en/stable/) in your terminal window:

```bash
pip install vizro
```
<!-- vale off -->

## Use Vizro inside Anaconda Navigator

<!-- vale on -->
To completely avoid terminal usage, follow these steps to work with Vizro:
    
    
1. Install [Anaconda Navigator](https://www.anaconda.com/download).

2. Create a new environment as [outlined in the Anaconda documentation](https://docs.anaconda.com/free/navigator/tutorials/manage-environments/). Choose a Python version `>=3.8`.

3. Search `vizro` and install it [using the Anaconda Navigator package manager](https://docs.anaconda.com/free/navigator/tutorials/manage-packages/).
 
4. Similarly, search `jupyter` and install it.

5. [Launch a Jupyter notebook](https://problemsolvingwithpython.com/02-Jupyter-Notebooks/02.04-Opening-a-Jupyter-Notebook/#open-a-jupyter-notebook-with-anaconda-navigator) to work with Vizro.


## Confirm a successful installation

To confirm the installation was successful, and verify the version of Vizro installed, call the following. You can do this from within a Jupyter notebook cell, or run the following as a Python script:

```py
import vizro

print(vizro.__version__)
```

You should see a return output of the form `x.y.z`.

## Upgrade

To change the version of Vizro installed:

```bash
pip install vizro -U
```

!!! tip Check the Vizro release notes
    
    To upgrade safely, check the [release notes](https://github.com/mckinsey/vizro/blob/main/vizro-core/CHANGELOG.md) for any notable breaking changes before migrating an existing project.
