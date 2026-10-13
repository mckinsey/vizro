<!--
A new scriv changelog fragment.

Uncomment the section that is right (remove the HTML comment wrapper).
-->

### Removed

- Remove the `RangeSlider` model. Use `Slider` with `range=True` instead. See the [migration guide](https://vizro.readthedocs.io/en/stable/pages/API-reference/migration/#rangeslider-model). ([#1877](https://github.com/mckinsey/vizro/pull/1877))

- Remove the `Layout` model. Use `Grid` instead. See the [migration guide](https://vizro.readthedocs.io/en/stable/pages/API-reference/migration/#layout-model). ([#1877](https://github.com/mckinsey/vizro/pull/1877))

- Remove the `AgGrid` model and the Dash `DataTable` backing for `Table` (`dash_data_table`). `Table` now renders only a `dash_ag_grid` figure: use `vm.Table(figure=dash_ag_grid(...))`. See the [migration guide](https://vizro.readthedocs.io/en/stable/pages/API-reference/migration/#aggrid-model). ([#1877](https://github.com/mckinsey/vizro/pull/1877))

- Remove the `set_control` action. Use `set_controls`, whose `controls` argument accepts a single id or a list of ids. See the [migration guide](https://vizro.readthedocs.io/en/stable/pages/API-reference/migration/#set_control-action). ([#1877](https://github.com/mckinsey/vizro/pull/1877))

- Remove the `filter_interaction` action. Use the more powerful and flexible `set_controls` instead. See the [migration guide](https://vizro.readthedocs.io/en/stable/pages/API-reference/migration/#filter_interaction). ([#1877](https://github.com/mckinsey/vizro/pull/1877))

- Remove the `Action` model's `inputs` argument. Pass references to runtime inputs directly as arguments of `function`. See the [migration guide](https://vizro.readthedocs.io/en/stable/pages/API-reference/migration/#action-model-inputs-argument). ([#1877](https://github.com/mckinsey/vizro/pull/1877))

- Remove support for passing static arguments to a custom action. All arguments must now be runtime inputs; define any static values directly in the function body instead. See the [migration guide](https://vizro.readthedocs.io/en/stable/pages/API-reference/migration/#static-argument-for-custom-action). ([#1877](https://github.com/mckinsey/vizro/pull/1877))

- Remove support for using the `Action` model to wrap a built-in action. Call the built-in action directly, for example `actions=va.export_data(...)`. See the [migration guide](https://vizro.readthedocs.io/en/stable/pages/API-reference/migration/#action-model-for-built-in-action). ([#1877](https://github.com/mckinsey/vizro/pull/1877))

- Remove the fallback that let an action specified as a dictionary or in YAML/JSON omit its `type`. Every action must now declare an explicit `type` (for example `type: action` for a custom action, or `type: export_data` for a built-in action), consistent with all other models. See the [migration guide](https://vizro.readthedocs.io/en/stable/pages/API-reference/migration/#action-type-required-in-dict-yaml-json). ([#1877](https://github.com/mckinsey/vizro/pull/1877))

- Remove the fallback that let a layout specified as a dictionary or in YAML/JSON omit its `type`. Every layout must now declare an explicit `type` (`type: grid` for a `Grid` or `type: flex` for a `Flex`), consistent with all other models. See the [migration guide](https://vizro.readthedocs.io/en/stable/pages/API-reference/migration/#layout-type-required-in-dict-yaml-json). ([#1877](https://github.com/mckinsey/vizro/pull/1877))

### Changed

- The default of `Cascader.full_path` is now `True` (path mode). Set `full_path=False` explicitly to keep the previous leaf-mode behavior. See the [migration guide](https://vizro.readthedocs.io/en/stable/pages/API-reference/migration/#cascader-full_path-default). ([#1877](https://github.com/mckinsey/vizro/pull/1877))
