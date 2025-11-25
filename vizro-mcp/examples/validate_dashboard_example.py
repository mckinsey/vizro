"""Example script demonstrating how to validate dashboard configurations with vizro_mcp.

This script shows how to:
1. Create a dashboard configuration as a Python dictionary
2. Validate it using the vizro_mcp core library
3. Get the generated Python code and PyCafe preview URL

Usage:
    python examples/validate_dashboard_example.py
"""

from vizro_mcp import (
    ChartPlan,
    DFMetaData,
    get_sample_data,
    validate_chart,
    validate_dashboard,
)


def example_simple_dashboard():
    """Validate a simple dashboard with one scatter plot."""
    print("=" * 60)
    print("Example 1: Simple Dashboard with Scatter Plot")
    print("=" * 60)

    # Get sample iris data metadata
    iris = get_sample_data("iris")

    # Define a simple dashboard config
    dashboard_config = {
        "title": "Iris Analysis Dashboard",
        "pages": [
            {
                "title": "Scatter Plot",
                "components": [
                    {
                        "type": "graph",
                        "title": "Sepal Dimensions by Species",
                        "figure": {
                            "_target_": "scatter",
                            "data_frame": "iris_data",
                            "x": "sepal_length",
                            "y": "sepal_width",
                            "color": "species",
                        },
                    }
                ],
            }
        ],
    }

    # Validate the dashboard
    result = validate_dashboard(dashboard_config, [iris])

    print(f"Valid: {result.valid}")
    print(f"Message: {result.message}")
    if result.valid:
        print(f"\nGenerated Python code ({len(result.python_code)} chars):")
        print("-" * 40)
        print(result.python_code)
        print("-" * 40)
        if result.pycafe_url:
            print(f"\nPyCafe URL: {result.pycafe_url[:80]}...")


def example_dashboard_with_filters():
    """Validate a dashboard with filters and multiple components."""
    print("\n" + "=" * 60)
    print("Example 2: Dashboard with Filters and Layout")
    print("=" * 60)

    # Define data metadata for tips dataset
    tips = get_sample_data("tips")

    # Dashboard with filters and grid layout
    dashboard_config = {
        "title": "Tips Analysis",
        "pages": [
            {
                "title": "Overview",
                "layout": {
                    "type": "grid",
                    "grid": [[0, 1], [2, 2]],
                },
                "components": [
                    {
                        "type": "graph",
                        "title": "Tips by Day",
                        "figure": {
                            "_target_": "bar",
                            "data_frame": "tips_data",
                            "x": "day",
                            "y": "tip",
                            "color": "sex",
                        },
                    },
                    {
                        "type": "graph",
                        "title": "Total Bill vs Tip",
                        "figure": {
                            "_target_": "scatter",
                            "data_frame": "tips_data",
                            "x": "total_bill",
                            "y": "tip",
                            "color": "smoker",
                        },
                    },
                    {
                        "type": "card",
                        "text": """
### Tips Dataset Analysis

This dashboard explores the relationship between:
- **Total bill** and **tip amount**
- **Day of week** patterns
- **Smoker vs non-smoker** behavior
                        """,
                    },
                ],
                "controls": [
                    {
                        "type": "filter",
                        "column": "day",
                        "selector": {"type": "dropdown", "multi": True},
                    },
                    {
                        "type": "filter",
                        "column": "smoker",
                    },
                ],
            }
        ],
    }

    result = validate_dashboard(dashboard_config, [tips])

    print(f"Valid: {result.valid}")
    print(f"Message: {result.message}")
    if result.valid and result.pycafe_url:
        print(f"PyCafe URL: {result.pycafe_url[:80]}...")


def example_dashboard_with_custom_chart():
    """Validate a dashboard with a custom chart function."""
    print("\n" + "=" * 60)
    print("Example 3: Dashboard with Custom Chart")
    print("=" * 60)

    gapminder = get_sample_data("gapminder")

    # Define a custom chart
    custom_chart = ChartPlan(
        chart_type="bubble",
        chart_name="gdp_life_bubble",
        imports=["import plotly.express as px"],
        chart_code="""
def gdp_life_bubble(data_frame):
    # Filter to 2007 data and create bubble chart
    df_2007 = data_frame[data_frame["year"] == 2007]
    fig = px.scatter(
        df_2007,
        x="gdpPercap",
        y="lifeExp",
        size="pop",
        color="continent",
        hover_name="country",
        log_x=True,
        title="GDP vs Life Expectancy (2007)"
    )
    return fig
        """,
    )

    # Dashboard using the custom chart
    dashboard_config = {
        "title": "Gapminder Analysis",
        "pages": [
            {
                "title": "Global Overview",
                "components": [
                    {
                        "type": "graph",
                        "title": "GDP vs Life Expectancy",
                        "figure": {
                            "_target_": "gdp_life_bubble",
                            "data_frame": "gapminder_data",
                        },
                    }
                ],
                "controls": [
                    {"type": "filter", "column": "continent"},
                ],
            }
        ],
    }

    result = validate_dashboard(dashboard_config, [gapminder], custom_charts=[custom_chart])

    print(f"Valid: {result.valid}")
    print(f"Message: {result.message}")
    if result.valid:
        print("\nGenerated code includes custom chart definition:")
        # Show just the custom chart part
        if "def gdp_life_bubble" in result.python_code:
            print("  - Custom chart 'gdp_life_bubble' included in generated code")
        if result.pycafe_url:
            print(f"PyCafe URL: {result.pycafe_url[:80]}...")


def example_validate_chart_only():
    """Validate just a chart (not a full dashboard)."""
    print("\n" + "=" * 60)
    print("Example 4: Validate Chart Only")
    print("=" * 60)

    stocks = get_sample_data("stocks")

    # Define a chart plan
    chart = ChartPlan(
        chart_type="line",
        chart_name="stock_trend",
        imports=["import plotly.express as px", "import pandas as pd"],
        chart_code="""
def stock_trend(data_frame):
    # Melt the dataframe to get stock symbols as a column
    df_melted = data_frame.melt(
        id_vars=["Date"],
        var_name="Symbol",
        value_name="Price"
    )
    fig = px.line(
        df_melted,
        x="Date",
        y="Price",
        color="Symbol",
        title="Stock Price Trends"
    )
    return fig
        """,
    )

    result = validate_chart(chart, stocks)

    print(f"Valid: {result.valid}")
    print(f"Message: {result.message}")
    if result.valid:
        print("\nGenerated chart code:")
        print("-" * 40)
        print(result.python_code)
        print("-" * 40)


def example_invalid_config():
    """Show how validation catches errors."""
    print("\n" + "=" * 60)
    print("Example 5: Invalid Configuration (Error Handling)")
    print("=" * 60)

    iris = get_sample_data("iris")

    # Invalid config - missing required 'pages' field
    invalid_config = {
        "title": "Invalid Dashboard",
        # 'pages' is required but missing!
    }

    result = validate_dashboard(invalid_config, [iris])

    print(f"Valid: {result.valid}")
    print(f"Message: {result.message[:200]}...")


def example_custom_data():
    """Validate with custom (local) data metadata."""
    print("\n" + "=" * 60)
    print("Example 6: Custom Local Data")
    print("=" * 60)

    # Define metadata for a local CSV file
    local_data = DFMetaData(
        file_name="sales_data",
        file_path_or_url="/path/to/your/sales_data.csv",
        file_location_type="local",
        read_function_string="pd.read_csv",
        column_names_types={
            "date": "str",
            "product": "str",
            "revenue": "float",
            "quantity": "int",
        },
    )

    dashboard_config = {
        "title": "Sales Dashboard",
        "pages": [
            {
                "title": "Revenue Analysis",
                "components": [
                    {
                        "type": "graph",
                        "figure": {
                            "_target_": "bar",
                            "data_frame": "sales_data",
                            "x": "product",
                            "y": "revenue",
                        },
                    }
                ],
            }
        ],
    }

    result = validate_dashboard(dashboard_config, [local_data])

    print(f"Valid: {result.valid}")
    print(f"Message: {result.message}")
    # Note: PyCafe URL will be None for local data
    print(f"PyCafe URL: {result.pycafe_url}")
    print("(PyCafe URL is None because data is local, not remote)")


def main():
    """Run all examples."""
    print("Vizro MCP - Dashboard Validation Examples")
    print("=" * 60)

    example_simple_dashboard()
    example_dashboard_with_filters()
    example_dashboard_with_custom_chart()
    example_validate_chart_only()
    example_invalid_config()
    example_custom_data()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
