# Installation Guide for Vizro

## Overview
This guide explains how to install Vizro, a tool for building interactive dashboards.
You can use [PyCafe](https://py.cafe/) to work with Vizro without installing it, as the [first dashboard tutorial](../tutorials/first-dashboard.md) shows. Refer to the [PyCafe documentation](https://py.cafe/docs/apps/vizro) to find out more.

To install Vizro on your local machine, follow the steps below. This page also covers how to verify the installation, check the installed version, and update Vizro when needed.

## Prerequisites

- Python 3.9 or later
- A virtual environment (recommended)


**For Python installation and virtual environment setup, refer to:**

- [Official Python Installation Guide](https://www.python.org/downloads/)
- [Python Packaging Guide - How to install packages](https://packaging.python.org/en/latest/tutorials/installing-packages/#requirements-for-installing-packages)
- [Anaconda](https://docs.conda.io/en/latest/) - For Python installation and virtual environment management
- [uv](https://github.com/astral-sh/uv) - A fast Python package installer and resolver

!!! warning "Use Virtual Environments"

    Always use a virtual environment when working with Python packages. This helps avoid dependency conflicts and keeps your system Python clean. See the [Python Packaging Guide on creating virtual environments](https://packaging.python.org/en/latest/tutorials/installing-packages/#creating-and-using-virtual-environments) for detailed instructions.

## Installing Vizro

### Using pip

```bash
pip install vizro
```

### Using uv

```bash
uv pip install vizro
```

## Verifying the Installation

To confirm the installation was successful and verify the version of Vizro installed, call the following:

```python
import vizro

print(vizro.__version__)
```

## Upgrading

To upgrade to the latest version:

```bash
pip install -U vizro
```

!!! note "Check Release Notes"

    Before upgrading, check the [release notes](https://github.com/mckinsey/vizro/blob/main/vizro-core/CHANGELOG.md) for any breaking changes.

## IDE Support

!!! tip "Enable IDE Autocompletion"

    Vizro uses [pydantic](https://docs.pydantic.dev/latest/) for configuration. Enable autocompletion by installing:

    - [VS Code plugin](https://docs.pydantic.dev/latest/integrations/visual_studio_code/)
    - [PyCharm plugin](https://docs.pydantic.dev/latest/integrations/pycharm/)

![logo](../../assets/user_guides/install/logo_watermark_extended.svg){width="250"}
