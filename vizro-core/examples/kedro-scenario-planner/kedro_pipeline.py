"""Kedro pipeline that powers the scenario planner demo.

A scenario filters the synthetic `orders` dataset by region, categories and a minimum order
value, then computes summary KPIs and a per-category revenue/order-count breakdown. Running a
scenario appends one row to `scenario_results` (the Vizro AgGrid's dynamic data source) and
writes a per-scenario breakdown CSV (a Vizro dynamic data source parametrized by scenario name).
"""

from datetime import datetime
from pathlib import Path

import pandas as pd
from data_generation import ORDERS_PATH, SCENARIO_RESULTS_PATH
from kedro.io import DataCatalog, MemoryDataset
from kedro.pipeline import Pipeline, node
from kedro.runner import SequentialRunner
from kedro_datasets.pandas import CSVDataset
from werkzeug.utils import secure_filename

BREAKDOWN_DIR = Path(__file__).parent / "data" / "breakdown"
BREAKDOWN_COLUMNS = ["category", "total_revenue", "n_orders"]


def build_static_catalog() -> DataCatalog:
    """Kedro Data Catalog for the two datasets that don't change shape between runs."""
    return DataCatalog.from_config(
        {
            "orders": {"type": "pandas.CSVDataset", "filepath": str(ORDERS_PATH)},
            "scenario_results": {"type": "pandas.CSVDataset", "filepath": str(SCENARIO_RESULTS_PATH)},
        }
    )


def _register_dataset(catalog: DataCatalog, name: str, dataset) -> None:
    # DataCatalog supports item assignment from Kedro 1.0 onwards; earlier versions require `.add`.
    try:
        catalog[name] = dataset
    except TypeError:
        catalog.add(name, dataset)


def filter_orders(orders: pd.DataFrame, region: str, min_order_value: float, categories: list[str]) -> pd.DataFrame:
    """Filters orders."""
    return orders[
        (orders["region"] == region)
        & (orders["order_value"] >= min_order_value)
        & (orders["category"].isin(categories))
    ]


def compute_kpis(
    filtered_orders: pd.DataFrame,
    scenario_name: str,
    region: str,
    min_order_value: float,
    categories: list[str],
) -> pd.DataFrame:
    """Computes kpis."""
    return pd.DataFrame(
        [
            {
                "scenario_name": scenario_name,
                "date_created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "region": region,
                "categories": ", ".join(categories),
                "min_order_value": min_order_value,
                "n_orders": len(filtered_orders),
                "total_revenue": round(filtered_orders["order_value"].sum(), 2),
                "avg_order_value": round(filtered_orders["order_value"].mean(), 2),
            }
        ]
    )


def compute_breakdown(filtered_orders: pd.DataFrame) -> pd.DataFrame:
    """Computes breakdown."""
    return filtered_orders.groupby("category", as_index=False).agg(
        total_revenue=("order_value", "sum"), n_orders=("order_value", "count")
    )


def build_pipeline() -> Pipeline:
    """Builds Kedro pipeline."""
    return Pipeline(
        [
            node(
                filter_orders,
                inputs=["orders", "region", "min_order_value", "categories"],
                outputs="filtered_orders",
                name="filter_orders",
            ),
            node(
                compute_kpis,
                inputs=["filtered_orders", "scenario_name", "region", "min_order_value", "categories"],
                outputs="kpi_row",
                name="compute_kpis",
            ),
            node(compute_breakdown, inputs="filtered_orders", outputs="breakdown", name="compute_breakdown"),
        ]
    )


def run_scenario(scenario_name: str, region: str, categories: list[str], min_order_value: float) -> dict:
    """Validate inputs, run the Kedro pipeline and persist its results.

    Raises:
        Exception: a `(message, notification_key)` pair for each validation failure, matching
            the custom notification keys wired up on the "Run scenario" button in `app.py`.
    """
    scenario_name = (scenario_name or "").strip()
    safe_name = secure_filename(scenario_name)
    if not scenario_name or not safe_name:
        raise Exception("Scenario name cannot be empty or contain only special characters.", "invalid_name")

    if not categories:
        raise Exception("Select at least one category to include.", "no_categories")

    catalog = build_static_catalog()
    existing_results = catalog.load("scenario_results")
    if not existing_results.empty and scenario_name in existing_results["scenario_name"].astype(str).to_numpy():
        raise Exception(
            f"A scenario named '{scenario_name}' already exists. Choose a different name.", "duplicate_name"
        )

    orders = catalog.load("orders")
    matching_orders = orders[
        (orders["region"] == region)
        & (orders["order_value"] >= min_order_value)
        & (orders["category"].isin(categories))
    ]
    if matching_orders.empty:
        raise Exception(
            "No orders match this combination of region, categories and minimum order value.",
            "no_matching_orders",
        )

    _register_dataset(catalog, "region", MemoryDataset(region))
    _register_dataset(catalog, "min_order_value", MemoryDataset(min_order_value))
    _register_dataset(catalog, "categories", MemoryDataset(categories))
    _register_dataset(catalog, "scenario_name", MemoryDataset(scenario_name))

    BREAKDOWN_DIR.mkdir(parents=True, exist_ok=True)
    _register_dataset(catalog, "breakdown", CSVDataset(filepath=str(BREAKDOWN_DIR / f"{safe_name}.csv")))

    SequentialRunner().run(build_pipeline(), catalog)
    # Load explicitly rather than using the runner's return value: depending on the Kedro version,
    # a "free" pipeline output may come back as the loaded data or as the dataset object itself.
    kpi_row = catalog.load("kpi_row")

    updated_results = pd.concat([existing_results, kpi_row], ignore_index=True)
    catalog.save("scenario_results", updated_results)

    return {
        "n_orders": int(kpi_row["n_orders"].iloc[0]),
        "total_revenue": float(kpi_row["total_revenue"].iloc[0]),
        "avg_order_value": float(kpi_row["avg_order_value"].iloc[0]),
    }


def load_breakdown_data(scenario_name: str | None = None) -> pd.DataFrame:
    """Vizro dynamic data loader for the per-scenario category breakdown charts."""
    if not scenario_name:
        return pd.DataFrame(columns=BREAKDOWN_COLUMNS)

    path = BREAKDOWN_DIR / f"{secure_filename(scenario_name)}.csv"
    if not path.exists():
        return pd.DataFrame(columns=BREAKDOWN_COLUMNS)

    return pd.read_csv(path)
