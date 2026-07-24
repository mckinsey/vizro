### Added

- `vdc.Cascader` gains a `full_path` boolean prop (default `False`) selecting how `value` is encoded. ([#1807](https://github.com/mckinsey/vizro/pull/1807))

### Changed

- **BREAKING:** `vdc.Cascader` now defaults to leaf-value mode (`full_path=False`): `value` is a bare leaf scalar (single-select) or a list of leaf scalars (multi-select), matching the `0.1.x` behaviour. Set `full_path=True` to keep the `0.2.0` full root-to-leaf path shape (a single path, or a list of paths), which is required to address duplicate leaf `value`s across different branches. Leaf mode requires leaf `value`s (not `label`s) to be unique across the tree. A persisted value whose shape does not match the current mode is ignored rather than restored. ([#1807](https://github.com/mckinsey/vizro/pull/1807))
