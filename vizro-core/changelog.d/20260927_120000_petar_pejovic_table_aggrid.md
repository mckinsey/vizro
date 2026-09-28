### Added

- `Table` now renders an interactive Dash AG Grid when given a `dash_ag_grid` figure (`vm.Table(figure=dash_ag_grid(...))`). This replaces `AgGrid`. ([#1869](https://github.com/mckinsey/vizro/pull/1869))

### Deprecated

- `AgGrid` is deprecated and will be removed in Vizro `1.0.0`. Use `Table` with a `dash_ag_grid` figure instead (`vm.Table(figure=dash_ag_grid(...))`). ([#1869](https://github.com/mckinsey/vizro/pull/1869))

- The Dash DataTable backing for `Table` (via `dash_data_table`) is deprecated and will be removed in Vizro `1.0.0`. Use a `dash_ag_grid` figure instead. ([#1869](https://github.com/mckinsey/vizro/pull/1869))
