<!--
A new scriv changelog fragment.

Uncomment the section that is right (remove the HTML comment wrapper).
-->

### Highlights ✨

- Keep controls in sync: a `Filter` or `Parameter` can now list another control's `id` in its `targets` so that changing one control automatically applies the same value to the other. The synced control can be on the same page or on a **different page**, in which case a value set on one page is applied to the synced control when its page is opened, making it possible to build dashboard-wide "global controls". See the [user guide on syncing controls](https://vizro.readthedocs.io/en/stable/pages/user-guides/controls/#sync-controls) for more details. ([#1723](https://github.com/mckinsey/vizro/pull/1723))

<!--
### Removed

- A bullet item for the Removed category with a link to the relevant PR at the end of your entry, e.g. Enable feature XXX. ([#1](https://github.com/mckinsey/vizro/pull/1))

-->
### Added

- Drill-through (a `set_control` triggered from a figure or component such as `Graph`, `AgGrid`, `Button` or `Card`) can now target a control on a different page **without that control needing `show_in_url=True`**. ([#1723](https://github.com/mckinsey/vizro/pull/1723))
- [`set_control`][vizro.actions.set_control] can now target multiple controls at once: pass a list of control ids to `control`. A single action sets them all (one callback and one confirmation notification). ([#1723](https://github.com/mckinsey/vizro/pull/1723))

<!--
### Changed

- A bullet item for the Changed category with a link to the relevant PR at the end of your entry, e.g. Enable feature XXX. ([#1](https://github.com/mckinsey/vizro/pull/1))

-->
<!--
### Deprecated

- A bullet item for the Deprecated category with a link to the relevant PR at the end of your entry, e.g. Enable feature XXX. ([#1](https://github.com/mckinsey/vizro/pull/1))

-->
### Fixed

- Fixed `set_control` targeting a `TimePicker(range=True)` or `DateTimePicker(range=True)` control so it now triggers that control's actions (e.g. its `update_targets`), matching every other selector. ([#1723](https://github.com/mckinsey/vizro/pull/1723))

<!--
### Security

- A bullet item for the Security category with a link to the relevant PR at the end of your entry, e.g. Enable feature XXX. ([#1](https://github.com/mckinsey/vizro/pull/1))

-->
