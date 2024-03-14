# Changelog

<!-- All enhancements and patches to vizro will be documented
in this file.  It adheres to the structure of http://keepachangelog.com/.

This project adheres to Semantic Versioning (http://semver.org/). -->

## Unreleased

See the fragment files in the [changelog.d directory](https://github.com/mckinsey/vizro/tree/main/vizro-ai/changelog.d).

<!-- scriv-insert-here -->

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
