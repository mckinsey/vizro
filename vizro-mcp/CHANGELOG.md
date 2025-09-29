<a id='changelog-0.1.3'></a>

# 0.1.3 — 2025-09-29

## Added

- Added ability to use KPI cards in `Figure`. ([#1392](https://github.com/mckinsey/vizro/pull/1392))

## Changed

- Updated Layout prompting for better Layout performance of the MCP server. ([#1405](https://github.com/mckinsey/vizro/pull/1405))

- Updated Vizro version to >=0.1.46. ([#1423](https://github.com/mckinsey/vizro/pull/1423))

## Fixed

- Added tool parameter descriptions to Field definition instead of docstring so that they display properly in hosts like Cursor. ([#1374](https://github.com/mckinsey/vizro/pull/1374)) <a id='changelog-0.1.2'></a>

# 0.1.2 — 2025-06-30

## Added

- Add Dockerfile for Vizro MCP server to enable containerized local setup. ([#1184](https://github.com/mckinsey/vizro/pull/1184))

- Add capability to create custom charts (beyond Plotly Express) with Vizro-MCP. ([#1227](https://github.com/mckinsey/vizro/pull/1227))

## Changed

- Update Vizro version to `>=0.1.42`. ([#1227](https://github.com/mckinsey/vizro/pull/1227))

- Improve usability of MCP server in IDE environments like Cursor. ([#1227](https://github.com/mckinsey/vizro/pull/1227))

<a id='changelog-0.1.1'></a>

# 0.1.1 — 2025-05-15

### Fixed

- Fix name conflict with `langchain` by avoiding use of conflicting parameter names in tools. ([#1177](https://github.com/mckinsey/vizro/pull/1177))

<a id='changelog-0.1.0'></a>

# 0.1.0 — 2025-05-06

## Added

- Initial release of the Vizro MCP server. ([#1125](https://github.com/mckinsey/vizro/pull/1125))
    - still experimental, please provide feedback via [github issues](https://github.com/mckinsey/vizro/issues)
    - pinned `vizro` version to `0.1.38`
    - published with 6 tools and 3 prompt templates
