# Changelog

<!-- All enhancements and patches to vizro will be documented
in this file.  It adheres to the structure of http://keepachangelog.com/.

This project adheres to Semantic Versioning (http://semver.org/). -->

## Unreleased

See the fragment files in the [changelog.d directory](https://github.com/mckinsey/vizro/tree/main/vizro-core/changelog.d).

<!-- scriv-insert-here -->

<a id='changelog-0.1.2'></a>

# 0.1.2 — 2023-09-25

## Added

- Add additional information in case of duplicate `model_manager` ID's to guide users if this occurs in a Jupyter Notebooks. ([#59](https://github.com/mckinsey/vizro/pull/59))

## Changed

- Optimize the client-server communication ([#34](https://github.com/mckinsey/vizro/pull/34))

  - Eliminate most server side callbacks in favour of client-side callbacks
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
