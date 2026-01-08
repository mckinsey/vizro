# Information Architecture Guide

Deep guidance for Phase 1: Understanding Requirements.

## Contents

- The Foundation of Effective Dashboards
- Requirements Gathering Framework (business context, analytical questions, data sources, KPIs, page structure)
- Common Mistakes in Information Architecture
- Validation Framework (checklist)
- Example: E-Commerce Dashboard IA

## The Foundation of Effective Dashboards

Information architecture determines dashboard success more than visual design. A beautiful dashboard with wrong metrics fails; an ugly dashboard with right metrics succeeds.

## Requirements Gathering Framework

### 1. Understand the Business Context

**Questions to ask**:

- What business process does this dashboard support?
- What decisions will users make based on this data?
- What happens if these decisions are wrong or delayed?
- Who are the primary users? Secondary users?

**User Archetypes**:

| Type | Needs | Dashboard Approach |
|------|-------|-------------------|
| Executive | High-level trends, exceptions | KPIs, sparklines, alerts |
| Manager | Team performance, comparisons | Comparisons, drill-downs |
| Analyst | Deep exploration, raw data | Filters, tables, exports |
| Operator | Real-time status, actions | Live metrics, action buttons |

### 2. Define Analytical Questions

Every page should answer specific questions. Document them explicitly:

**Good questions** (actionable):
- "Which regions are underperforming this quarter?"
- "Are we on track to meet the monthly target?"
- "Which products should we restock?"

**Bad questions** (too vague):
- "What's happening with sales?"
- "Show me everything about customers"
- "Give me all the data"

### 3. Inventory Data Sources

| Source | Type | Refresh | Owner | Quality |
|--------|------|---------|-------|---------|
| sales_db | PostgreSQL | Daily | Data Team | High |
| marketing.csv | File | Weekly | Marketing | Medium |
| api/metrics | REST API | Real-time | Engineering | High |

**Data quality considerations**:

- Missing values: How to handle?
- Data freshness: Is delayed data acceptable?
- Access permissions: Who can see what?

### 4. Select KPIs

**The 5-7 Rule**: No more than 5-7 primary KPIs per page.

**KPI Selection Criteria**:

- **Measurable**: Can be quantified precisely
- **Actionable**: User can do something about it
- **Timely**: Available when needed
- **Relevant**: Directly tied to business goals

**KPI Hierarchy**:

```
Primary KPIs (3-5): Featured prominently, answer main questions
├── Supporting metrics: Provide context for primary KPIs
└── Detail metrics: Available on drill-down
```

**Example: Sales Dashboard**

```
Primary KPIs:
- Total Revenue (vs target)
- Conversion Rate
- Average Order Value
- Customer Acquisition Cost

Supporting:
- Revenue by Region
- Top Products
- Sales Pipeline

Detail (drill-down):
- Individual transactions
- Customer details
```

### 5. Design Page Structure

**Organizational Patterns**:

| Pattern | Best For | Example |
|---------|----------|---------|
| By Role | Different user needs | Executive / Manager / Analyst views |
| By Topic | Domain areas | Sales / Marketing / Operations |
| By Process | Workflow stages | Lead → Opportunity → Close |
| By Time | Temporal analysis | Daily / Weekly / Monthly |

**Information Flow**:

```
Level 1: Overview (3-7 primary KPIs, high-level trends)
├── High-level KPIs
├── Trend summaries
└── Exception alerts

Level 2: Analysis (supporting metrics, comparative data via tabs/sections)
├── Comparisons
├── Breakdowns
└── Filters

Level 3: Detail (individual records, deep analysis via drill-downs)
├── Individual transactions
├── Raw data tables
└── Export capability
```

**Drill-Down Patterns**:

- Click on chart → Filtered detail view
- Hover → Tooltip with exact values
- Click on metric → Time series or breakdown
- "Show more" → Expanded table or list

**Data Density Management**:

| User Type | Data Density | Approach |
|-----------|--------------|----------|
| Executive | Low | KPIs, sparklines, exceptions only |
| Manager | Medium | Comparisons, summaries, key filters |
| Analyst | High | Full exploration, raw data, exports |
| Operator | Medium-High | Real-time metrics, action buttons |

**Page Limit Guidelines**:

- 1-3 pages: Simple operational dashboard
- 4-7 pages: Comprehensive business dashboard
- 8+ pages: Consider splitting into multiple dashboards

## Common Mistakes in Information Architecture

### 1. Everything on One Page

**Problem**: 20+ metrics crammed together
**Solution**: Prioritize ruthlessly, use drill-downs

### 2. No Clear Hierarchy

**Problem**: All metrics appear equally important
**Solution**: Define primary vs supporting vs detail metrics

### 3. Data-Driven Instead of Question-Driven

**Problem**: "We have this data, let's show it"
**Solution**: Start with questions users need answered

### 4. Ignoring User Context

**Problem**: Same dashboard for executives and analysts
**Solution**: Role-specific views or pages

### 5. Missing Comparisons

**Problem**: Numbers without context (Revenue: $1.2M... is that good?)
**Solution**: Always include comparison (vs target, vs last period, vs benchmark)

## Validation Framework

Before moving to Phase 2, verify:

```
Information Architecture Checklist:
- [ ] Dashboard purpose is clear in one sentence
- [ ] Target users are identified
- [ ] Each page answers specific questions (documented)
- [ ] Primary KPIs are limited (5-7 per page)
- [ ] Data sources are accessible and understood
- [ ] Information hierarchy is defined (primary/supporting/detail)
- [ ] User has explicitly confirmed the structure
```

## Example: E-Commerce Dashboard IA

```yaml
dashboard:
  name: E-Commerce Performance
  purpose: Monitor sales performance and identify growth opportunities
  users: [Sales Manager, Marketing Director]

pages:
  - name: Executive Summary
    purpose: "Are we hitting targets? What needs attention?"
    kpis:
      - Total Revenue (vs target)
      - Orders This Month
      - Conversion Rate
      - Customer Acquisition Cost
    supporting:
      - Revenue trend (sparkline)
      - Top performing category

  - name: Sales Analysis
    purpose: "Where are sales coming from? What's trending?"
    kpis:
      - Revenue by Region
      - Revenue by Category
      - Sales Pipeline Value
    interactions:
      - Filter by date range
      - Filter by region
      - Drill to product detail

  - name: Customer Insights
    purpose: "Who are our customers? How do we retain them?"
    kpis:
      - New vs Returning Customers
      - Customer Lifetime Value
      - Churn Rate
    interactions:
      - Filter by segment
      - Drill to customer detail

data_sources:
  - name: orders_db
    type: PostgreSQL
    refresh: Hourly
    tables: [orders, order_items, customers]

  - name: marketing_metrics
    type: API
    refresh: Daily
    metrics: [ad_spend, impressions, clicks]
```
