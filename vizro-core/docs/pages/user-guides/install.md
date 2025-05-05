# Installation Guide for Vizro

## Overview

Welcome to Vizro! 👋 This guide will help you get started with installing and setting up Vizro for building interactive dashboards.

You can use [PyCafe](https://py.cafe/) to work with Vizro without installing it, as demonstrated in the [first dashboard tutorial](../tutorials/first-dashboard.md). Using PyCafe is a great way to try out Vizro quickly. For more information, see the [PyCafe documentation](https://py.cafe/docs/apps/vizro).

If you prefer to work locally, this guide will walk you through installing Vizro onto your machine. We'll also cover how to verify your installation and keep Vizro up to date.

## Prerequisites

Before installing Vizro, you'll need:

- Python 3.9 or later
- A virtual environment (recommended)

**For Python installation and virtual environment setup, refer to:**

- [Official Python Installation Guide](https://www.python.org/downloads/) - The best place to start if you're new to Python.
- [Python Packaging Guide](https://packaging.python.org/en/latest/tutorials/installing-packages/#requirements-for-installing-packages) - Comprehensive guide on Python package management.
- [Anaconda](https://docs.conda.io/en/latest/) - A popular choice for Python installation and virtual environment management.
- [uv](https://github.com/astral-sh/uv) - A modern, fast Python package installer and resolver.

!!! warning "Use a virtual environment"

    We strongly recommend using a virtual environment when working with Python packages to avoid dependency conflicts and keep your system Python clean. See the [Python Packaging Guide for more information about creating virtual environments](https://packaging.python.org/en/latest/tutorials/installing-packages/#creating-and-using-virtual-environments).

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

To make sure everything is working correctly, you can verify your installation and check the installed version:

```python
import vizro

print(vizro.__version__)
```

You should see the version number displayed (e.g., `0.1.0`).

## Upgrading

When new versions of Vizro are released, you can upgrade to use them with:

```bash
pip install -U vizro
```

!!! note "Check Release Notes"

    Before upgrading, we recommend checking the [release notes](https://github.com/mckinsey/vizro/blob/main/vizro-core/CHANGELOG.md) for any breaking changes that might affect your existing dashboards.

## IDE Support

!!! tip "Enable IDE autocompletion"

    Vizro uses [pydantic](https://docs.pydantic.dev/latest/) for configuration, which means you can get IDE support. To enable autocompletion and type hints, install:

    - [VS Code plugin](https://docs.pydantic.dev/latest/integrations/visual_studio_code/)
    - [PyCharm plugin](https://docs.pydantic.dev/latest/integrations/pycharm/)

![logo](../../assets/user_guides/install/logo_watermark_extended.svg){width="250"}
