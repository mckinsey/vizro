
<a id='changelog-0.3.0'></a>
# 0.3.0 — 2026-07-29

## Added

- `vdc.Cascader` gains a `full_path` boolean prop (default `False`) selecting how `value` is encoded. ([#1807](https://github.com/mckinsey/vizro/pull/1807))

## Changed

- `vdc.Cascader` now defaults to leaf-value mode (`full_path=False`): `value` is a bare leaf scalar (single-select) or a list of leaf scalars (multi-select), matching the `0.1.x` behavior. Set `full_path=True` to keep the `0.2.0` full root-to-leaf path shape (a single path, or a list of paths), which is required to address duplicate leaf `value`s across different branches. ([#1807](https://github.com/mckinsey/vizro/pull/1807))

<a id='changelog-0.2.0'></a>
# 0.2.0 — 2026-07-16

## Changed

- `Cascader.value` now returns the full root-to-leaf path (e.g. `["Europe", "France", "Paris"]`, or a list of such paths when `multi=True`) instead of just leaf values, enabling duplicate leaf labels across branches. ([#1792](https://github.com/mckinsey/vizro/pull/1792))
<a id='changelog-0.1.1'></a>

# 0.1.1 — 2026-03-31

## Added

- Add `Cascader` hierarchical dropdown component supporting single-select and multi-select with cascading side-by-side panels. ([#1673](https://github.com/mckinsey/vizro/pull/1673/))

<a id='changelog-0.1.0'></a>

# 0.1.0 — 2026-03-06

## Added

- Initial release of vizro-dash-components (`vdc`) with `Markdown` component: a clone of `dcc.Markdown` that uses `dmc.CodeHighlight` and `dmc.InlineCodeHighlight`. ([#1571](https://github.com/mckinsey/vizro/pull/1571))
