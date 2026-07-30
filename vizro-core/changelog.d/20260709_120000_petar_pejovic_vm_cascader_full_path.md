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
### Added

- `vm.Cascader` gains a `full_path` flag. The default (`full_path=False`, leaf mode) preserves existing behavior: a selection is a bare leaf value (single-select) or a list of leaf values (multi-select), leaf labels must be unique across the tree, a hierarchical `vm.Filter` matches the last `Filter.column`, and `set_control` is supported. ([#1793](https://github.com/mckinsey/vizro/pull/1793))

- Set `full_path=True` on `vm.Cascader` to enable path mode: a selection becomes a full root-to-leaf path (single-select) or a list of paths (multi-select), allowing duplicate leaf labels across branches. A hierarchical `vm.Filter` then matches on every level of `Filter.column`, so the number of `Filter.column` entries must equal the number of levels in the `options` hierarchy. Path mode does not support `set_control` yet. ([#1793](https://github.com/mckinsey/vizro/pull/1793))

<!--
### Changed

- A bullet item for the Changed category with a link to the relevant PR at the end of your entry, e.g. Enable feature XXX. ([#1](https://github.com/mckinsey/vizro/pull/1))

-->
<!--
### Deprecated

- A bullet item for the Deprecated category with a link to the relevant PR at the end of your entry, e.g. Enable feature XXX. ([#1](https://github.com/mckinsey/vizro/pull/1))

-->
### Fixed

- A hierarchical `vm.Filter` restores the previously selected value across multiple dynamic-data reloads. ([#1793](https://github.com/mckinsey/vizro/pull/1793))

<!--
### Security

- A bullet item for the Security category with a link to the relevant PR at the end of your entry, e.g. Enable feature XXX. ([#1](https://github.com/mckinsey/vizro/pull/1))

-->
