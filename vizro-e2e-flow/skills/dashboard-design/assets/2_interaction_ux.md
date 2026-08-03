# Interaction & UX

## Pages

### [Must match Step 1]
- Layout type: grid (or flex)
- Grid columns: 12
- Grid pattern:
  ```
  [[0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3]]
  ```
- Containers:
  - **[Container Name]** — has own filters: true / false
- Filter placement:
  - Page-level: [columns with selector types]
  - Container-level: [columns with selector types]

## Interactions

<!-- Omit this entire section if standard filters/parameters are sufficient. -->

### [Short name for the interaction]
- Type: cross-filter | cross-page-drill-through | cross-highlight | cross-parameter | export_data
- Pattern: [Pattern 1–6 name from wiring-vizro-actions]
- Trigger: [user action, e.g. "click bar in 'Pipeline by Region'"]
- Source: [Component name]
- Source value: [column name, or "x" / "y" for positional]
- Control id: [Filter/Parameter id]
- Control type: filter | parameter
- Control column: [column] (filters only)
- Targets: [list of component ids, or "all components in <container>"]
- Placement: page-level | container-level
- Visible: true / false (false for cross-highlight)
- Show in URL: true / false (required true for cross-page)

## Wireframes

### [Page name]

```
[ASCII wireframe for this page — one block per page and per tab view]
```

## Decisions
- **[What was decided]** — [Why this choice was made]
