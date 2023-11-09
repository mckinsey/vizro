# Changelog

<!-- All enhancements and patches to vizro will be documented
in this file.  It adheres to the structure of http://keepachangelog.com/.

This project adheres to Semantic Versioning (http://semver.org/). -->

## Unreleased

See the fragment files in the [changelog.d directory](https://github.com/mckinsey/vizro/tree/main/vizro-core/changelog.d).

<!-- scriv-insert-here -->

<a id='changelog-0.1.6'></a>

# 0.1.6 — 2023-11-09

## Highlights ✨

- Release of the Vizro Dash DataTable. Visit the [user guide on tables](https://vizro.readthedocs.io/en/stable/pages/user_guides/table/) to learn more. ([#114](https://github.com/mckinsey/vizro/pull/114))

## Added

- `Vizro` takes `**kwargs` that are passed through to `Dash` ([#151](https://github.com/mckinsey/vizro/pull/151))

## Changed

- The path to a custom assets folder is now configurable using the `assets_folder` argument when instantiating `Vizro` ([#151](https://github.com/mckinsey/vizro/pull/151))

## Fixed

- Assets are now routed correctly when hosting the dashboard in a subdirectory ([#151](https://github.com/mckinsey/vizro/pull/151))

## Security

- Bump werkzeug version suggested by Snyk to avoid a vulnerability: https://security.snyk.io/vuln/SNYK-PYTHON-WERKZEUG-6035177 ([#128](https://github.com/mckinsey/vizro/pull/128))

<a id='changelog-0.1.5'></a>

# 0.1.5 — 2023-10-26

## Removed

- Remove warning message if not all registered pages are used in `Navigation` ([#117](https://github.com/mckinsey/vizro/pull/117))

## Added

- Add plotly layout template for waterfall chart type ([#106](https://github.com/mckinsey/vizro/pull/106))

- Add CSS default styling for `textarea` ([#106](https://github.com/mckinsey/vizro/pull/106))

- Provide ID to unique outer HTML divs on page ([#111](https://github.com/mckinsey/vizro/pull/111))

- Enable turning off `marks` when `step` is defined in `Slider` and `RangeSlider` ([#115](https://github.com/mckinsey/vizro/pull/115))

## Changed

- Autopopulate `navigation.pages` with registered pages during `Dashboard` validation if `navigation.pages = None` ([#117](https://github.com/mckinsey/vizro/pull/117))

- Update warning for duplicated IDs in `data_manager` and `model_manager` to now recommend `Vizro._reset()` as a potential fix when working in a Jupyter notebook ([#120](https://github.com/mckinsey/vizro/pull/120))

## Fixed

- If the `targets` argument in the `export_data` action function is specified as `"falsy"` value (`None`, `[]`), triggering the action will result in the same outcome as if the argument were not set, exporting data from all charts on the current page. ([#93](https://github.com/mckinsey/vizro/pull/93))

- Fix alignment between control panel, dashboard title and page title ([#106](https://github.com/mckinsey/vizro/pull/106))

- `CapturedCallable` now handles variadic keywords arguments (`**kwargs`) correctly ([#121](https://github.com/mckinsey/vizro/pull/121))

## Security

- Bump @babel/traverse from 7.22.20 to 7.23.2 ([#118](https://github.com/mckinsey/vizro/pull/118))

<a id='changelog-0.1.4'></a>

# 0.1.4 — 2023-10-09

## Added

- Add highlighting to accordion button of active page ([#74](https://github.com/mckinsey/vizro/pull/74))

- Add validator for `Dashboard.navigation` to default to `Navigation()` if not provided ([#74](https://github.com/mckinsey/vizro/pull/74))

- Add comparison table to `Why Vizro` docs page ([#90](https://github.com/mckinsey/vizro/pull/90))

- Parameters can be optional: use the string `"NONE"` as an option of `Parameter.selector` to pass `None`([#95](https://github.com/mckinsey/vizro/pull/95))

- Raise `ModuleNotFoundError` in case the `export_data` action is used with `file_format="xlsx"` and neither `openpyxl` nor `xlsxwriter` are installed ([#97](https://github.com/mckinsey/vizro/pull/97))

## Changed

- Move creation of `dash.page_registry` to `Dashboard.pre_build` ([#74](https://github.com/mckinsey/vizro/pull/74))

- Change the default collapsible behavior and highlighting color of the selected accordion group ([#74](https://github.com/mckinsey/vizro/pull/74))

## Fixed

- Fix unit test interdependence issue due to shared dash.page_registry ([#84](https://github.com/mckinsey/vizro/pull/84))

- Fix bug of horizontal rulers not being visible in `Card` ([#91](https://github.com/mckinsey/vizro/pull/91))

- Fix bug so that `add_type` updates forward references in new type added ([#92](https://github.com/mckinsey/vizro/pull/92))

## Security

- Update pydantic requirement to `pydantic>=1.10.13, <2` due to medium Snyk vulnerability ([#83](https://github.com/mckinsey/vizro/pull/83))

<a id='changelog-0.1.3'></a>

# 0.1.3 — 2023-09-29

## Added

- Add a "why Vizro" section to the docs ([#73](https://github.com/mckinsey/vizro/pull/73))

## Changed

- Remove `left_side` container by default if there are no elements present ([#68](https://github.com/mckinsey/vizro/pull/68))

## Fixed

- Raise `ValueError` of shared column with inconsistent dtypes properly ([#64](https://github.com/mckinsey/vizro/pull/64))

<a id='changelog-0.1.2'></a>

# 0.1.2 — 2023-09-25

## Added

- Add additional information in case of duplicate `model_manager` ID's to guide users if this occurs in a Jupyter Notebooks. ([#59](https://github.com/mckinsey/vizro/pull/59))

## Changed

- Optimize the client-server communication ([#34](https://github.com/mckinsey/vizro/pull/34))

  - Eliminate most server side callbacks in favor of client-side callbacks
  - Add tests for client-side callbacks written in Node.js framework called `jest`.
  - Add hatch command `hatch run test-js` that runs unit tests written in `jest`.
  - Logging information now only displayed for action function carried out (no trigger or finished information)

- Replaced all screenshots in the docs to reflect new navigation designs ([#48](https://github.com/mckinsey/vizro/pull/48))

## Fixed

- Fixed issue of accordion arrow not loading on deployed demo version ([#44](https://github.com/mckinsey/vizro/pull/44))

<a id='changelog-0.1.1'></a>

# 0.1.1 — 2023-09-21

## Added

- Enable `title` argument in `Dashboard` model, which allows a title to be added on every page on top left-side ([#31](https://github.com/mckinsey/vizro/pull/31))

- Add the ability to use custom actions. Currently in beta, expect this to break at any time. ([#46](https://github.com/mckinsey/vizro/pull/46))

## Changed

- Provide ID to outer div to enable CSS customization of component and its sub-components ([#29](https://github.com/mckinsey/vizro/pull/29))

- Disable creation of accordion navigation if only one page is provided ([#32](https://github.com/mckinsey/vizro/pull/32))

- Change the structure of user-guides in documentation to group topics ([#42](https://github.com/mckinsey/vizro/pull/42)).

<a id='changelog-0.1.0'></a>

# 0.1.0 — 2023-09-08

## Added

- Add Vizro templates and enable choice of `light` and `dark` themes

- Enable integration of plotly express charts within Graph

- Enable data connections via Kedro data catalog

- Add ModelManager and DataManager class

- Add the Vizro class and enable parsing and running a dashboard

- Add the following pydantic models:

  - Action
  - Button
  - Card
  - Checklist
  - Dashboard
  - Dropdown
  - Filter
  - Graph
  - Layout
  - Navigation
  - Page
  - Parameter
  - RadioItems
  - RangeSlider
  - Slider
  - VizroBaseModel

- Enable the addition and usage of custom components and custom charts
