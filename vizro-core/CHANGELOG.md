# Changelog

<!-- All enhancements and patches to vizro will be documented
in this file.  It adheres to the structure of http://keepachangelog.com/.

This project adheres to Semantic Versioning (http://semver.org/). -->

## Unreleased

See the fragment files in the [changelog.d directory](https://github.com/mckinsey/vizro/tree/main/vizro-core/changelog.d).

<!-- scriv-insert-here -->

<a id='changelog-0.1.40'></a>

# 0.1.40 — 2025-06-03

## Highlights ✨

- Enable controls inside containers. See the [user guide on container](https://vizro.readthedocs.io/en/stable/pages/user-guides/container/#add-controls-to-container) for more details. ([#1094](https://github.com/mckinsey/vizro/pull/1094))

## Added

- Add `description` argument to `Tabs` to enable tooltips in the title. See the [user guide on container](https://vizro.readthedocs.io/en/stable/pages/user-guides/container/#add-a-tooltip) for an example. ([#1178](https://github.com/mckinsey/vizro/pull/1178))

- Enable `extra` argument for `vm.Graph`, which allows passing arguments directly to the underlying `dcc.Graph`. ([#1210](https://github.com/mckinsey/vizro/pull/1210))

## Fixed

- Fix a bug where assigning a custom action to `Filter.selector.actions` raised an error. ([#1197](https://github.com/mckinsey/vizro/pull/1197))

<a id='changelog-0.1.39'></a>

# 0.1.39 — 2025-05-16

## Added

- Add `description` argument to `Dashboard`, `Page`, `Container`, `Graph`, `AgGrid` and `Table` to enable tooltips in titles. See this [user guide](https://vizro.readthedocs.io/en/stable/pages/user-guides/container/#add-a-tooltip) for an example. ([#1144](https://github.com/mckinsey/vizro/pull/1144))

- Enable `title` inside `Tabs`. ([#1169](https://github.com/mckinsey/vizro/pull/1169))

## Changed

- Bump `dash>=3.0.0`, `dash-bootstrap-components>=2.0.0`, `dash-ag-grid>=31.3.1` and `dash-mantine-components>=1.0.0`. ([#1160](https://github.com/mckinsey/vizro/pull/1160))

## Fixed

- Fix bug where `dash_data_table` and `dash_ag_grid` callables with the same `id` would not raise an error but break the dashboard. ([#1159](https://github.com/mckinsey/vizro/pull/1159))

<a id='changelog-0.1.38'></a>

# 0.1.38 — 2025-04-24

## Added

- Add `collapsed` argument to `vm.Container` to enable collapsible containers. See the [user guide on collapsible container](https://vizro.readthedocs.io/en/stable/pages/user-guides/container/#collapsible-containers) for more details. ([#1079](https://github.com/mckinsey/vizro/pull/1079))

- Enable styling of `vm.Button` with a new argument `variant="plain"/"filled"/"outlined"`. See the [user guide on styled buttons](https://vizro.readthedocs.io/en/stable/pages/user-guides/button/#styled-buttons) for more details. ([#1114](https://github.com/mckinsey/vizro/pull/1114))

- Add `description` argument to `Checklist`, `Dropdown`, `RadioItems`, `Slider`, `RangeSlider` and `DatePicker` to enable tooltips in selector titles. See the [user guide on tooltips](https://vizro.readthedocs.io/en/stable/pages/user-guides/selectors/#add-a-tooltip) for more details. ([#1124](https://github.com/mckinsey/vizro/pull/1124))

## Changed

- Update the light theme for better consistency and contrast. Right-side and card backgrounds now adapt when a `Container` with `variant="filled"` is used. ([#1048](https://github.com/mckinsey/vizro/pull/1048))

- `actions` now have type `list[ActionType]` rather than `list[Action]`. ([#1054](https://github.com/mckinsey/vizro/pull/1054))

## Fixed

- Adjust the width and height of flex-items and grid-items dynamically based on the dimensions of their ancestor.([#1108](https://github.com/mckinsey/vizro/pull/1108))

- Update styling (font style, bg-color and hover effect) of `Card`. ([#1112](https://github.com/mckinsey/vizro/pull/1112))

<a id='changelog-0.1.37'></a>

# 0.1.37 — 2025-04-09

## Highlights ✨

- `Flex` model support for the `layout` argument of the `Page` and `Container`. See the [user guide on the `Flex` layout](https://vizro.readthedocs.io/en/stable/pages/user-guides/layouts/#flex-layout) for more details. ([#1050](https://github.com/mckinsey/vizro/pull/1050))

- Vizro models now have autocomplete functionality in IDEs when using the pydantic [plugin for VS Code](https://docs.pydantic.dev/latest/integrations/visual_studio_code/) or [for PyCharm](https://docs.pydantic.dev/latest/integrations/pycharm/). ([#1089](https://github.com/mckinsey/vizro/pull/1089))

## Added

- Add support for more CSS units (rem, em, %) for `row_min_height`, `row_gap`, `col_gap`, and `col_min_width` in `Layout`. ([#1050](https://github.com/mckinsey/vizro/pull/1050))

## Changed

- Improve mobile responsiveness: the flex layout breakpoint is now 764px (side panel collapsed) or 1064px (side panel expanded). ([#1097](https://github.com/mckinsey/vizro/pull/1097))

- Make `Container.title` mandatory only when used within `Tabs`. ([#1103](https://github.com/mckinsey/vizro/pull/1103))

## Deprecated

- `vm.Layout` has been renamed `vm.Grid`, and `vm.Layout` will no longer exist in Vizro 0.2.0. ([#1098](https://github.com/mckinsey/vizro/pull/1098))

<a id='changelog-0.1.36'></a>

# 0.1.36 — 2025-03-31

## Changed

- Add an `id` to the header and footer HTML elements of `Graph`, `Table`, and `AgGrid` to enable targeting through actions/callbacks. ([#1080](https://github.com/mckinsey/vizro/pull/1080))

## Fixed

- Fix `model_rebuild` errors originating from recent changes in pydantic 2.11. ([#1086](https://github.com/mckinsey/vizro/pull/1086))

<a id='changelog-0.1.35'></a>

# 0.1.35 — 2025-03-18

## Highlights ✨

- Add `vm.Text` component to easily add arbitrary text to your dashboard. See the user guide on the [`vm.Text` component](https://vizro.readthedocs.io/en/stable/pages/user-guides/text/) for more details. ([#1061](https://github.com/mckinsey/vizro/pull/1061))

## Added

- Enable styling of `vm.Container` with a new argument `variant="plain"/"filled"/"outlined"`. See the user guide on [styled containers](https://vizro.readthedocs.io/en/stable/pages/user-guides/container/#styled-containers) for more details. ([#1002](https://github.com/mckinsey/vizro/pull/1002))

- `DatePicker` filters update automatically when underlying dynamic data changes. See the user guide on [dynamic filters](https://vizro.readthedocs.io/en/stable/pages/user-guides/data/#filters) for more information. ([#1039](https://github.com/mckinsey/vizro/pull/1039))

- Add `extra` argument to selected models to enable passing arguments directly to the underlying Dash component. ([#1032](https://github.com/mckinsey/vizro/pull/1032))

- Dynamic data parameters automatically refresh the relevant dynamic filters. ([#1051](https://github.com/mckinsey/vizro/pull/1051))

## Changed

- Turn `AgGrid` background transparent. ([#1047](https://github.com/mckinsey/vizro/pull/1047))

## Fixed

- Fix a bug where an empty parameter selection incorrectly sent `[None]` to its target. ([#1026](https://github.com/mckinsey/vizro/pull/1026))

- Fix `datasets_from_catalog` for `kedro>=0.19.9`. ([#1063](https://github.com/mckinsey/vizro/pull/1063))

- `datasets_from_catalog` now loads the latest version of versioned datasets. ([#1063](https://github.com/mckinsey/vizro/pull/1063))

- `Filter` and `Parameter` can now be initialized before their targeted components. ([#1065](https://github.com/mckinsey/vizro/pull/1065))

<a id='changelog-0.1.34'></a>

# 0.1.34 — 2025-02-13

## Removed

- Remove export png button from modebar inside `Graph`. ([#1005](https://github.com/mckinsey/vizro/pull/1005))

## Added

- Add `reverse_color` argument to `kpi_card_reference`, enabling color inversion based on delta values. ([#995](https://github.com/mckinsey/vizro/pull/995))

- Kedro integration function `datasets_from_catalog` can handle dataset factories for `kedro>=0.19.9`. ([#1001](https://github.com/mckinsey/vizro/pull/1001))

## Changed

- Bump optional dependency lower bound to `kedro>=0.19.0`. ([#1001](https://github.com/mckinsey/vizro/pull/1001))

- Make chart background transparent when used inside dashboard. ([#1005](https://github.com/mckinsey/vizro/pull/1005))

## Fixed

- Fix a bug where `add_type` would raise an error if the `type` had already been added. ([#999](https://github.com/mckinsey/vizro/pull/999))

<a id='changelog-0.1.33'></a>

# 0.1.33 — 2025-02-05

## Fixed

- Adjust the lower bound of pydantic to `2.7.0` so that Vizro can run on `pyodide==0.26.2`. ([#993](https://github.com/mckinsey/vizro/pull/993))

<a id='changelog-0.1.32'></a>

# 0.1.32 — 2025-02-04

## Highlights ✨

- Vizro now uses Pydantic V2 for its models. This should not affect most users, but if you use custom components that rely on Pydantic V1 features then you should consult [Pydantic's migration guide](https://docs.pydantic.dev/latest/migration/) or use `vizro<0.1.32`. ([#917](https://github.com/mckinsey/vizro/pull/917))

- Release Vizro's Bootstrap theme that can be used in a pure Dash app with `Dash(external_stylesheets=[vizro.bootstrap])`. ([#970](https://github.com/mckinsey/vizro/pull/970))

## Changed

- Update `material-symbols-outlined.wolff2` to include the latest icons. ([#972](https://github.com/mckinsey/vizro/pull/972))

## Fixed

- Fix coloring of `NavLink` inside `NavBar`. ([#968](https://github.com/mckinsey/vizro/pull/968))

- Fix flickering scroll bars when using new Plotly map figures with `plotly==6.0.0`. ([#984](https://github.com/mckinsey/vizro/pull/984))

- Remove flash of unstyled text before Google Material icons font is loaded. ([#987](https://github.com/mckinsey/vizro/pull/987))

<a id='changelog-0.1.31'></a>

# 0.1.31 — 2025-01-23

## Changed

- Bumped library used for `vm.DatePicker` to `dash_mantine_components~=0.15.1`. ([#924](https://github.com/mckinsey/vizro/pull/924))

## Fixed

- Enable arbitrarily deep nesting of custom components within lists, tuples or dictionaries. ([#929](https://github.com/mckinsey/vizro/pull/929))

- Fix hidden axis and tick labels for Graph components using `px.parallel_coordinates`. ([#941](https://github.com/mckinsey/vizro/pull/941))

- Enable visibility of the spinner buttons in number inputs. ([#954](https://github.com/mckinsey/vizro/pull/954))

<a id='changelog-0.1.30'></a>

# 0.1.30 — 2024-12-16

## Removed

- Remove built-in CSS shortcuts `#floating-*` to float images. These can still be provided manually. ([#919](https://github.com/mckinsey/vizro/pull/919))

## Fixed

- Ensure the single-select dropdown value can be cleared when used as a dynamic filter. ([#915](https://github.com/mckinsey/vizro/pull/915))

- Remove static CSS that prevented header text from wrapping in `AgGrid`. ([#928](https://github.com/mckinsey/vizro/pull/928))

<a id='changelog-0.1.29'></a>

# 0.1.29 — 2024-12-03

## Highlights ✨

- Filters update automatically when underlying dynamic data changes. See the [user guide on dynamic filters](https://vizro.readthedocs.io/en/stable/pages/user-guides/data/#filters) for more information. ([#879](https://github.com/mckinsey/vizro/pull/879))

## Changed

- Custom controls can be nested arbitrarily deep inside `Page.controls`. ([#903](https://github.com/mckinsey/vizro/pull/903))

- Replace `dmc.Switch` with `dbc.Switch` and change CSS selectors accordingly. ([#907](https://github.com/mckinsey/vizro/pull/907))

<a id='changelog-0.1.28'></a>

# 0.1.28 — 2024-11-27

## Removed

- Removed all CSS variables from `variables.css` and `token_names.css`, replacing them with CSS variables from `vizro-bootstrap.min.css`. Refer to [`vizro-bootstrap.min.css`](https://github.com/mckinsey/vizro/blob/main/vizro-core/src/vizro/static/css/vizro-bootstrap.min.css) for the updated CSS variables. ([#886](https://github.com/mckinsey/vizro/pull/886))

## Added

- Enable `href` inside `vm.Button`. ([#881](https://github.com/mckinsey/vizro/pull/881))

## Changed

- Replace `dmc.Tabs` with `dbc.Tabs` and change CSS selectors accordingly. ([#895](https://github.com/mckinsey/vizro/pull/895))

<a id='changelog-0.1.27'></a>

# 0.1.27 — 2024-11-14

## Changed

- Improve performance of data loading. ([#850](https://github.com/mckinsey/vizro/pull/850), [#857](https://github.com/mckinsey/vizro/pull/857))

- Upper bound dependency `dash<3`. ([#877](https://github.com/mckinsey/vizro/pull/877))

## Fixed

- Fix 404 error page and page flickering on refresh. ([#865](https://github.com/mckinsey/vizro/pull/865))

<a id='changelog-0.1.26'></a>

# 0.1.26 — 2024-10-30

## Removed

- Drop support for Python 3.8. ([#813](https://github.com/mckinsey/vizro/pull/813))

## Added

- Add support for Python 3.13. ([#813](https://github.com/mckinsey/vizro/pull/813))

## Fixed

- Fix paths to Vizro assets on Windows. ([#837](https://github.com/mckinsey/vizro/pull/837))

<a id='changelog-0.1.25'></a>

# 0.1.25 — 2024-10-15

## Added

- All Vizro resources are served through a CDN when `serve_locally=False`. ([#775](https://github.com/mckinsey/vizro/pull/775))

## Fixed

- Remove extraneous `<link>` to font file. ([#775](https://github.com/mckinsey/vizro/pull/775))

- Fix user override of Vizro's JavaScript resources. ([#775](https://github.com/mckinsey/vizro/pull/775))

- Remove unnecessarily repeated loading of data. ([#802](https://github.com/mckinsey/vizro/pull/802))

<a id='changelog-0.1.24'></a>

# 0.1.24 — 2024-10-01

## Added

- Add `id` to `title` of `Graph`, `Table`, `AgGrid` and `Container`. ([#705](https://github.com/mckinsey/vizro/pull/705))

- Theme switcher can now switch between light and dark logos. ([#745](https://github.com/mckinsey/vizro/pull/745))

## Changed

- Changed dependency from `ruff` to `black` and `autoflake` in order to facilitate installation on pyodide. ([#757](https://github.com/mckinsey/vizro/pull/757))

## Fixed

- Enable overwriting global `font-family` in vizro chart templates. ([#717](https://github.com/mckinsey/vizro/pull/717))

<a id='changelog-0.1.23'></a>

# 0.1.23 — 2024-09-12

## Fixed

- Fix incompatibility with older `plotly versions` due to chart template update. ([#695](https://github.com/mckinsey/vizro/pull/695))

<a id='changelog-0.1.22'></a>

# 0.1.22 — 2024-09-10

## Removed

- Remove automatic alignment for chart title when it's specified within a Plotly chart. A warning will now suggest using `Graph.title` instead. ([#669](https://github.com/mckinsey/vizro/pull/669))

## Added

- Enable `header` and `footer` argument inside `Graph`, `Table` and `AgGrid`. ([#669](https://github.com/mckinsey/vizro/pull/669))

- Enable `title` argument inside `Graph`. ([#669](https://github.com/mckinsey/vizro/pull/669))

- Add chart layout template specification for `map_style`. ([#677](https://github.com/mckinsey/vizro/pull/677))

## Fixed

- Fix bug that prevented `VizroBaseModel._to_python()` to convert `dict` fields of models correctly. ([#660](https://github.com/mckinsey/vizro/pull/660))

- Fix dynamically calculated row height for `Dropdown` when the options are provided as dictionaries. ([#672](https://github.com/mckinsey/vizro/pull/672))

<a id='changelog-0.1.21'></a>

# 0.1.21 — 2024-08-28

## Changed

- Improve page loading time for `AgGrid`, `Table` and `Figure`. ([#644](https://github.com/mckinsey/vizro/pull/644))

- Optimize vizro templates `vizro_dark` and `vizro_light` for charts. ([#645](https://github.com/mckinsey/vizro/pull/645))

## Fixed

- Fix persistence of `columnSize` and `selectedRows` for `AgGrid`. ([#644](https://github.com/mckinsey/vizro/pull/644))

<a id='changelog-0.1.20'></a>

# 0.1.20 — 2024-08-20

## Added

- Add validation error message if `CapturedCallable` is directly provided. ([#590](https://github.com/mckinsey/vizro/pull/590))

- Create `vizro.figures.library` to contain KPI card Dash components that can be used outside the Vizro framework. ([#578](https://github.com/mckinsey/vizro/pull/578))

- Add dark mode and loading spinner to the layout loading screen (before Vizro app is shown). ([#598](https://github.com/mckinsey/vizro/pull/598))

## Changed

- Serve Google Material icons library locally to enable offline functionality. ([#578](https://github.com/mckinsey/vizro/pull/578))

- Disable altering the default plotly template by importing Vizro. ([#615](https://github.com/mckinsey/vizro/pull/615))

## Fixed

- Fix subclassing of `vm.Graph`, `vm.Table`, `vm.AgGrid`, `vm.Figure` and `vm.Action` models. ([#606](https://github.com/mckinsey/vizro/pull/606))

- Fix display of marks in `vm.Slider` and `vm.RangeSlider` by converting floats to integers when possible. ([#613](https://github.com/mckinsey/vizro/pull/613))

- Update chart title padding dynamically to prevent subtitle cutoff. ([#632](https://github.com/mckinsey/vizro/pull/632))

<a id='changelog-0.1.19'></a>

# 0.1.19 — 2024-07-16

## Removed

- Remove `demo` dashboard folder from repository. ([#581](https://github.com/mckinsey/vizro/pull/581))

## Added

- Improve validation error messages for `CapturedCallable`. ([#547](https://github.com/mckinsey/vizro/pull/547))

- Vizro app itself implements WSGI interface as a shortcut to `app.dash.server`. ([#580](https://github.com/mckinsey/vizro/pull/580))

## Changed

- Include sign in default `reference_format` of `kpi_card_reference`. ([#549](https://github.com/mckinsey/vizro/pull/549))

- Update `optionHeight` of `vm.Dropdown` dynamically based on character length. ([#574](https://github.com/mckinsey/vizro/pull/574))

- Rename `features` demo dashboard folder to `dev`. ([#581](https://github.com/mckinsey/vizro/pull/581))

## Fixed

- Fix title disappearance when scrolling `dash_data_table`. ([#548](https://github.com/mckinsey/vizro/pull/548))

- Ensure that categorical selectors always return a list of values. ([#562](https://github.com/mckinsey/vizro/pull/562))

- Remove default icon provision for `vm.NavLink` when the icon count exceeds 9 and a user icon is provided.([#572](https://github.com/mckinsey/vizro/pull/572))

- External `href` links in `vm.Card` now open in the full body of the window as opposed to in the same frame as they were clicked. ([#585](https://github.com/mckinsey/vizro/pull/585))

<a id='changelog-0.1.18'></a>

# 0.1.18 — 2024-06-24

## Highlights ✨

- Introduce `Figure` as a new `Page` component, enabling all Dash components to be reactive in `Vizro`. See the [user guide on figure](https://vizro.readthedocs.io/en/stable/pages/user-guides/figure/) for more information. ([#493](https://github.com/mckinsey/vizro/pull/493), [#524](https://github.com/mckinsey/vizro/pull/524))

- Introduce KPI card functions to be used inside `Figure`. See the [user guide on KPI cards](https://vizro.readthedocs.io/en/stable/pages/user-guides/figure#key-performance-indicator-kpi-cards) for more information. ([#493](https://github.com/mckinsey/vizro/pull/493), [#529](https://github.com/mckinsey/vizro/pull/529))

## Added

- Add KPI dashboard to examples. ([#505](https://github.com/mckinsey/vizro/pull/505))

## Changed

- Turn off `pagination` by default in `dash_ag_grid`. ([#512](https://github.com/mckinsey/vizro/pull/512))

- Move changing theme callback to the client-side. ([#523](https://github.com/mckinsey/vizro/pull/523))

## Fixed

- Fix disappearance of charts after theme switch on mobile. ([#511](https://github.com/mckinsey/vizro/pull/511))

- Ignore unexpected query parameters rather than raising an exception. ([#539](https://github.com/mckinsey/vizro/pull/539))

<a id='changelog-0.1.17'></a>

# 0.1.17 — 2024-05-30

## Highlights ✨

- Enable dynamic data parametrization, so that different data can be loaded while the dashboard is running. ([#482](https://github.com/mckinsey/vizro/pull/482))

## Removed

- Remove all CSS classes with suffix `_outer` from components. Visit the user guide on [how to customize CSS in selected components](https://vizro.readthedocs.io/en/stable/pages/user-guides/custom-css/#overwrite-css-for-selected-components) for more details. ([#456](https://github.com/mckinsey/vizro/pull/456))

## Changed

- Store `page.id` in outer page container to enable page specific styling. ([#455](https://github.com/mckinsey/vizro/pull/455))

- Change the default of the `dash_ag_grid` function to the default of the underlying Dash `dag.AgGrid`. ([#446](https://github.com/mckinsey/vizro/pull/446))

## Fixed

- Fix `dash_data_table` cell dropdown menu to open on click. ([#481](https://github.com/mckinsey/vizro/pull/481))

- Fix bug that [prevented referring to columns in custom grids/tables](https://github.com/mckinsey/vizro/issues/435). ([#439](https://github.com/mckinsey/vizro/pull/439))

- Fix an issue that prevented the column widths of the AgGrid to render correctly upon reloading a page. ([#446](https://github.com/mckinsey/vizro/pull/446))

- Fix actions associated with a manually added control. ([#478](https://github.com/mckinsey/vizro/pull/478))

<a id='changelog-0.1.16'></a>

# 0.1.16 — 2024-04-30

## Removed

- Remove class names `checkboxes-list`, `radio-items-list` and `input-container` from Vizro stylesheets. ([#414](https://github.com/mckinsey/vizro/pull/414))

## Changed

- Update design of dashboard layout. ([#433](https://github.com/mckinsey/vizro/pull/433))

<a id='changelog-0.1.15'></a>

# 0.1.15 — 2024-04-15

## Highlights ✨

- Add dynamic data, which can be reloaded while the dashboard is running. An optional caching layer enables efficient refreshes with per-data source timeouts. Visit the [user guide on data](https://vizro.readthedocs.io/en/stable/pages/user-guides/data/) for more details. ([#398](https://github.com/mckinsey/vizro/pull/398))

## Changed

- Replace default bootstrap stylesheet with `vizro-bootstrap` stylesheet. ([#384](https://github.com/mckinsey/vizro/pull/384))

- Refactor code and remove custom classNames from `Button`, `Card`, `NavBar` and `NavLink`. ([#384](https://github.com/mckinsey/vizro/pull/384))

- Change default continuous color scale to `SEQUENTIAL_CYAN`. ([#407](https://github.com/mckinsey/vizro/pull/407))

## Fixed

- Fix CSS for `floatingFilter` in `AgGrid`. ([#388](https://github.com/mckinsey/vizro/pull/388))

<a id='changelog-0.1.14'></a>

# 0.1.14 — 2024-03-26

## Highlights ✨

- Introduce `DatePicker` as a new selector for`Filter` and `Parameter`. Visit the [user guide on selectors](https://vizro.readthedocs.io/en/stable/pages/user-guides/selectors/) for more details. ([#309](https://github.com/mckinsey/vizro/pull/309))

## Changed

- Replace `dmc.Tooltip` with `dbc.Tooltip` and change CSS selectors accordingly. ([#361](https://github.com/mckinsey/vizro/pull/361))

- Rename CSS classNames `nav_card_container` and `card_container` to `nav-card` and `card`. ([#373](https://github.com/mckinsey/vizro/pull/373))

## Fixed

- Fix navigation to external links by replacing `dcc.Link` with `dbc.NavLink`. ([#364](https://github.com/mckinsey/vizro/pull/364))

<a id='changelog-0.1.13'></a>

# 0.1.13 — 2024-03-12

### Highlights ✨

- Introduce `AgGrid` as a new `Page` component, allowing the usage of [AG Grid](https://www.ag-grid.com/) in `Vizro`. See the [user guide on tables](https://vizro.readthedocs.io/en/stable/pages/user_guides/table/) for more information. ([#289](https://github.com/mckinsey/vizro/pull/289),[#268](https://github.com/mckinsey/vizro/pull/268),[#324](https://github.com/mckinsey/vizro/pull/324))

## Changed

- Apply new design to `Slider` and `RangeSlider`. ([#336](https://github.com/mckinsey/vizro/pull/336))
- Consolidate gaps between selectors. ([#336](https://github.com/mckinsey/vizro/pull/336))

## Fixed

- Fix path to built-in Vizro assets when `requests_pathname_prefix` is not the same as `routes_pathname_prefix`. ([#358](https://github.com/mckinsey/vizro/pull/358))

<a id='changelog-0.1.12'></a>

# 0.1.12 — 2024-03-04

## Changed

- Temporarily exclude `dash==2.16.0` ([#341](https://github.com/mckinsey/vizro/pull/341))

## Fixed

- Added default Bootstrap theme to external stylesheets and fix any visually incompatible CSS declarations. ([#311](https://github.com/mckinsey/vizro/pull/311))

- Fix CSS bug on `page-main` overflowing `page-container` in mobile layouts. ([#331](https://github.com/mckinsey/vizro/pull/331))

<a id='changelog-0.1.11'></a>

# 0.1.11 — 2024-02-13

## Fixed

- Improve layouts for small devices. ([#302](https://github.com/mckinsey/vizro/pull/302))

<a id='changelog-0.1.10'></a>

# 0.1.10 — 2024-01-31

## Highlights ✨

- Introduce `Tabs` model as a new `Page` component. ([#280](https://github.com/mckinsey/vizro/pull/280))

## Changed

- Replace `html.P` with `html.Label` in form components. ([#293](https://github.com/mckinsey/vizro/pull/293))

## Fixed

- Fix bug on accordion group not opening properly when re-directing to active page via navigation card or URL path. ([#276](https://github.com/mckinsey/vizro/pull/276))

<a id='changelog-0.1.9'></a>

# 0.1.9 — 2024-01-25

## Highlights ✨

- Introduce `Container` model as a new `Page` component. Visit the [user guide on container](https://vizro.readthedocs.io/en/stable/pages/user_guides/container/) to learn more. ([#254](https://github.com/mckinsey/vizro/pull/254))

## Added

- Enable automatic logo insertion into `page-header` container. ([#248](https://github.com/mckinsey/vizro/pull/248))

- Enable the side panel to collapse/expand with a button. ([#225](https://github.com/mckinsey/vizro/pull/225))

## Changed

- Move `dashboard-title` to top header container `page-header`. ([#238](https://github.com/mckinsey/vizro/pull/238))

## Fixed

- Add CSS for `dmc.Switch` and fix CSS when toggle-switch is turned on. ([#244](https://github.com/mckinsey/vizro/pull/244))

- Fix bug of `value` argument not properly being evaluated in `Slider` and `RangeSlider`. ([#266](https://github.com/mckinsey/vizro/pull/266))

- Fix bug on scrolling and viewport on Safari. ([#277](https://github.com/mckinsey/vizro/pull/277))

<a id='changelog-0.1.8'></a>

# 0.1.8 — 2024-01-04

## Added

- When set, the dashboard title appears alongside the individual page title as the text labeling a browser tab. ([#228](https://github.com/mckinsey/vizro/pull/228))

- Enable adding description and image to the meta tags. ([#185](https://github.com/mckinsey/vizro/pull/185))

## Changed

- Re-arrange main containers on page and change their CSS IDs. ([#205](https://github.com/mckinsey/vizro/pull/205))

## Fixed

- Fix position of invisible button inside `Card`. ([#236](https://github.com/mckinsey/vizro/pull/236))

- Fix a bug that prevented the update of nested graph properties through parameters when the graph property was not previously defined. ([#273](https://github.com/mckinsey/vizro/pull/237))

<a id='changelog-0.1.7'></a>

# 0.1.7 — 2023-12-15

## Highlights ✨

- Release of custom actions. Visit the [user guide on custom actions](https://vizro.readthedocs.io/en/stable/pages/user_guides/custom_actions/) to learn more. ([#178](https://github.com/mckinsey/vizro/pull/178))

- Add `NavBar` and `NavLink` models to enable a hierarchical navigation bar with icons. Visit the [user guide on navigation](https://vizro.readthedocs.io/en/stable/pages/user_guides/navigation/) to learn more. ([#70](https://github.com/mckinsey/vizro/pull/70))

## Added

- Enable tooltips for `NavLink` ([#186](https://github.com/mckinsey/vizro/pull/186))

## Changed

- Change the persistence of client-side data to `session` rather than `local` ([#182](https://github.com/mckinsey/vizro/pull/182))

- Bump dash lower bound to 2.14.1 ([#203](https://github.com/mckinsey/vizro/pull/203))

## Fixed

- Remove graph flickering on page load with Vizro light theme ([#166](https://github.com/mckinsey/vizro/pull/166))

- Fix `vm.Slider` and `vm.RangeSlider` to work with incorrect text input ([#173](https://github.com/mckinsey/vizro/pull/173))

- Remove default font color from global CSS to enable overwrites ([#213](https://github.com/mckinsey/vizro/pull/213))

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
