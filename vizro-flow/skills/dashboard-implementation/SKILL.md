---
name: dashboard-implementation
description: Practical guidance for building dashboards with Vizro. Use when implementing dashboards with Vizro framework, setting up Vizro MCP, or determining if Vizro is appropriate for a dashboard project. Includes decision trees, MCP setup, and Python quickstart references.
---

# Vizro Implementation

## Overview

Vizro is an open-source Python toolkit for building data visualization dashboards through configuration. This skill provides guidance for implementing dashboards with Vizro, including MCP setup and Python quickstart.

## Decision Tree: Should I Use Vizro?

```
Should I use Vizro for this dashboard?

├─ Is this a Python environment?
│  └─ NO → Do not use Vizro (Vizro requires Python)
│  └─ YES → Continue
│
├─ Do you need custom interactivity beyond filters/drill-downs?
│  └─ YES → Consider custom Dash/Plotly (Vizro may be limiting)
│  └─ NO → Continue
│
├─ Are you using standard Plotly Express chart types?
│  └─ NO → Consider custom implementation
│  └─ YES → Use Vizro

Decision: Use Vizro if Python + standard Plotly charts + rapid development needed
```

## What Vizro Offers

**Out-of-the-box**:
- Professional themes (vizro_dark, vizro_light) with colorblind-safe palette
- Grid and Flex layouts
- Auto-filters (page & container level, auto-detects categorical/numerical/temporal)
- All Plotly Express charts
- Multi-page navigation with automatic sidebar
- Actions (export, drill-down, cross-filtering)
- Component organization (Container, Tabs)
- Theme toggle (light/dark)

**Not for**: CRUD apps, chatbots, very complex custom UX workflows

## Implementation Path

### Option 1: Build with Vizro MCP (Recommended)

**Check for MCP first**: Look for `mcp__vizro__*` tools in available tools list.

**If MCP available**: Use MCP tools to generate, validate, and build Vizro dashboards with AI assistance.

**If MCP not available**: Install MCP following `references/mcp_setup.md`, then use MCP tools.

### Option 2: Build with Python (Manual)

**If MCP not desired**: Follow Python quickstart in `references/python_quickstart.md`.

## Bundled Resources

### References

**`mcp_setup.md`** - MCP installation instructions (uvx configuration), setup steps, and verification. Read when Vizro MCP is not available and needs to be installed.

**`python_quickstart.md`** - Python-based Vizro implementation guide with live documentation references, basic structure, and example configurations from official tutorials. Read when building Vizro dashboards manually without MCP.

**`dashboard_examples.md`** - Visual examples of well-designed Vizro dashboards with PNG screenshots showing landing pages, drill-down patterns, KPI layouts, and multi-page navigation. Read when exploring layout patterns or seeking visual design inspiration.

### Finding Information in References

```bash
# MCP setup
grep -i "installation\|uvx\|configuration" references/mcp_setup.md

# Python quickstart
grep -i "example\|configuration" references/python_quickstart.md
grep -i "layout\|filter\|component" references/python_quickstart.md

# Dashboard examples
grep -i "landing page\|drill-down\|pattern" references/dashboard_examples.md
```

## Quick Reference

**Always do**:
- Check for Vizro MCP first (faster development)
- Reference live documentation: https://vizro.readthedocs.io/en/latest/llms.txt
- Use default colorblind-safe palette (override only if needed)
- Test with accessibility tools
- Get user feedback early

**Live Documentation**:
- LLM-optimized: https://vizro.readthedocs.io/en/latest/llms.txt
- Main docs: https://vizro.readthedocs.io/en/stable/
- API Reference: https://vizro.readthedocs.io/en/stable/pages/API-reference/
