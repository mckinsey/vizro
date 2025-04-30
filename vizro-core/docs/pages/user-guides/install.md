# Installation Guide for Vizro

## Overview

You can use [PyCafe](https://py.cafe/) to work with Vizro without installing it, as the [first dashboard tutorial](../tutorials/first-dashboard.md) demonstrations. Refer to the [PyCafe documentation](https://py.cafe/docs/apps/vizro) to find out more.

If you prefer install Vizro, the rest of this page explains how to do get set up, verify the instsallation, check the version of Vizro you have installed, and update the version if you later want to do so.

### Prerequisites

Before proceeding with the installation, ensure that you have the following prerequisites:

- **Python**: Vizro is compatible with macOS, Linux, and Windows, requiring Python version 3.9 or later.
- **Virtual Environment**: It is recommended to use a virtual environment to manage dependencies. For more information, consult the following resources:

  - [Python Virtual Environments](https://realpython.com/python-virtual-environments-a-primer/)
  - [Conda Virtual Environments](https://docs.conda.io/projects/conda/en/latest/user-guide/getting-started.html#starting-conda)
  - [Explainer Video on Virtual Environments](https://youtu.be/YKfAwIItO7M)

<details>

<summary>To install Python using the terminal on a macOS machine, follow these steps;<summary>

##### Step 1: Open Terminal

You can open Terminal by searching for it in Spotlight (press Cmd + Space and type "Terminal") or by navigating to Applications > Utilities > Terminal.

##### Step 2: Check Existing Python Installation.

Before installing a new version of Python, check if you already have Python installed:

```bash
python3 --version
```
If Python is installed, you will see the version number. If not, proceed to the next steps.

##### Step 3: Install Homebrew (if not already installed)

Homebrew is a package manager for macOS that makes it easy to install software from the terminal. If you don't have Homebrew installed, you can install it by running:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
Follow the on-screen instructions to complete the installation of Homebrew.

##### Step 4: Install Python

Now that Homebrew is installed, you can use it to install Python. Run the following command:

```bash
brew install python
```

This command will install the latest version of Python. Homebrew will handle the installation process and any dependencies required.

##### Step 5: Verify the Installation

Once the installation is complete, verify that Python has been installed successfully by checking the version again:

```bash
python3 --version
```

You should see the version number of the installed Python.

##### Step 6: (Optional) Set Up a Virtual Environment

It is a good practice to use a virtual environment for your Python projects. Here's how to create and activate one:

1) Navigate to your project directory:

```bash
cd /path/to/your/project
```

2) Ceate a virtual environment:

```bash
python3 -m venv venv
```

3) Activate the virtual environment:

```bash
source venv/bin/activate
```

4) Deactivate the virtual environment (when done):

```bash
deactivate
```

</details>

## Creating a Virtual Environment

Creating a virtual environment is essential for isolating your Python dependencies. Follow these steps to set up a virtual environment using `venv`, which is included in Python's standard library:

**Create and Navigate to Project Directory:**

```bash
mkdir vizro-project
cd vizro-project
```

**Create and Activate a Virtual Environment:**

For macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```
For Windows
```bash
python3 -m venv .venv
.venv\Scripts\activate
```

Alternatively, you can use [`conda` as your virtual environment manager](https://docs.conda.io/projects/conda/en/latest/user-guide/install/).

```bash
conda create --name vizro-environment
conda activate vizro-environment
```

## Installing Vizro

To install Vizro, utilize the Python package manager,, use [`pip`](https://pip.pypa.io/en/stable/). Execute the following command in your terminal::

```bash
pip install vizro
```

## Verifying the Installation

To confirm that Vizro has been installed successfully and to check the installed version, run the following code. You can execute this within a Jupyter Notebook cell or as a standalone Python script:

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

## Plugins

!!! tip "Enable IDE autocompletion"

    Vizro is heavily based on [pydantic](https://docs.pydantic.dev/latest/). In order to enable autocompletion when configuring Vizro models, you can use the pydantic [plugin for VS Code](https://docs.pydantic.dev/latest/integrations/visual_studio_code/) or [for PyCharm](https://docs.pydantic.dev/latest/integrations/pycharm/).

![logo](../../assets/user_guides/install/logo_watermark_extended.svg){width="250"}
