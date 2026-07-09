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

- **Breaking:** `vm.Cascader` selections are now full root-to-leaf paths (e.g. `["Europe", "France"]`) instead of just the leaf value, so hierarchical filters support duplicate leaf labels across branches. ([#XXXX](https://github.com/mckinsey/vizro/pull/XXXX))

<!--
### Deprecated

- A bullet item for the Deprecated category with a link to the relevant PR at the end of your entry, e.g. Enable feature XXX. ([#1](https://github.com/mckinsey/vizro/pull/1))

-->
### Fixed

- A hierarchical `vm.Filter` selection now survives dynamic-data reloads even across multiple reloads, because the selected path is restored directly from its own branch context. ([#XXXX](https://github.com/mckinsey/vizro/pull/XXXX))

<!--
### Security

- A bullet item for the Security category with a link to the relevant PR at the end of your entry, e.g. Enable feature XXX. ([#1](https://github.com/mckinsey/vizro/pull/1))

-->
