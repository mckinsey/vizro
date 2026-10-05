<!--
A new scriv changelog fragment.

Uncomment the section that is right (remove the HTML comment wrapper).
-->

### Removed

- Removed the `RangeSlider` model. Use `Slider` with `range=True` instead. ([#1877](https://github.com/mckinsey/vizro/pull/1877))

- Removed the `Layout` model. Use `Grid` instead. ([#1877](https://github.com/mckinsey/vizro/pull/1877))

- Removed the `AgGrid` model and the Dash `DataTable` backing for `Table` (`dash_data_table`). `Table` now renders only a `dash_ag_grid` figure: use `vm.Table(figure=dash_ag_grid(...))`. ([#1877](https://github.com/mckinsey/vizro/pull/1877))

- Removed the `set_control` action. Use `set_controls`, whose `controls` argument accepts a single id or a list of ids. ([#1877](https://github.com/mckinsey/vizro/pull/1877))

- Removed the `filter_interaction` action. Use the more powerful and flexible `set_controls` instead. ([#1877](https://github.com/mckinsey/vizro/pull/1877))

- Removed the `Action` model's `inputs` argument. Pass references to runtime inputs directly as arguments of `function`. ([#1877](https://github.com/mckinsey/vizro/pull/1877))

- Removed support for passing static arguments to a custom action. All arguments must now be runtime inputs. ([#1877](https://github.com/mckinsey/vizro/pull/1877))

- Removed support for using the `Action` model to wrap a built-in action. Call the built-in action directly, for example `actions=va.export_data(...)`. ([#1877](https://github.com/mckinsey/vizro/pull/1877))

- Removed the fallback that let an action specified as a dictionary or in YAML/JSON omit its `type`. Every action must now declare an explicit `type` (for example `type: action` for a custom action, or `type: export_data` for a built-in action), consistent with all other models. ([#1877](https://github.com/mckinsey/vizro/pull/1877))

### Changed

- The default of `Cascader.full_path` is now `True` (path mode). Set `full_path=False` explicitly to keep the previous leaf-mode behavior. ([#1877](https://github.com/mckinsey/vizro/pull/1877))
