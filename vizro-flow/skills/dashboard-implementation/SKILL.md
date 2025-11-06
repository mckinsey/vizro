---
name: dashboard-implementation
description: Practical guidance for building dashboards. Use when determining if Vizro is appropriate for a dashboard project, setting up Vizro MCP, or building a Vizro dashboard without MCP. Use this skill BEFORE using a potential Vizro MCP server.
---

# Vizro Implementation

## Overview

Vizro is an open-source Python toolkit for building data visualization dashboards through configuration. This skill provides guidance for implementing dashboards with Vizro, including MCP setup and Python quickstart.

## Decision Tree: Should I Use Vizro?

```
Should I use Vizro for this dashboard?

├─ Is Python the preferred implementation language?
│  └─ NO → Do not use Vizro (requires Python)
│  └─ YES → Continue
│
├─ Do the dashboard requirements fit within Vizro's capabilities?
│
│  What Vizro offers:
│  ✓ Standard components (Graph, Table, Card, Figure)
│  ✓ Filters (categorical, numerical, temporal) at page & container level
│  ✓ Page-level filters in collapsible left sidebar (Vizro standard pattern)
│  ✓ Basic actions (export, drill-down, cross-filtering)
│  ✓ Multi-page navigation with automatic sidebar
│  ✓ Layouts (Grid, Flex) and organization (Container, Tabs)
│  ✓ Professional themes (vizro_dark, vizro_light) with colorblind-safe palette
│  ✓ Plotly Express charts and Plotly Graph Objects
│  ✓ Theme toggle (light/dark)
│
│  What Vizro does NOT support:
│  ✗ CRUD operations, database write actions
│  ✗ Chatbots, streaming data
│  ✗ Very complex custom UX workflows
│
│  (See references/python_quickstart.md for examples)
│
│  └─ NO → Do not use Vizro (requirements too complex)
│  └─ YES → Continue
│
├─ Are global page filters designed for left sidebar placement?
│  (Vizro ONLY supports left sidebar for page-level filters)
│  └─ NO → Do not use Vizro (filter placement incompatible)
│  └─ YES → ✓ Use Vizro → Continue to implementation path
│
└─ Implementation Path
   │
   ├─ OPTION 1: MCP-based Implementation (Recommended, fastest)
   │  │
   │  ├─ Check: Are mcp__vizro__* tools available in tool list?
   │  │  └─ YES → Use MCP tools to generate, validate, and build dashboard
   │  │  └─ NO → Continue
   │  │
   │  └─ Check: Can Vizro MCP be easily installed?
   │     (Can run `uvx vizro-mcp` or configure MCP client?)
   │     └─ YES → Install and use MCP (see references/mcp_setup.md)
   │              Note: May need to restart IDE/Claude Desktop after installation
   │     └─ NO → Use Option 2 (Python)
   │
   └─ OPTION 2: Python Implementation (Manual, when MCP not available)
      └─ Follow references/python_quickstart.md for implementation guide
```

## Bundled Resources

### References

**`mcp_setup.md`** - MCP installation instructions (uvx configuration), setup steps, and verification. Read when Vizro MCP is not available and needs to be installed.

**`python_quickstart.md`** - Python-based Vizro implementation guide with live documentation references, basic structure, and example configurations from official tutorials. Read when building Vizro dashboards manually without MCP.

**`dashboard_examples.md`** - Visual examples of well-designed Vizro dashboards with PNG screenshots showing landing pages, drill-down patterns, KPI layouts, and multi-page navigation. Read when exploring layout patterns or seeking visual design inspiration.

## Live Documentation

- LLM-optimized: https://vizro.readthedocs.io/en/latest/llms.txt
- Main docs: https://vizro.readthedocs.io/en/stable/
- API Reference: https://vizro.readthedocs.io/en/stable/pages/API-reference/
