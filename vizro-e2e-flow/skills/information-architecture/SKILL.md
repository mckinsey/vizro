---
name: information-architecture
description: Stage 1 of Vizro dashboard development. USE FIRST when starting a new dashboard project or restructuring an existing one. Defines the overall information structure - what analytical questions each page answers, how insights are grouped across pages/tabs, and maps KPIs to appropriate views. Must be completed before moving to interaction design.
---

# Information Architecture for Vizro Dashboards

**Key Focus**: Define WHAT information will be presented, WHY it matters, and HOW it's organized across pages.

## OUTPUT PRESERVATION NOTICE

Your outputs from this stage are BINDING CONTRACTS for later stages:

- Page structure → MUST be implemented exactly in development
- KPI definitions → MUST appear in visual design
- Data groupings → MUST be preserved in layouts

## REQUIRED OUTPUT: spec/1_information_architecture.yaml

```yaml
# spec/1_information_architecture.yaml
dashboard:
  name: string
  purpose: string

pages:
  - name: string
    purpose: string
    kpis: list[string]

data_sources:
  - name: string
    type: string
```

Save this file BEFORE proceeding to the next stage.

## Process

1. **Understand business context**: What problems are we solving? Who are the users? What decisions do they make?
2. **Define analytical questions**: What questions does each page answer?
3. **Inventory data sources**: What data is available? What's the refresh frequency?
4. **Select KPIs**: Limit to 5-7 primary KPIs per dashboard
5. **Design page structure**: Organize by role, topic, process, or time
6. **Map information flow**: Define navigation paths (overview → detail → granular)

## Validation Checklist

Before proceeding to interaction-ux-design:

- [ ] Every page has a clear purpose
- [ ] KPIs are measurable and actionable
- [ ] Data sources are accessible
- [ ] No more than 3 levels of page hierarchy
- [ ] Critical questions answerable within 3 clicks

## Next Step

Proceed to **interaction-ux-design** skill.
