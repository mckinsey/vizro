<!--
A new scriv changelog fragment.

Uncomment the section that is right (remove the HTML comment wrapper).
-->

<!--
### Highlights ✨

- A bullet item for the Highlights ✨ category with a link to the relevant PR at the end of your entry, e.g. Enable feature XXX. ([#1](https://github.com/mckinsey/vizro/pull/1))

-->
<!--
### Removed

- A bullet item for the Removed category with a link to the relevant PR at the end of your entry, e.g. Enable feature XXX. ([#1](https://github.com/mckinsey/vizro/pull/1))

-->
<!--
### Added

- A bullet item for the Added category with a link to the relevant PR at the end of your entry, e.g. Enable feature XXX. ([#1](https://github.com/mckinsey/vizro/pull/1))

-->

### Changed

<!--

- A bullet item for the Changed category with a link to the relevant PR at the end of your entry, e.g. Enable feature XXX. ([#1](https://github.com/mckinsey/vizro/pull/1))

-->

Changed AgGrid defaults to improve layout compatibility and performance:

- Enabled "domLayout": "autoHeight" by default, allowing the grid to automatically adjust its height based on content. This prevents layout issues where the grid could collapse to 0px in flexible containers without an explicit parent height.
- Enabled pagination by default to ensure good performance, as autoHeight causes all rows to be rendered at once. Pagination limits the number of visible rows and maintains responsiveness even with large datasets.

These changes ensure AgGrid displays correctly in more layout scenarios and remains performant with large tables. ([#1226](https://github.com/mckinsey/vizro/pull/1226))

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
