---
name: test-iterate
description: Stage 5 of Vizro dashboard development. USE AFTER completing development-implementation. Test basic dashboard functionality - launches successfully, no console errors, navigation and controls work.
---

# Test & Iterate for Vizro Dashboards

**Key Focus**: Verify dashboard launches, no errors, navigation works, controls function.

**Tool**: Playwright MCP (pre-configured) for browser automation.

**Out of Scope**: Performance testing, usability studies, deployment.

## REQUIRED OUTPUT: spec/5_test_report.yaml

```yaml
launch:
  successful: boolean
  errors: list[string]

navigation:
  all_pages_work: boolean
  issues: list[string]

controls:
  filters_work: boolean
  issues: list[string]

console:
  no_errors: boolean
  errors_found: list[string]

dashboard_ready: boolean
```

## Testing Checklist

1. **Launch**: Dashboard starts, URL loads, no startup errors
2. **Navigation**: All pages load, no broken links
3. **Controls**: Filters update visualizations, dropdowns/sliders work
4. **Console**: No JavaScript errors or failed callbacks

## Done When

- Dashboard launches without errors
- All pages navigate correctly
- Core controls work
- No console errors
