# Implementation Guide

Deep guidance for Phase 4: Building the dashboard with Vizro MCP tools.

## Contents

- MCP Workflow (understand MCP server, get schemas, validate config, run dashboard)
- Components Reference (Graph, AgGrid, Figure, Card, Container, Tabs)
- Controls Reference (Filter, Parameter)
- Layout Reference (Grid, Flex, Nested)
- Custom Charts (when and how to use @capture decorator)
- Multi-Page Dashboard
- Running the Dashboard
- Common Patterns (Overview + Detail pages)
- Number Formatting & Typography
- Grid Configuration Rules
- Documentation Links

## MCP Workflow

### Step 1: Understand how the MCP server works

```
Use: vizro-mcp:get_vizro_chart_or_dashboard_plan(user_plan="dashboard", user_host="ide")
```

You can either load data again, or if well enough understood, you can skip this step and proceed to the next step.

### Step 2: Get Model Schemas

Schemas define valid properties, required fields, and available options for each component. Fetch schemas for components you plan to use.

```
Use: vizro-mcp:get_model_json_schema(model_name="Dashboard")
Use: vizro-mcp:get_model_json_schema(model_name="Page")
```

### Step 3: Build Dashboard Config

Create JSON config respecting Phase 1-3 decisions:

```json
{
  "pages": [
    {
      "title": "Overview",
      "components": [
        {
          "type": "graph",
          "figure": {
            "_target_": "bar",
            "data_frame": "sales",
            "x": "category",
            "y": "revenue"
          },
          "title": "Revenue by Category"
        }
      ],
      "controls": [
        {
          "type": "filter",
          "column": "region"
        }
      ]
    }
  ]
}
```

### Step 4: Validate and Get Code

```
Use: vizro-mcp:validate_dashboard_config(dashboard_config={...}, data_infos=[...], custom_charts=[])
```

**CRITICAL**: Call this tool after each iteration to ensure the solution is still valid.

Returns Python code.

### Step 5: Run the Dashboard

Add the required dependencies as inline dependencies in the `app.py` file, e.g.:

```python
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "vizro",
#     "pandas",
#     <anything else important>
# ]
# ///

# The app output from the validation tool!
```

Then execute the script with the following command:

```bash
uv run python app.py
```

## Components Reference

**IMPORTANT**: Always fetch component schemas using `vizro-mcp:get_model_json_schema(model_name="ComponentName")` to see all available properties, required fields, and valid options. The examples below show common patterns, but schemas are the source of truth.

### Graph (Charts)

```json
{
  "type": "graph",
  "id": "my_chart",
  "figure": {
    "_target_": "bar",
    "data_frame": "sales",
    "x": "category",
    "y": "value",
    "color": "segment"
  },
  "title": "Chart Title",
  "header": "Additional context",
  "footer": "SOURCE: **Data source**"
}
```

**Notes**:

- `id` is optional, but needed for Parameter targets
- `title` goes here, NOT in plotly figure
- `header` and `footer` are optional
- `footer` supports markdown

### AgGrid (Tables)

```json
{
  "type": "ag_grid",
  "figure": {
    "_target_": "dash_ag_grid",
    "data_frame": "sales"
  },
  "title": "Data Table"
}
```

### Figure (KPIs)

**Simple KPI**:

```json
{
  "type": "figure",
  "figure": {
    "_target_": "kpi_card",
    "data_frame": "sales",
    "value_column": "revenue",
    "title": "Total Revenue",
    "value_format": "${value:,.0f}",
    "agg_func": "sum",
    "icon": "payments"
  }
}
```

**KPI with reference comparison**:

```json
{
  "type": "figure",
  "figure": {
    "_target_": "kpi_card_reference",
    "data_frame": "sales",
    "value_column": "revenue",
    "reference_column": "previous_revenue",
    "title": "Revenue vs Last Month",
    "value_format": "${value:,.0f}",
    "reference_format": "{delta:+.1f}%",
    "reverse_color": true
  }
}
```

**Note**: Use `reverse_color: true` when lower is better (costs, errors). NEVER add a `kpi_card` or `kpi_card_reference` as a custom chart, only use as shown above.

### Other Components

**Card**: Use for text content, markdown, or HTML. Supports markdown formatting in `text` field.

**Container**: Use to group related components with shared filters/parameters. Controls are scoped to the container. Supports `variant` ("outlined", "filled", "plain") and custom layouts.

**Tabs**: Use to organize multiple views/pages within a single page. Each tab is a Container with its own components and controls.

## Controls Reference

**IMPORTANT**: Always fetch control schemas using `vizro-mcp:get_model_json_schema(model_name="Filter")` or `vizro-mcp:get_model_json_schema(model_name="Parameter")` to see all available properties and options.

### Filter

Filters filter data across multiple visualizations. Place at page-level (left sidebar) if needed across multiple components, or container-level if scoped to a specific container.

**IMPORTANT**: Choose the appropriate selector - don't default to Dropdown for everything:

- **RadioItems**: 2-4 mutually exclusive options (e.g., Region: North/South/East/West)
- **Checklist**: Multi-select or boolean values (e.g., Status: Active/Inactive/Pending)
- **Dropdown**: 5+ options (e.g., Product Category with many categories)
- **RangeSlider**: Numeric ranges (e.g., Price: $0-$1000)
- **Slider**: Single numeric value (e.g., Year: 2020-2025)
- **DatePicker**: Date selection (use `range: true` for date ranges)

### Parameter

Parameters modify chart arguments (not filter data). Use when you want to change what's displayed (e.g., switch x-axis column, change metric) rather than filter the underlying dataset. Requires `targets` array pointing to component IDs and their properties (e.g., `["chart_id.x"]`).

## Layout Reference

### Grid Configuration

**Grid Rules**:

- Each sub-list is a row
- Integers are component indices (0-based, consecutive)
- Use `-1` for empty cells
- Components span rectangular areas by repeating their index
- Always use `row_min_height="140px"`
- **12 columns recommended** (not enforced) - examples below use 12 columns

```json
{
  "type": "page",
  "title": "Dashboard",
  "layout": {
    "type": "grid",
    "grid": [
      [
        0,
        0,
        0,
        0,
        0,
        0,
        1,
        1,
        1,
        1,
        1,
        1
      ],
      [
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2
      ]
    ],
    "row_min_height": "140px"
  },
  "components": [
    {
      "type": "graph",
      "figure": {
        "_target_": "bar",
        "data_frame": "sales",
        "x": "category",
        "y": "revenue"
      }
    },
    {
      "type": "graph",
      "figure": {
        "_target_": "line",
        "data_frame": "sales",
        "x": "date",
        "y": "revenue"
      }
    },
    {
      "type": "ag_grid",
      "figure": {
        "_target_": "dash_ag_grid",
        "data_frame": "sales"
      }
    }
  ]
}
```

### Standard Grid Pattern

```json
{
  "type": "page",
  "title": "Dashboard",
  "layout": {
    "type": "grid",
    "grid": [
      [
        0,
        0,
        0,
        1,
        1,
        1,
        2,
        2,
        2,
        3,
        3,
        3
      ],
      [
        4,
        4,
        4,
        4,
        4,
        4,
        5,
        5,
        5,
        5,
        5,
        5
      ],
      [
        4,
        4,
        4,
        4,
        4,
        4,
        5,
        5,
        5,
        5,
        5,
        5
      ],
      [
        4,
        4,
        4,
        4,
        4,
        4,
        5,
        5,
        5,
        5,
        5,
        5
      ],
      [
        6,
        6,
        6,
        6,
        6,
        6,
        6,
        6,
        6,
        6,
        6,
        6
      ],
      [
        6,
        6,
        6,
        6,
        6,
        6,
        6,
        6,
        6,
        6,
        6,
        6
      ]
    ],
    "row_min_height": "140px"
  },
  "components": [
    {
      "type": "figure",
      "figure": {
        "_target_": "kpi_card",
        "data_frame": "sales",
        "value_column": "revenue"
      }
    },
    {
      "type": "figure",
      "figure": {
        "_target_": "kpi_card",
        "data_frame": "sales",
        "value_column": "orders"
      }
    },
    {
      "type": "figure",
      "figure": {
        "_target_": "kpi_card",
        "data_frame": "sales",
        "value_column": "profit"
      }
    },
    {
      "type": "figure",
      "figure": {
        "_target_": "kpi_card",
        "data_frame": "sales",
        "value_column": "customers"
      }
    },
    {
      "type": "graph",
      "figure": {
        "_target_": "bar",
        "data_frame": "sales",
        "x": "category",
        "y": "revenue"
      }
    },
    {
      "type": "graph",
      "figure": {
        "_target_": "line",
        "data_frame": "sales",
        "x": "date",
        "y": "revenue"
      }
    },
    {
      "type": "ag_grid",
      "figure": {
        "_target_": "dash_ag_grid",
        "data_frame": "sales"
      }
    }
  ]
}
```

### Flexible Width Distributions

12 columns allows uneven widths since 12 has many divisors (1, 2, 3, 4, 6, 12):

```python
# Equal widths: 3 charts × 4 cols
[[0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2]]

# Emphasis on primary chart: 6 + 3 + 3
[[0, 0, 0, 0, 0, 0, 1, 1, 1, 2, 2, 2]]

# Two-thirds + one-third: 8 + 4
[[0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1]]

# Half + half: 6 + 6
[[0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1]]
```

### Row Height Control

**Always use 140px row height**:

```json
{
  "layout": {
    "type": "grid",
    "grid": [...],
    "row_min_height": "140px"
  }
}
```

**Component height = row_min_height × rows_spanned**:

- KPI cards: 1 row = 140px (optimal)
- Charts: 3 rows = 420px (minimum for proper rendering)
- Tables: 4+ rows = 560px+ (adjust based on content)

### Creating Taller Components

Repeat rows in the grid array to make components taller:

```json
{
  "layout": {
    "type": "grid",
    "grid": [
      [
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0
      ],
      [
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1
      ],
      [
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1
      ],
      [
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1
      ],
      [
        2,
        2,
        2,
        2,
        2,
        2,
        3,
        3,
        3,
        3,
        3,
        3
      ],
      [
        2,
        2,
        2,
        2,
        2,
        2,
        3,
        3,
        3,
        3,
        3,
        3
      ],
      [
        2,
        2,
        2,
        2,
        2,
        2,
        3,
        3,
        3,
        3,
        3,
        3
      ],
      [
        2,
        2,
        2,
        2,
        2,
        2,
        3,
        3,
        3,
        3,
        3,
        3
      ]
    ],
    "row_min_height": "140px"
  }
}
```

### Flex Layout

```json
{
  "type": "page",
  "title": "Simple Page",
  "layout": {
    "type": "flex"
  },
  "components": [
    {
      "type": "graph",
      "figure": {
        "_target_": "bar",
        "data_frame": "sales",
        "x": "category",
        "y": "revenue"
      }
    },
    {
      "type": "graph",
      "figure": {
        "_target_": "line",
        "data_frame": "sales",
        "x": "date",
        "y": "revenue"
      }
    },
    {
      "type": "ag_grid",
      "figure": {
        "_target_": "dash_ag_grid",
        "data_frame": "sales"
      }
    }
  ]
}
```

### Container with Grid

```json
{
  "type": "container",
  "title": "Regional Analysis",
  "layout": {
    "type": "grid",
    "grid": [
      [
        0,
        0,
        0,
        0,
        0,
        0,
        1,
        1,
        1,
        1,
        1,
        1
      ],
      [
        0,
        0,
        0,
        0,
        0,
        0,
        1,
        1,
        1,
        1,
        1,
        1
      ],
      [
        0,
        0,
        0,
        0,
        0,
        0,
        1,
        1,
        1,
        1,
        1,
        1
      ]
    ],
    "row_min_height": "140px"
  },
  "components": [
    {
      "type": "graph",
      "figure": {
        "_target_": "bar",
        "data_frame": "sales",
        "x": "region",
        "y": "sales"
      }
    },
    {
      "type": "graph",
      "figure": {
        "_target_": "pie",
        "data_frame": "sales",
        "values": "sales",
        "names": "region"
      }
    }
  ],
  "controls": [
    {
      "type": "filter",
      "column": "quarter"
    }
  ],
  "variant": "outlined"
}
```

### Nested Layouts

```json
{
  "type": "page",
  "title": "Mixed Layout",
  "layout": {
    "type": "flex"
  },
  "components": [
    {
      "type": "graph",
      "figure": {
        "_target_": "line",
        "data_frame": "sales",
        "x": "date",
        "y": "revenue"
      }
    },
    {
      "type": "container",
      "title": "Details",
      "layout": {
        "type": "grid",
        "grid": [
          [
            0,
            0,
            0,
            0,
            1,
            1,
            1,
            1,
            2,
            2,
            2,
            2
          ]
        ],
        "row_min_height": "140px"
      },
      "components": [
        {
          "type": "graph",
          "figure": {
            "_target_": "bar",
            "data_frame": "sales",
            "x": "category",
            "y": "revenue"
          }
        },
        {
          "type": "graph",
          "figure": {
            "_target_": "scatter",
            "data_frame": "sales",
            "x": "revenue",
            "y": "profit"
          }
        },
        {
          "type": "graph",
          "figure": {
            "_target_": "pie",
            "data_frame": "sales",
            "values": "revenue",
            "names": "category"
          }
        }
      ]
    }
  ]
}
```

## Custom Charts

Use custom charts when you need:

- Data manipulation before visualization
- Build chart types not available in `plotly.express` (waterfall, bullet, etc.)
- Use plotly update calls: `update_layout()`, `update_xaxes()`, `update_traces()`
- Add horizontal/vertical reference lines showing targets or benchmarks
- Create multi-layered visualizations combining different trace types
- Apply conditional formatting based on data values
- **NEVER** return `kpi_card` or `kpi_card_reference` as a custom chart, use the built-in `kpi_card` and `kpi_card_reference` in `Figure` model instead
- The function MUST return a `plotly.graph_objects.Figure` object

### Example: Bar Chart with Target Line

**Python function** (pass to `validate_dashboard_config` in the `custom_charts` parameter):

```python
from vizro.models.types import capture
import vizro.plotly.express as px


@capture("graph")
def bar_with_target(data_frame, x, y, target=None):
    """Bar chart with optional horizontal target line."""
    fig = px.bar(data_frame=data_frame, x=x, y=y)
    if target is not None:
        fig.add_hline(
            y=target,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Target: {target}",
        )
    return fig
```

**JSON usage**:

```json
{
  "type": "graph",
  "id": "sales_chart",
  "figure": {
    "_target_": "bar_with_target",
    "data_frame": "sales",
    "x": "month",
    "y": "revenue",
    "target": 100000
  },
  "title": "Monthly Revenue vs Target"
}
```

**With Parameter control**:

```json
{
  "type": "parameter",
  "targets": [
    "sales_chart.target"
  ],
  "selector": {
    "type": "slider",
    "min": 50000,
    "max": 200000,
    "value": 100000,
    "title": "Target"
  }
}
```

### Custom Chart Rules

1. Function must accept `data_frame` as first argument
1. Must return `plotly.graph_objects.Figure`
1. Chart titles go in JSON `title` field, not in the function
1. Let Vizro handle colors unless semantic coloring needed
1. Reference custom charts in JSON using `"_target_": "function_name"`

## Running the Dashboard

Add the required dependencies as inline dependencies in the `app.py` file (see Step 5 in MCP Workflow above), then run:

```bash
uv run app.py
```

Access at `http://localhost:8050`

## Common Patterns

### Dashboard with Overview and Detail Pages

**Overview page** - KPIs and summary charts:

```json
{
  "type": "page",
  "title": "Overview",
  "layout": {
    "type": "grid",
    "grid": [
      [
        0,
        0,
        0,
        0,
        0,
        0,
        1,
        1,
        1,
        1,
        1,
        1
      ],
      [
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2
      ],
      [
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2
      ],
      [
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2
      ]
    ],
    "row_min_height": "140px"
  },
  "components": [
    {
      "type": "figure",
      "figure": {
        "_target_": "kpi_card",
        "data_frame": "sales",
        "value_column": "revenue",
        "title": "Revenue",
        "value_format": "${value:,.0f}"
      }
    },
    {
      "type": "figure",
      "figure": {
        "_target_": "kpi_card",
        "data_frame": "sales",
        "value_column": "orders",
        "title": "Orders",
        "value_format": "{value:,}"
      }
    },
    {
      "type": "graph",
      "figure": {
        "_target_": "line",
        "data_frame": "sales",
        "x": "date",
        "y": "revenue"
      },
      "title": "Trend"
    }
  ],
  "controls": [
    {
      "type": "filter",
      "column": "region"
    }
  ]
}
```

**Detail page** - tables and drill-downs:

```json
{
  "type": "page",
  "title": "Details",
  "layout": {
    "type": "flex"
  },
  "components": [
    {
      "type": "ag_grid",
      "figure": {
        "_target_": "dash_ag_grid",
        "data_frame": "sales"
      },
      "title": "All Data"
    },
    {
      "type": "button",
      "text": "Export",
      "actions": [
        {
          "_target_": "export_data"
        }
      ]
    }
  ],
  "controls": [
    {
      "type": "filter",
      "column": "region"
    },
    {
      "type": "filter",
      "column": "product"
    }
  ]
}
```

**Complete dashboard**:

```json
{
  "pages": [
    {
      "type": "page",
      "title": "Overview",
      ...
    },
    {
      "type": "page",
      "title": "Details",
      ...
    }
  ]
}
```

## Number Formatting & Typography

### Number Formatting Rules

| Type          | Format                         | Example     |
| ------------- | ------------------------------ | ----------- |
| Large numbers | K, M, B notation               | 1.2M, 45.3K |
| Currency      | Symbol before, with separators | $1,234,567  |
| Percentages   | 1 decimal place                | 45.3%       |
| Decimals      | 0-2 places maximum             | 12.34       |
| Thousands     | Always use separators          | 1,234,567   |

**Format Strings for KPI Cards**:

```python
# Currency
value_format = "${value:,.0f}"  # $1,234,567
value_format = "${value:,.2f}"  # $1,234,567.89

# Percentages
value_format = "{value:.1f}%"  # 45.3%

# Large numbers (manual K/M/B)
value_format = "{value/1000000:.1f}M"  # 1.2M
```

### Label Best Practices

- Short and descriptive (2-5 words)
- Sentence case (not Title Case or UPPERCASE)
- No periods at end of labels
- Truncate with ellipsis if necessary (max 20 chars)

## Grid Configuration Rules

- Indices must be consecutive integers starting from 0
- Each sub-list is a row, each element is a column
- Use `*[[...]] * n` to repeat rows (makes components taller)
- Components must span rectangular areas
- Actual height = `row_min_height × rows_spanned`

## Documentation Links

- **LLM-optimized docs**: https://vizro.readthedocs.io/en/latest/llms.txt
- **User Guides**: https://vizro.readthedocs.io/en/stable/pages/user-guides/
- **API Reference**: https://vizro.readthedocs.io/en/stable/pages/API-reference/vizro/
- **Vizro MCP**: https://vizro.readthedocs.io/projects/vizro-mcp/
- **Playwright MCP**: https://github.com/microsoft/playwright-mcp
- **Claude Code MCP Guide**: https://docs.anthropic.com/en/docs/claude-code/tutorials/mcp-tutorial
