---
name: test-iterate
description: Stage 5 of Vizro dashboard development. USE AFTER completing development-implementation. Validates basic dashboard functionality - launches successfully, no console errors, navigation and controls work, layout appears correct.
---

# Test & Iterate for Vizro Dashboards

## Overview

Test & Iterate validates that your dashboard works correctly before sharing with stakeholders. This is a basic smoke test to catch obvious issues.

**Key Focus**: Verify the dashboard launches, has no errors, navigation of each page works, controls function, and layout looks reasonable.

**Out of Scope**: Performance testing, usability studies, deployment preparation, and production monitoring.

## MCP-Based Testing (Recommended)

### Overview

For testing, use Playwright MCP server that enables AI-assisted browser automation. This tool allows Claude to directly test your dashboard by interacting with the UI and checking for issues.

**Good news**: Playwright MCP is **pre-configured** with the vizro-e2e-flow plugin! It's automatically available when you install this plugin - no additional setup required.

### Recommended MCP Server

#### Playwright MCP - For Functional Testing

**What it does**: Browser automation to test navigation, interactions, console errors, and screenshots

**Status**: ✅ **Pre-configured with this plugin** - ready to use immediately!

**Manual setup** (if needed): See `references/mcp_setup.md` in the development-implementation skill for installation instructions.

**Use for**:
- Testing page navigation
- Clicking filters and controls
- Verifying interactive elements work
- Checking console for errors
- Taking screenshots to verify layout
- Inspecting page structure

**Example**: Ask Claude "Test navigation - visit all dashboard pages and confirm they load" or "Check for console errors and take screenshots of all pages"

### Testing Without MCP

The vizro-e2e-flow plugin includes Playwright MCP pre-configured. If for some reason MCP is not available, you can fall back to:
- **Manual testing**: Open the dashboard and manually test
- **Browser DevTools**: Use F12 to check console errors manually
- **Python scripts**: Write Selenium/Playwright automation scripts

However, MCP-based testing is **significantly faster** for basic validation.

## Basic Functional Testing

### Testing Checklist

Run through these basic checks to validate your dashboard:

**1. Launch Check**
- [ ] Dashboard starts without errors
- [ ] URL loads successfully
- [ ] No startup errors in console

**2. Page Navigation**
- [ ] All pages load correctly
- [ ] Navigation between pages works
- [ ] No broken links or 404 errors
- [ ] Browser back/forward buttons work

**3. Controls and Interactions**
- [ ] Filters can be opened and selections made
- [ ] Filter selections update visualizations
- [ ] Dropdowns, radio buttons, sliders work
- [ ] Interactive charts respond to clicks/hovers
- [ ] Any export buttons function

**4. Console Errors**
- [ ] No JavaScript errors in console
- [ ] No failed network requests
- [ ] No warnings about missing data

**5. Layout Check (via Screenshots)**
- [ ] Overall layout looks correct (not overlapping/broken)
- [ ] Charts are visible and rendered
- [ ] Text is readable (not cut off)
- [ ] Filters and controls are positioned correctly
- [ ] Navigation is visible and usable

### Example Testing Workflow with Claude

**Simple natural language commands**:

```
"Launch the dashboard and check if it starts without errors"

"Navigate through all pages and confirm they load correctly"

"Test the regional filter - select a few options and verify charts update"

"Check the browser console for any errors"

"Take screenshots of each page so I can verify the layout looks correct"
```

Claude will use the MCP tools to:
1. Open your dashboard in a browser
2. Navigate and interact with elements
3. Check console for errors
4. Capture screenshots
5. Report any issues found

## Test Results

### Document Issues Found

After testing, create a simple list of issues to address:

**Issue Report Format**:
```
✅ Working Correctly:
- Dashboard launches successfully
- All 3 pages load correctly
- Regional filter works as expected

❌ Issues Found:
- Console error: "Cannot read property 'data' of undefined" on Details page
- Export button does not respond to clicks
- Product filter dropdown appears empty (no options)

⚠️ Layout Concerns:
- KPI cards on Overview page appear slightly misaligned
- Chart legend is cut off on mobile view (from screenshot)
```

### Share with Developers

Present your findings to the development team and discuss which issues need fixing:

**Quick Discussion**:
- Show the issue list
- Show screenshots highlighting layout problems
- Ask: "Which of these should we fix before considering the dashboard complete?"

**Common Quick Fixes**:
- Console errors → Usually data loading or missing error handling
- Broken controls → Check component IDs and callback connections
- Layout issues → Adjust container sizing or chart dimensions
- Missing filter options → Verify data source and column names

## Iterate and Retest

After developers fix issues:

1. **Retest** the specific items that were broken
2. **Quick smoke test** to ensure fixes didn't break anything else
3. **Update issue list** with current status
4. **Repeat** until no critical issues remain

**When to Stop**: When the dashboard launches cleanly, navigation works, core controls function, and there are no console errors.

## Completion Criteria

Your dashboard is ready when:

- [ ] Dashboard launches without errors
- [ ] All pages navigate correctly
- [ ] Core filters and controls work
- [ ] No console errors
- [ ] Layout appears correct (from screenshots)
- [ ] Any obvious broken features are fixed

**Next Step**: Dashboard is validated and ready to share with stakeholders or move to deployment.

## References

### MCP-Based Testing (Recommended)
**Note**: Playwright MCP is pre-configured with the vizro-e2e-flow plugin
- Playwright MCP: https://github.com/microsoft/playwright-mcp
