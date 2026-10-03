"""Synthetic data generation for the Kedro scenario planner demo."""

from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent / "data"
ORDERS_PATH = DATA_DIR / "orders.csv"
SCENARIO_RESULTS_PATH = DATA_DIR / "scenario_results.csv"

REGIONS = ["North", "South", "East", "West"]
CATEGORIES = ["Electronics", "Grocery", "Apparel", "Home", "Beauty"]

SCENARIO_RESULTS_COLUMNS = [
    "scenario_name",
    "date_created",
    "region",
    "categories",
    "min_order_value",
    "n_orders",
    "total_revenue",
    "avg_order_value",
]


def generate_orders(n=2000, seed=42) -> pd.DataFrame:
    """Generate orders data."""
    rng = np.random.default_rng(seed)
    return pd.DataFrame(
        {
            "order_id": np.arange(1, n + 1),
            "region": rng.choice(REGIONS, size=n),
            "category": rng.choice(CATEGORIES, size=n, p=[0.25, 0.25, 0.2, 0.2, 0.1]),
            "order_value": rng.gamma(shape=2.0, scale=40, size=n).round(2),
        }
    )


def ensure_orders_data() -> None:
    """Generate orders data."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not ORDERS_PATH.exists():
        generate_orders().to_csv(ORDERS_PATH, index=False)


def ensure_scenario_results_file() -> None:
    """Generate orders data."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not SCENARIO_RESULTS_PATH.exists():
        pd.DataFrame(columns=SCENARIO_RESULTS_COLUMNS).to_csv(SCENARIO_RESULTS_PATH, index=False)
