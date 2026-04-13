# Data Management Guide

Deep guidance for handling data in Vizro dashboards.

## Contents

**Quick Start** (most dashboards need only this):

- Data Source Types (static vs dynamic)
- Choosing Your Approach (decision tree)
- Static Data (simple loading patterns)
- Dynamic Data (basic registration, caching)
- Best Practices
- Comparison Summary

**Advanced Patterns** (databases, APIs, parametrized loading):

- Parametrized Data Loading
- Common Data Patterns (databases, APIs, multi-source)
- Dynamic Filters (data-driven filter options)
- Documentation Links

---

# Quick Start

## Data Source Types

Vizro supports two types of data sources:

| Type    | Python Type                  | Refresh   | Use Case                      |
| ------- | ---------------------------- | --------- | ----------------------------- |
| Static  | pandas DataFrame             | Never     | Simple dashboards, fixed data |
| Dynamic | Function returning DataFrame | On demand | Live data, caching needed     |

## Choosing Your Approach

```
Do you need data to refresh while dashboard is running?
├── No → Use static data (DataFrame directly)
└── Yes → Use dynamic data (function + data_manager)
```

## Static Data

### Direct Supply (Simplest)

```python
import pandas as pd
import vizro.models as vm
from vizro import Vizro
import vizro.plotly.express as px

# Load data once at startup
df = pd.read_csv("sales.csv")

page = vm.Page(
    title="Sales Dashboard",
    components=[
        vm.Graph(figure=px.scatter(df, x="units", y="revenue")),
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
```

**Pros**: Simplest approach **Cons**: Data never refreshes

### Named Reference

Use when referencing data by name:

```python
from vizro.managers import data_manager
import pandas as pd

# Add to data manager with a name
data_manager["sales"] = pd.read_csv("sales.csv")

# Reference by name (string, not DataFrame)
vm.Graph(figure=px.scatter("sales", x="units", y="revenue"))
```

## Dynamic Data

Dynamic data uses a **function** that returns a DataFrame. This function can be re-executed to refresh data.

### Basic Dynamic Data

```python
from vizro.managers import data_manager
import pandas as pd


def load_sales():
    """This function runs on each page refresh (without caching)."""
    return pd.read_csv("sales.csv")


# Add function (NOT function call!)
data_manager["sales"] = load_sales  # Correct: function reference
# data_manager["sales"] = load_sales()  # Wrong: this is static!

# Reference by name
vm.Graph(figure=px.scatter("sales", x="units", y="revenue"))
```

### With Caching

Without caching, the function runs on every page refresh. Add caching to improve performance:

**Development (Simple Cache)**:

```python
from flask_caching import Cache
from vizro.managers import data_manager

data_manager.cache = Cache(config={"CACHE_TYPE": "SimpleCache"})


def load_sales():
    return pd.read_csv("sales.csv")


data_manager["sales"] = load_sales
```

**Production (File System Cache)**:

```python
data_manager.cache = Cache(
    config={
        "CACHE_TYPE": "FileSystemCache",
        "CACHE_DIR": "cache",
    }
)
```

**Production (Redis Cache)**:

```python
data_manager.cache = Cache(
    config={
        "CACHE_TYPE": "RedisCache",
        "CACHE_REDIS_HOST": "localhost",
        "CACHE_REDIS_PORT": 6379,
    }
)
```

### Custom Timeouts

Control cache expiration per data source:

```python
from flask_caching import Cache
from vizro.managers import data_manager

data_manager.cache = Cache(config={"CACHE_TYPE": "SimpleCache"})

# Default timeout (5 minutes)
data_manager["default_data"] = load_data

# Fast refresh (10 seconds)
data_manager["live_data"] = load_live_data
data_manager["live_data"].timeout = 10

# Slow refresh (1 hour)
data_manager["historical"] = load_historical
data_manager["historical"].timeout = 3600

# Never expire (like static)
data_manager["reference"] = load_reference
data_manager["reference"].timeout = 0
```

## Best Practices

### When to Use Static Data

- Data doesn't need to refresh
- Simple, small datasets

### When to Use Dynamic Data

- Data needs to refresh without restart
- Large datasets benefiting from caching
- Need parametrized loading

### Performance Tips

1. **Use appropriate dtypes** (`category` for strings)
1. **Pre-aggregate** dynamic data in the loading function
1. **Parametrize early** dynamic data in the loading function
1. **Enable caching** for slow dynamic data loads
1. **Use FileSystemCache or Redis** in production for dynamic data\`\`\`

## Comparison Summary

| Feature                                            | Static    | Dynamic      |
| -------------------------------------------------- | --------- | ------------ |
| Python type                                        | DataFrame | Function     |
| Supply directly in `data_frame` argument of figure | Yes       | No           |
| Reference by name after adding to data manager     | Yes       | Yes          |
| Refresh while running                              | No        | Yes          |
| Caching                                            | N/A       | Configurable |
| Parametrized loading                               | No        | Yes          |
| Production ready                                   | Yes       | Yes          |

---

# Advanced Patterns

## Parametrized Dynamic Data Loading

Add parameters to control what data is loaded:

```python
from vizro.managers import data_manager
import pandas as pd


def load_data(sample_size=100):
    df = pd.read_csv("large_data.csv")
    return df.sample(sample_size)


data_manager["data"] = load_data

page = vm.Page(
    title="Parametrized Data",
    components=[
        vm.Graph(
            id="chart",  # Need ID for parameter targeting
            figure=px.scatter("data", x="x", y="y"),
        ),
    ],
    controls=[
        vm.Parameter(
            targets=["chart.data_frame.sample_size"],
            selector=vm.Slider(min=10, max=1000, value=100),
        ),
    ],
)
```

**Target syntax**: `<component_id>.data_frame.<function_argument>`

### Security

Always validate user input in parametrized loading:

```python
from werkzeug.utils import secure_filename


def load_file(filename):
    safe_name = secure_filename(filename)
    return pd.read_csv(f"data/{safe_name}.csv")
```

## Common Data Patterns

### Database Connection

```python
import sqlalchemy as sa
import pandas as pd


def load_from_database():
    engine = sa.create_engine("postgresql://user:pass@host/db")
    query = """
        SELECT * FROM sales
        WHERE date >= CURRENT_DATE - INTERVAL '30 days'
    """
    return pd.read_sql(query, engine)


data_manager["sales"] = load_from_database
data_manager["sales"].timeout = 300  # 5-minute cache
```

### API Fetch

```python
import requests
import pandas as pd


def load_from_api():
    response = requests.get("https://api.example.com/metrics", headers={"Authorization": "Bearer token"})
    return pd.DataFrame(response.json())


data_manager["api_data"] = load_from_api
```

### Multiple Files

```python
from pathlib import Path
import pandas as pd


def load_all_csvs():
    files = Path("data/").glob("*.csv")
    dfs = [pd.read_csv(f) for f in files]
    return pd.concat(dfs, ignore_index=True)


data_manager["combined"] = load_all_csvs
```

### Pre-Aggregated Data

For better performance, aggregate in the loading function:

```python
def load_summary():
    df = pd.read_csv("transactions.csv")
    return (
        df.groupby(["region", "product"])
        .agg(
            {
                "revenue": "sum",
                "orders": "count",
            }
        )
        .reset_index()
    )


data_manager["summary"] = load_summary
```

## Dynamic Filters

Filters on dynamic data automatically update their options when data changes:

```python
def load_data(limit=100):
    df = pd.read_csv("data.csv")
    return df.head(limit)


data_manager["data"] = load_data

page = vm.Page(
    title="Dynamic Filters",
    components=[
        vm.Graph(id="chart", figure=px.scatter("data", x="category", y="value")),
    ],
    controls=[
        # Filter options update when data refreshes
        vm.Filter(column="category"),
        # Parameter to control data loading
        vm.Parameter(
            targets=["chart.data_frame.limit"],
            selector=vm.Slider(min=10, max=500, value=100),
        ),
    ],
)
```

**Static filter options** (don't update with data):

```python
vm.Filter(
    column="status",
    selector=vm.Dropdown(options=["Active", "Inactive", "Pending"]),
)
```

## Documentation Links

- **Data Guide**: https://vizro.readthedocs.io/en/latest/pages/user-guides/data/
- **Flask-Caching**: https://flask-caching.readthedocs.io/en/latest/
