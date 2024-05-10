# Changelog

<!-- All enhancements and patches to vizro will be documented
in this file.  It adheres to the structure of http://keepachangelog.com/.

This project adheres to Semantic Versioning (http://semver.org/). -->

## Unreleased

See the fragment files in the [changelog.d directory](https://github.com/mckinsey/vizro/tree/main/vizro-ai/changelog.d).

<!-- scriv-insert-here -->

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

- Initial release of Vizro-AI package. Vizro-AI is a tool for generating data
  visualizations. ([#138](https://github.com/mckinsey/vizro/pull/138))
