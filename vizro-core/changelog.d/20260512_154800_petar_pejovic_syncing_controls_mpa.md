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

- `Filter` and `Parameter` can now sync a control on a **different page** by listing its id in `targets`, so a value set on one page is applied to the synced control when its page is opened. This makes it possible to build dashboard-wide "global controls". See the [user guide on syncing controls across pages](https://vizro.readthedocs.io/en/stable/pages/user-guides/controls/#sync-controls-across-pages). ([#1853](https://github.com/mckinsey/vizro/pull/1853))
- Drill-through (a `set_control` triggered from a figure or component such as `Graph`, `AgGrid`, `Button` or `Card`) can now target a control on a different page **without that control needing `show_in_url=True`**; Vizro navigates to the target page and applies the value there. ([#1853](https://github.com/mckinsey/vizro/pull/1853))

<!--
### Changed

- A bullet item for the Changed category with a link to the relevant PR at the end of your entry, e.g. Enable feature XXX. ([#1](https://github.com/mckinsey/vizro/pull/1))

-->
<!--
### Deprecated

- A bullet item for the Deprecated category with a link to the relevant PR at the end of your entry, e.g. Enable feature XXX. ([#1](https://github.com/mckinsey/vizro/pull/1))

-->
<!--
### Fixed

- A bullet item for the Fixed category with a link to the relevant PR at the end of your entry, e.g. Enable feature XXX. ([#1](https://github.com/mckinsey/vizro/pull/1))

-->
<!--
### Security

- A bullet item for the Security category with a link to the relevant PR at the end of your entry, e.g. Enable feature XXX. ([#1](https://github.com/mckinsey/vizro/pull/1))

-->
