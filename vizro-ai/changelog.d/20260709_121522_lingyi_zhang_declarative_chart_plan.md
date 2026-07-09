<!--
A new scriv changelog fragment.

Uncomment the section that is right (remove the HTML comment wrapper).
-->
<!--
### Highlights ✨

- A bullet item for the Highlights ✨ category with a link to the relevant PR at the end of your entry, e.g. Enable feature XXX. ([#1](https://github.com/mckinsey/vizro/pull/1))

-->
### Removed

- Removed the `chart_code`, `imports` and `code_explanation` fields from the chart plan models.
- Removed the code-execution safeguard and the `black` and `autoflake` dependencies.

<!--
### Added

- A bullet item for the Added category with a link to the relevant PR at the end of your entry, e.g. Enable feature XXX. ([#1](https://github.com/mckinsey/vizro/pull/1))

-->

### Changed

- `chart_agent` now returns a declarative chart specification that Vizro-AI renders with its own `plotly.express` code — model-generated code is never executed.
- `vizro_chart_function` and `code_vizro` produce standard `vizro.plotly.express` charts (no `@capture("graph")`), and chart functions accept plotly express keyword overrides such as `title=`.
- Invalid chart specifications now fail with clear errors instead of being silently ignored, and `chart_agent` validates the plan against your dataframe, retrying on mismatch. Pass the dataframe already in the shape to plot; Vizro-AI does not transform data.

<!--
### Deprecated

- A bullet item for the Deprecated category with a link to the relevant PR at the end of your entry, e.g. Enable feature XXX. ([#1](https://github.com/mckinsey/vizro/pull/1))

-->
<!--
### Fixed

- A bullet item for the Fixed category with a link to the relevant PR at the end of your entry, e.g. Enable feature XXX. ([#1](https://github.com/mckinsey/vizro/pull/1))

-->
<!--
### Security

- A bullet item for the Security category with a link to the relevant PR at the end of your entry, e.g. Enable feature XXX. ([#1](https://github.com/mckinsey/vizro/pull/1))

-->
