
<a id='changelog-0.1.7'></a>
# 0.1.7 — 2026-06-02

## Added

- Add `example_ag_grid.py` reference to `dashboard-build` with canonical Vizro AG Grid patterns (drop-in `dash_ag_grid` factory and custom `@capture("ag_grid")`), plus explicit guidance on what to ignore: `vm.Table` / Dash DataTable, Plotly-as-table hacks, and JS-only AG Grid features. ([#1744](https://github.com/mckinsey/vizro/pull/1744))
- Add a `## Tables` section to `selecting-vizro-charts` so table-related guidance lives next to chart and KPI guidance. ([#1744](https://github.com/mckinsey/vizro/pull/1744))
- Add `assets/` folder to `dashboard-design` and `dashboard-build` skills, holding the 5 spec templates (`1_information_architecture.md`, `2_interaction_ux.md`, `3_visual_design.md`, `4_implementation.md`, `5_test_report.md`) per the Anthropic skill convention. ([#1744](https://github.com/mckinsey/vizro/pull/1744))

## Changed

- Migrate all 5 spec outputs from YAML to markdown. Templates ship in `assets/` and are copied into the project's `spec/` directory. The SKILL.md "REQUIRED OUTPUT" sections now point to the template files instead of embedding them inline. ([#1744](https://github.com/mckinsey/vizro/pull/1744))
- Strengthen Step 2 (Browser Testing) in `dashboard-build`: (1) Playwright install now uses `--with-deps chromium` so it works on slim Linux base images (Docker, CI runners, devcontainers) where the plain install fails at launch; (2) the testing flow is reframed as "batch errors, don't loop one-at-a-time" — collect all errors in a single walk, batch the fixes, restart the dashboard once, and re-walk. ([#1744](https://github.com/mckinsey/vizro/pull/1744))

<a id='changelog-0.1.6'></a>
# 0.1.6 — 2026-05-20

## Added

- Add `wiring-vizro-actions` skill with 5 interaction patterns: Hierarchical Drill-Down, Single-Page Drill-Down, Comparison Spotlight, Multi-Dimensional Slice, and Data Export. ([#1737](https://github.com/mckinsey/vizro/pull/1737))

<a id='changelog-0.1.5'></a>

# 0.1.5 — 2026-04-10

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
