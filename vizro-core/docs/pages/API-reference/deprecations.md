# Deprecations and breaking changes

This page lists Vizro features that are now deprecated and forthcoming breaking changes for Vizro 0.2.0.

## `Layout` model

The [`Layout`][vizro.models.Layout] model has been renamed [`Grid`][vizro.models.Grid], and `Layout` will no longer exist in Vizro 0.2.0. To ensure future compatibility, replace your references to `vm.Layout` with `vm.Grid`.
