# Changelog

<!-- All enhancements and patches to vizro will be documented
in this file.  It adheres to the structure of http://keepachangelog.com/.

This project adheres to Semantic Versioning (http://semver.org/). -->

## Unreleased

See the fragment files in the [changelog.d directory](https://github.com/mckinsey/vizro/tree/main/vizro-ai/changelog.d).

<!-- scriv-insert-here -->

<a id='changelog-0.3.7'></a>

# 0.3.7 — 2025-06-03

## Fixed

- Fixed bugs in `vizro-ai.dashboard`. ([#1220](https://github.com/mckinsey/vizro/pull/1220))

<a id='changelog-0.3.6'></a>

# 0.3.6 — 2025-02-26

## Changed

- VizroAI now uses Pydantic V2 for its models and supports langchain>=0.3.0 and vizro>=0.1.32. ([#1018](https://github.com/mckinsey/vizro/pull/1018))

<a id='changelog-0.3.5'></a>

# 0.3.5 — 2025-02-24

## Added

- Added `_minimal_output` flag to allow excluding "chart insights" and "code explanations" from LLM responses. ([#1007](https://github.com/mckinsey/vizro/pull/1007))

<a id='changelog-0.3.4'></a>

# 0.3.4 — 2025-02-10

## Fixed

- Added temporary compatibility fix for Gemini models in `_pydantic_output.py`. ([#986](https://github.com/mckinsey/vizro/pull/986))

<a id='changelog-0.3.3'></a>

# 0.3.3 — 2025-01-16

## Changed

- Pinned the Vizro upper bound to prepare for Pydantic V2 migration. ([#923](https://github.com/mckinsey/vizro/pull/923))

## Fixed

- Fixed the "Model name could not be retrieved" error when using VizroAI with AWS Bedrock. ([#953](https://github.com/mckinsey/vizro/pull/953))

<a id='changelog-0.3.2'></a>

# 0.3.2 — 2024-11-08

## Removed

- Removed the older models from model shortcuts and docs. ([#853](https://github.com/mckinsey/vizro/pull/853))

## Fixed

- Fixed output validation to handle Python code block markers from llm responses. ([#858](https://github.com/mckinsey/vizro/pull/858))

<a id='changelog-0.3.1'></a>

# 0.3.1 — 2024-11-06

## Changed

- Changed prompt for `vizro-ai.plot` to provide more guidance for desired import format. ([#854](https://github.com/mckinsey/vizro/pull/854))

<a id='changelog-0.3.0'></a>

# 0.3.0 — 2024-10-02

## Highlights ✨

- VizroAI now allows **any** model with `langchain` structured output capabilities to be used, not just `ChatOpenAI`. ([#646](https://github.com/mckinsey/vizro/pull/646))
- VizroAI now has a more flexible output when choosing `VizroAI.plot(...,return_elements=True)`. See [Vizro-AI docs](https://vizro.readthedocs.io/projects/vizro-ai/en/latest/pages/user-guides/advanced-options/) for all new options. ([#646](https://github.com/mckinsey/vizro/pull/646))
- VizroAI now supports text-to-dashboard generation using `VizroAI.dashboard()`. To get started, visit the [Vizro-AI docs](https://vizro.readthedocs.io/projects/vizro-ai/en/latest/pages/tutorials/quickstart-dashboard/).

## Removed

- Removed the automatic display of chart explanation and insights in Jupyter. ([#646](https://github.com/mckinsey/vizro/pull/646))

## Changed

- Changed the return type of `VizroAI.plot(...,return_elements=True)` from `PlotOutputs` dataclass to a pydantic model with more flexible methods. See [Vizro-AI docs](https://vizro.readthedocs.io/projects/vizro-ai/en/latest/pages/user-guides/advanced-options/) for more info. ([#646](https://github.com/mckinsey/vizro/pull/646))

## Deprecated

- Removed argument `explain` from VizroAI.plot(). Use `return_elements=True` instead. ([#646](https://github.com/mckinsey/vizro/pull/646))

<a id='changelog-0.2.3'></a>

# 0.2.3 — 2024-09-09

## Added

- Added Docker image of `VizroAI.plot` UI for local use ([#1177](https://github.com/mckinsey/vizro/pull/1177))

<a id='changelog-0.2.2'></a>

# 0.2.2 — 2024-09-06

## Fixed

- Documented the step for instantiating `VizroAI` in text-to-dashboard pages ([#685](https://github.com/mckinsey/vizro/pull/685))

<a id='changelog-0.2.1'></a>

# 0.2.1 — 2024-08-28

## Removed

- Remove `_return_all_text` from `VizroAI` class ([#518](https://github.com/mckinsey/vizro/pull/518))

## Added

- Add argument `return_elements` to`VizroAI.plot()`. When it is set to `True`, the return type will be changed to a `dataclass` containing the code string, figure object, business insights, and code explanation. ([#488](https://github.com/mckinsey/vizro/pull/488))

- Add functionality to generate dashboards from text. This feature is currently in **Alpha** and is not yet officially released ([#651](https://github.com/mckinsey/vizro/pull/651))

## Changed

- Disabled figure display upon variable assignment. To display outcome of `VizroAI.plot()` add `.show()`. ([#527](https://github.com/mckinsey/vizro/pull/527))

- Stabilized `plot` performance by addressing several dataframe mutation issues. ([#603](https://github.com/mckinsey/vizro/pull/603))

<a id='changelog-0.2.0'></a>

# 0.2.0 — 2024-05-09

## Removed

- Removed `temperature` and `model_name` arguments of `VizroAI` class. For current configuration options, visit the [Vizro-AI docs](https://vizro.readthedocs.io/projects/vizro-ai/en/latest/pages/explanation/faq/#what-parameters-does-vizro-ai-support) ([#423](https://github.com/mckinsey/vizro/pull/423))

## Added

- Enable customization of LLM models provided to Vizro-AI class. ([#423](https://github.com/mckinsey/vizro/pull/423))

## Changed

- `VizroAI.plot` now generates and returns a `plotly.graph_objects.Figure` object. ([#411](https://github.com/mckinsey/vizro/pull/441)). This facilitates the integration of Vizro-AI charts into the `vizro` dashboard, visit [Use Vizro-AI dynamically to return a fig object](https://vizro.readthedocs.io/projects/vizro-ai/en/latest/pages/user-guides/add-generated-chart-usecase/#use-vizro-ais-generated-code) for details.

<a id='changelog-0.1.2'></a>

# 0.1.2 — 2024-03-13

## Added

- Add `max_debug_retry` parameter to `VizroAI.plot` to allow users to determine the maximum number of debugging attempts desired. ([#261](https://github.com/mckinsey/vizro/pull/261))

- Enable automatic loading of environment variables in a `.env` file. ([#270](https://github.com/mckinsey/vizro/pull/270))

## Changed

- Remove upper bound for `langchain` and `openai` dependencies. ([#369](https://github.com/mckinsey/vizro/pull/369))

## Fixed

- Remove the keyword `explain` from docs example explaining the `_get_chart_code` function. ([#256](https://github.com/mckinsey/vizro/pull/256))

<a id='changelog-0.1.1'></a>

# 0.1.1 — 2024-01-04

## Fixed

- Fix incompatibility with `pydantic>=2.0.0` ([#189](https://github.com/mckinsey/vizro/pull/189))

## Security

- Bump langchain version to 0.0.329, suggested by snyk ([#204](https://github.com/mckinsey/vizro/pull/204))

<a id='changelog-0.1.0'></a>

# 0.1.0 — 2023-11-13

## Highlights ✨

- Initial release of Vizro-AI package. Vizro-AI is a tool for generating data visualizations. ([#138](https://github.com/mckinsey/vizro/pull/138))
