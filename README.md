<br/><br/>

<p align="center">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/mckinsey/vizro/main/.github/images/Vizro_Github_Banner_Dark_Mode.png">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/mckinsey/vizro/main/.github/images/Vizro_Github_Banner_Light_Mode.png">
  <img alt="Vizro logo" src="https://raw.githubusercontent.com/mckinsey/vizro/main/.github/images/Vizro_Github_Banner_Dark_Mode.png" width="250">
</picture>
</p>
<br/><br/>

<div align="center" markdown="1">

[![Python version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://pypi.org/project/vizro/)
[![PyPI version](https://badge.fury.io/py/vizro.svg)](https://badge.fury.io/py/vizro)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/mckinsey/vizro/blob/main/LICENSE.md)
[![Documentation](https://readthedocs.org/projects/vizro/badge/?version=stable)](https://vizro.readthedocs.io/)
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/7858/badge)](https://www.bestpractices.dev/projects/7858)

</div>

<div align="center" markdown="1">

<a href="https://vizro.readthedocs.io/en/stable/" target="_blank">Documentation </a> |
<a href="https://vizro.readthedocs.io/en/stable/pages/tutorials/first_dashboard/" target="_blank">Get Started </a> |
<a href="http://vizro.mckinsey.com/" target="_blank">Live Demo </a>

</div>

---

<p align="center">
<img src="https://raw.githubusercontent.com/mckinsey/vizro/main/.github/images/example_screens.png" width="700"/>
</p>

<p align="center">
<font size="+2">
<b>
Visual Intelligence. Beautifully Engineered
</b>
</font>
</p>

<p align="center">
<font size="+1">
Vizro is a toolkit for creating modular data visualization applications
</font>
</p>

<p align="center">
<img src="https://raw.githubusercontent.com/mckinsey/vizro/main/.github/images/tech_logos.png" width="300"/>
</p>

## What is Vizro?

<p align="left">
<font size="+1">
Rapidly self-serve the assembly of customized dashboards in minutes - without the need for advanced coding or design experience - to create flexible and scalable, Python-enabled data visualization applications.
</font>
</p>

<p align="center">
<img src="https://raw.githubusercontent.com/mckinsey/vizro/main/.github/images/code_dashboard.png" width="1300"/>
</p>

Use a few lines of simple configuration to create complex dashboards, which are automatically assembled using libraries such as [**Plotly**](https://github.com/plotly/plotly.py) and [**Dash**](https://github.com/plotly/dash), with inbuilt coding and design best practices.

Define high-level categories within the configuration, including:

- **Components:** create charts, tables, input/output interfaces, and more.
- **Controls**: create filters, parameter inputs, and custom action controllers.
- **Pages, layouts and navigation**: create multiple pages, with customizable layouts and flexible navigation across them.
- **Actions and interactions**: create interactions between charts, and use pre-defined or customized actions (such as exporting).

Configuration can be written in multiple formats including **Pydantic models**, **JSON**, **YAML** or **Python dictionaries** for added flexibility of implementation.

Optional high-code extensions enable almost infinite customization in a modular way, combining the best of low-code and high-code - for flexible and scalable, Python enabled data visualization applications.

Visit ["Why should I use Vizro?"](https://vizro.readthedocs.io/en/stable/pages/explanation/faq/#why-should-i-use-vizro) for a more detailed explanation of Vizro use cases.

### What is Vizro-AI?

Vizro-AI is a separate package and extends Vizro to enable the use of natural language queries to build Plotly charts.

<p align="center">
<img src="./vizro-ai/docs/assets/readme/readme_animation.gif" alt="Gif to show vizro-ai", width="525" height="296">
</p>

See the [Vizro-AI documentation](https://vizro.readthedocs.io/projects/vizro-ai/en/latest/) for more details.

## Key benefits of Vizro

<br/>

<p align="center">
<img src="https://raw.githubusercontent.com/mckinsey/vizro/main/.github/images/value_prop_icons.png" width="900"/>
</p>

<br/>

## Live demo

You can see Vizro in action by clicking on the following image or by visiting [vizro.mckinsey.com](https://vizro.mckinsey.com).

<p align="left">
<a href="http://vizro.mckinsey.com/">
<img border="0" src="https://raw.githubusercontent.com/mckinsey/vizro/main/.github/images/live_interactive_demo.png" width="525" height="296">  </a>
</p>

## Examples

<p align="center">
<img src="https://raw.githubusercontent.com/mckinsey/vizro/main/.github/images/dashboard_examples.png" width="1300"/>
</p>

## Installation and first steps

```console
pip install vizro
```

See the [installation guide](https://vizro.readthedocs.io/en/stable/pages/user-guides/install/) for more information.

The [get started documentation](https://vizro.readthedocs.io/en/stable/pages/tutorials/first-dashboard/) explains how to create your first dashboard.

## Get hands on

See the [how-to guides](https://vizro.readthedocs.io/en/stable/pages/user-guides/install/) for step-by-step instructions on the key Vizro features.

## Packages

This repository is a monorepo containing the following packages:

|           Folder           |                                           Version                                           |                               Documentation                                |
| :------------------------: | :-----------------------------------------------------------------------------------------: | :------------------------------------------------------------------------: |
| [vizro-core](./vizro-core) |    [![PyPI version](https://badge.fury.io/py/vizro.svg)](https://badge.fury.io/py/vizro)    |           [Vizro Docs](https://vizro.readthedocs.io/en/stable/)            |
|   [vizro-ai](./vizro-ai)   | [![PyPI version](https://badge.fury.io/py/vizro-ai.svg)](https://badge.fury.io/py/vizro-ai) | [Vizro-AI Docs](https://vizro.readthedocs.io/projects/vizro-ai/en/latest/) |

## Community and development

We encourage you to ask and answer technical questions via the [GitHub Issues](https://github.com/mckinsey/vizro/issues). This is also the place where you can submit bug reports or request new features.

## Want to contribute to Vizro?

The [contribution guidelines](https://vizro.readthedocs.io/en/stable/pages/explanation/contributing/) explain how you can contribute to Vizro.

You can also view current and former [contributors](https://vizro.readthedocs.io/en/stable/pages/explanation/authors/).

## Want to report a security vulnerability?

See our [security policy](https://github.com/mckinsey/vizro/security/policy).

## License

`vizro` is distributed under the terms of the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0)
