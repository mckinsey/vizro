---
name: information-architecture
description: Stage 1 of Vizro dashboard development. USE FIRST when starting a new dashboard project or restructuring an existing one. Defines the overall information structure - what analytical questions each page answers, how insights are grouped across pages/tabs, and maps KPIs to appropriate views. Must be completed before moving to interaction design.
---

# Information Architecture (IA) for Vizro Dashboards

## Overview

Information Architecture (IA) is the foundational stage of dashboard development. It defines WHAT information will be presented, WHY it matters to users, and HOW it will be organized across pages and sections. This stage must be completed before any design or implementation work begins.

**Key Focus**: Define the overall information structure — what analytical questions each page answers, and how insights are grouped across pages or tabs.

## Process Workflow

### 1. Understand Business Context

**Key questions to answer**:

- What business problems are we solving with this dashboard?
- Who are the primary users and what decisions do they need to make?
- What is the frequency of use? (Real-time monitoring, daily operations, weekly review, monthly reporting)
- What actions should users take based on the insights?

**Deliverable**: Business context document with clear problem statement and user personas.

### 2. Define Analytical Questions

**Process**:

1. Interview stakeholders to identify key questions they need answered
1. Group related questions into themes
1. Prioritize questions by business impact
1. Map questions to specific user roles

**Example questions by dashboard type**:

**Executive Dashboard**:

- "Are we meeting our quarterly targets?"
- "Which regions/products are underperforming?"
- "What are the top 3 risks to address?"

**Operational Dashboard**:

- "What issues need immediate attention?"
- "Are systems performing within acceptable thresholds?"
- "Which processes have bottlenecks?"

**Analytical Dashboard**:

- "What patterns exist in customer behavior?"
- "How do different segments compare?"
- "What factors correlate with success metrics?"

**Deliverable**: Prioritized list of analytical questions mapped to user roles.

### 3. Inventory Data Sources

**Key activities**:

- Identify all required data sources (databases, APIs, files)
- Document data refresh frequency and latency
- Map data fields to analytical questions
- Identify data quality issues or gaps
- Determine aggregation levels needed

**Data source checklist**:

```
□ Data source access verified
□ Refresh frequency documented
□ Data quality assessed
□ Required transformations noted
□ Performance implications considered
```

**Deliverable**: Data source inventory with field mappings and quality assessment.

### 4. Select and Prioritize KPIs

**Principles**:

- Limit to 5-7 primary KPIs per dashboard
- Each KPI must drive a specific decision
- Balance leading and lagging indicators
- Ensure KPIs align with business objectives

**KPI prioritization framework**:

**Tier 1 (Primary KPIs)**:

- Displayed prominently on main page
- Maximum 3-5 metrics
- Updated in real-time or near real-time
- Critical for immediate decisions

**Tier 2 (Supporting Metrics)**:

- Provide context for primary KPIs
- 5-10 metrics maximum
- Can be on secondary pages or expandable sections

**Tier 3 (Detailed Metrics)**:

- Available through drill-downs
- For deep analysis and investigation
- Can be numerous but well-organized

**Deliverable**: KPI hierarchy with clear definitions and business rules.

### 5. Design Page Structure

**Page organization patterns**:

**Pattern A: Role-Based Structure**

```
├── Executive Overview (C-suite view)
├── Manager Dashboard (departmental view)
└── Analyst Workspace (detailed view)
```

**Pattern B: Topic-Based Structure**

```
├── Sales Performance
├── Customer Analytics
├── Operations Metrics
└── Financial Summary
```

**Pattern C: Process-Based Structure**

```
├── Monitor (current state)
├── Analyze (trends and patterns)
├── Predict (forecasts)
└── Act (recommendations)
```

**Pattern D: Time-Based Structure**

```
├── Real-Time (live metrics)
├── Daily Snapshot
├── Weekly Trends
└── Monthly/Quarterly Review
```

**Deliverable**: Page hierarchy/sitemap with clear purpose for each page.

### 6. Map Information Flow

**Define navigation paths**:

- Overview → Detail → Granular (progressive disclosure)
- Cross-page relationships and dependencies
- Filter inheritance between pages
- Drill-down and drill-through paths

**Example information flow**:

```
Landing Page (KPI Summary)
    ↓
Category Pages (Sales | Operations | Finance)
    ↓
Detail Pages (by Region | Product | Time Period)
    ↓
Investigation Views (Root Cause Analysis)
```

**Deliverable**: Information flow diagram showing navigation and relationships.

## Deliverables Checklist

### Required Outputs

1. **Page Hierarchy/Sitemap**

    - Clear page structure with 2-4 levels maximum
    - Purpose statement for each page
    - Target audience per page

1. **Analytical Questions List**

    - Grouped by page/section
    - Prioritized by importance
    - Mapped to user roles

1. **KPI Inventory**

    - Primary, secondary, and tertiary metrics
    - Business definitions and calculations
    - Update frequency and data sources

1. **Data Source Map**

    - All required data sources
    - Field-level mappings
    - Refresh schedules and dependencies

1. **User Journey Maps**

    - Key workflows for each user type
    - Decision points and actions
    - Information needs at each step

## Common Patterns

### Executive Dashboard IA

```
Page 1: Executive Summary
- Revenue vs Target (KPI)
- Profit Margin (KPI)
- Customer Satisfaction (KPI)
- Top Issues Alert

Page 2: Performance Breakdown
- By Region (Tab)
- By Product (Tab)
- By Channel (Tab)

Page 3: Trends & Forecasts
- Historical Performance
- Predictive Analytics
- Scenario Planning
```

### Operational Dashboard IA

```
Page 1: System Status
- Live Status Indicators
- Alert Summary
- Performance Metrics

Page 2: Issue Management
- Active Incidents
- Resolution Progress
- Impact Analysis

Page 3: Performance Analytics
- Throughput Metrics
- Error Analysis
- Capacity Planning
```

### Customer Analytics IA

```
Page 1: Customer Overview
- Total Customers
- Acquisition/Churn
- Lifetime Value
- Segmentation

Page 2: Behavior Analysis
- Journey Analytics
- Product Usage
- Engagement Metrics

Page 3: Revenue Impact
- Revenue by Segment
- Upsell Opportunities
- Churn Risk Analysis
```

## Validation Checklist

Before proceeding to Interaction/UX Design, ensure:

- [ ] All key stakeholders have reviewed and approved the IA
- [ ] Every page has a clear purpose and target audience
- [ ] KPIs are measurable and actionable
- [ ] Data sources are accessible and reliable
- [ ] Information hierarchy supports user workflows
- [ ] Navigation paths are logical and intuitive
- [ ] No more than 3 levels of depth in page hierarchy
- [ ] Critical questions can be answered within 3 clicks

## Next Steps

Once Information Architecture is complete and validated:

1. Proceed to **interaction-ux-design** skill to design navigation and layout
1. Document any constraints or requirements for the UX phase
1. Share IA deliverables with design and development teams

## Tips for Success

1. **Start with user needs, not available data** - Design for decisions, then find/create data
1. **Less is more** - Better to have 5 useful metrics than 20 confusing ones
1. **Test with real users** - Validate IA with actual dashboard users early
1. **Plan for growth** - Design IA to accommodate future additions
1. **Document everything** - Clear documentation speeds up later stages
