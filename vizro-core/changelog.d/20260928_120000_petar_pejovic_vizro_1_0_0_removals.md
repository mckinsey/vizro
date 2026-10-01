<!--
A new scriv changelog fragment.

Uncomment the section that is right (remove the HTML comment wrapper).
-->

### Removed

- Removed the `RangeSlider` model. Use `Slider` with `range=True` instead. ([#XXXX](https://github.com/mckinsey/vizro/pull/XXXX))

- Removed the `Layout` model. Use `Grid` instead. ([#XXXX](https://github.com/mckinsey/vizro/pull/XXXX))

- Removed the `AgGrid` model and the Dash `DataTable` backing for `Table` (`dash_data_table`). `Table` now renders only a `dash_ag_grid` figure: use `vm.Table(figure=dash_ag_grid(...))`. ([#XXXX](https://github.com/mckinsey/vizro/pull/XXXX))

- Removed the `set_control` action. Use `set_controls`, whose `controls` argument accepts a single id or a list of ids. ([#XXXX](https://github.com/mckinsey/vizro/pull/XXXX))

- Removed the `filter_interaction` action. Use the more powerful and flexible `set_controls` instead. ([#XXXX](https://github.com/mckinsey/vizro/pull/XXXX))

- Removed the `Action` model's `inputs` argument. Pass references to runtime inputs directly as arguments of `function`. ([#XXXX](https://github.com/mckinsey/vizro/pull/XXXX))

- Removed support for passing static arguments to a custom action. All arguments must now be runtime inputs. ([#XXXX](https://github.com/mckinsey/vizro/pull/XXXX))

- Removed support for using the `Action` model to wrap a built-in action. Call the built-in action directly, for example `actions=va.export_data(...)`. ([#XXXX](https://github.com/mckinsey/vizro/pull/XXXX))

### Changed

- The default of `Cascader.full_path` is now `True` (path mode). Set `full_path=False` explicitly to keep the previous leaf-mode behavior. ([#XXXX](https://github.com/mckinsey/vizro/pull/XXXX))
