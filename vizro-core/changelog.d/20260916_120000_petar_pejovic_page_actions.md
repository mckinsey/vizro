### Fixed

- User-defined `Page.actions` are now respected and run when the page opens, instead of being silently replaced by the automatic on-page-load refresh. Include `va.update_targets()` in the chain to keep refreshing figures, or set `actions=[]` to disable the automatic refresh (for example to defer loading expensive data). See [more examples of actions when page loads](https://vizro.readthedocs.io/en/stable/pages/user-guides/page-actions.md). ([#1863](https://github.com/mckinsey/vizro/pull/1863))
