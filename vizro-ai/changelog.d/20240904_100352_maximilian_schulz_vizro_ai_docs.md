<!--
A new scriv changelog fragment.

Uncomment the section that is right (remove the HTML comment wrapper).
-->

### Highlights ✨

- VizroAI now allows **any** `langchain` model with structured output capabilities to be used, not just `ChatOpenAI` ([#646](https://github.com/mckinsey/vizro/pull/646))
- VizroAI now has a more flexible output when choosing `VizroAI.plot(...,return_elements=True)`. See documentation for all new options. ([#646](https://github.com/mckinsey/vizro/pull/646))

### Removed

- Removed the automatic display of chart explanation and insights in Jupyter. ([#646](https://github.com/mckinsey/vizro/pull/646))

<!--
### Added

- A bullet item for the Added category with a link to the relevant PR at the end of your entry, e.g. Enable feature XXX ([#1](https://github.com/mckinsey/vizro/pull/1))

-->

### Changed

- Changed the return type of `VizroAI.plot(...,return_elements=True)` from `PlotOutputs` dataclass to a pydantic model with more flexible methods. See documentation for more into ([#646](https://github.com/mckinsey/vizro/pull/646))

### Deprecated

- Removed argument `explain` from VizroAI.plot(). Use `return_elements=True` instead. ([#646](https://github.com/mckinsey/vizro/pull/646))

<!--
### Fixed

- A bullet item for the Fixed category with a link to the relevant PR at the end of your entry, e.g. Enable feature XXX ([#1](https://github.com/mckinsey/vizro/pull/1))

-->
<!--
### Security

- A bullet item for the Security category with a link to the relevant PR at the end of your entry, e.g. Enable feature XXX ([#1](https://github.com/mckinsey/vizro/pull/1))

-->
