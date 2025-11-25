# Examples

## Run Examples

```bash
cd vizro-mcp

# Example 1: Get JSON schemas for Vizro models
hatch run python examples/schema_example.py

# Example 2: Validate dashboard configurations
hatch run python examples/validate_dashboard_example.py
```

## Quick Usage

```python
from vizro_mcp import validate_dashboard, get_model_schema, get_sample_data

# Get model schema
schema = get_model_schema("Dashboard")

# Validate a dashboard config
iris = get_sample_data("iris")
result = validate_dashboard({"pages": [{"title": "Test", "components": [...]}]}, [iris])
print(result.valid, result.python_code)
```
