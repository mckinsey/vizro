<a id='changelog-0.1.5'></a>

# 0.1.5 — 2026-04-09

## Added

- Add eval framework (`evals/evals.json`) with 3 business-first test cases, validation scripts (`validate_colors.py`, `validate_aggregation.py`), and Playwright Python fallback for browser testing. ([#1692](https://github.com/mckinsey/vizro/pull/1692))

## Changed

- Make Step 2 (Testing) in dashboard-build non-optional, strengthen pre-aggregation guidance, and add `vizro.plotly.express` import warning. ([#1692](https://github.com/mckinsey/vizro/pull/1692))

<a id='changelog-0.1.4'></a>

# 0.1.4 — 2026-03-19

## Added

- Add three reusable skills (`designing-vizro-layouts`, `selecting-vizro-charts`, `writing-vizro-yaml`) extracted from duplicated logic across existing skills. ([#1661](https://github.com/mckinsey/vizro/pull/1662))

## Changed

- Refactor `dashboard-design` and `dashboard-build` skills to reference the new reusable skills, removing duplicated content and improving maintainability. ([#1661](https://github.com/mckinsey/vizro/pull/1662)) <a id='changelog-0.1.3'></a>

# 0.1.3 — 2026-03-04

## Changed

- Update color references in dashboard-design skill to align with Vizro 0.1.52 colorblind-safe palette. <a id='changelog-0.1.2'></a>

# 0.1.2 — 2026-02-17

## Changed

- Add instruction for Cursor setup. ([#1580](https://github.com/mckinsey/vizro/pull/1580)) <a id='changelog-0.1.1'></a>

# 0.1.1 — 2026-01-23

## Fixed

- Stronger guidance to model to not use custom charts as KPI cards. ([#1553](https://github.com/mckinsey/vizro/pull/1553)) <a id='changelog-0.1.0'></a>

# 0.1.0 — 2026-01-21

## Added

- Initial release of vizro-e2e-flow Claude Code plugin with `dashboard-design` and `dashboard-build` Agent Skills. ([#1481](https://github.com/mckinsey/vizro/pull/1481))
