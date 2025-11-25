---
name: test-iterate
description: Stage 5 of Vizro dashboard development. USE AFTER completing development-implementation. Test basic dashboard functionality - launches successfully, no console errors, navigation and controls work.
---

# Test & Iterate for Vizro Dashboards

## Overview

Test that your dashboard works correctly before sharing with stakeholders. This stage uses **Playwright MCP** (pre-configured with this plugin) to automate browser testing and catch obvious issues.

**Key Focus**: Verify the dashboard launches, has no errors, navigation of each page works, controls function.

**Out of Scope**: Performance testing, usability studies, deployment preparation, and production monitoring.

**Tool**: Playwright MCP for browser automation - launches dashboard, tests interactions, checks console errors, and captures screenshots.

## REQUIRED OUTPUT: spec/5_test_report.yaml

Create a test report documenting test results:

```yaml
# spec/5_test_report.yaml
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
next_steps: list[string]
```

## Testing Workflow

### Testing Checklist

Run through these basic checks to test your dashboard:

**1. Launch Check**

- [ ] Dashboard starts without errors
- [ ] URL loads successfully
- [ ] No startup errors in console

**2. Page Navigation**

- [ ] All pages load correctly
- [ ] Navigation between pages works
- [ ] No broken links or 404 errors

**3. Controls and Interactions**

- [ ] Filter selections update visualizations
- [ ] Dropdowns, radio buttons, sliders work
- [ ] Any export buttons function

**4. Console Errors**

- [ ] No JavaScript errors in console
- [ ] No failed callbacks

### Using Playwright MCP

Use natural language commands to test your dashboard. Playwright MCP will automatically:
- Open the dashboard in a browser
- Navigate and interact with elements
- Check console for errors
- Capture screenshots
- Report any issues found

**Example commands**:

```
"Launch the dashboard at http://localhost:8050 and check if it starts without errors"

"Navigate through all pages and confirm they load correctly"

"Test the regional filter - select a few options and verify charts update"

"Check the browser console for any errors or failed callbacks"
```

## Fix Issues Found

After identifying issues, fix them directly.

## Iterate and Retest

After fixing issues:

1. **Retest** the specific items that were broken
1. **Quick smoke test** to ensure fixes didn't break anything else
1. **Repeat** until no critical issues remain

**When to Stop**: When the dashboard launches cleanly, navigation works, core controls function, and there are no console errors.

## Completion Criteria

Your dashboard is ready when:

- [ ] Dashboard launches without errors
- [ ] All pages navigate correctly
- [ ] Core filters and controls work
- [ ] No console errors

**Next Step**: Dashboard is tested and ready to share with stakeholders.
