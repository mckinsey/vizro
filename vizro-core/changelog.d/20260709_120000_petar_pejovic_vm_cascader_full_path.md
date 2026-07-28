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

- `Cascader` gains a `full_path` attribute. With `full_path=False` (default, leaf mode) a selection is a bare leaf value (single-select) or a list of leaf values (multi-select), leaf labels must be unique across the tree, a hierarchical `Filter` matches the last `column`, and `set_control` is supported — matching the previous behavior. With `full_path=True` (path mode) a selection is a full root-to-leaf path (single-select) or a list of paths (multi-select), so duplicate leaf labels across branches are addressed unambiguously and a hierarchical `Filter` matches every `column`. ([#1793](https://github.com/mckinsey/vizro/pull/1793))

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
