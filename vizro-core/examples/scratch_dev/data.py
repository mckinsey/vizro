from datetime import datetime

import numpy as np
import pandas as pd

# ── 1. Daily time-series data (used for the line chart) ──────────────────────
daily_data = pd.DataFrame(
    {
        "date": pd.date_range("2026-10-01", periods=8, freq="D"),
        "total_production_volume_ton": [215, 182, 207, 175, 171, 237, 185, 231],
        "daily_avg_wip_ton": [14.2, 18.6, 13.9, 16.5, 12.1, 19.3, 15.7, 17.4],
        "avg_lead_time_day": [3.1, 4.2, 2.9, 3.8, 2.5, 4.5, 3.0, 3.9],
    }
)
daily_data["date_label"] = daily_data["date"].dt.strftime("%-m/%d")  # "10/01" etc.

# ── 1b. Scenario comparison line chart: two datasets (Baseline vs Scenario a) ─
_dates = pd.date_range("2026-10-01", periods=8, freq="D")
_date_labels = [d.strftime("%-m/%d") for d in _dates]
# Baseline: dotted white line in chart
daily_baseline = pd.DataFrame(
    {
        "date": _dates,
        "date_label": _date_labels,
        "ton": [56, 43, 50, 48, 42, 56, 43, 59],
    }
)
# Scenario a: solid teal line in chart
daily_scenario_a = pd.DataFrame(
    {
        "date": _dates,
        "date_label": _date_labels,
        "ton": [38, 65, 49, 50, 45, 52, 42, 68],
    }
)

# ── 2. KPI summary cards (left panel) ────────────────────────────────────────

kpi_summary_production = pd.DataFrame(
    [
        {
            "kpi": "Total production volume",
            "description": "The total production volume",
            "value": 1608.00,
            "unit": "ton",
            "baseline_value": 1285.00,
            "baseline_unit": "ton",
            "change_pct": 25.1,
            "direction": "up",
        },
    ]
)

kpi_summary_average = pd.DataFrame(
    [
        {
            "kpi": "Daily average WIP",
            "description": "The daily average WIP for all equipment during the period",
            "value": 14.56,
            "unit": "ton",
            "baseline_value": 25.02,
            "baseline_unit": "ton",
            "change_pct": -41.8,
            "direction": "down",
        },
    ]
)

kpi_summary_lead = pd.DataFrame(
    [
        {
            "kpi": "Average lead time",
            "description": "The average lead time for all product types across the 2nd company for the entire period",
            "value": 3.31,
            "unit": "day",
            "baseline_value": 8.25,
            "baseline_unit": "day",
            "change_pct": -59.8,
            "direction": "down",
        },
    ]
)

# ── 3. WIP by Equipment (used in the "WIP by Equipment" tab) ─────────────────
equipment_list = ["CNC Mill A", "CNC Mill B", "Lathe 1", "Lathe 2", "Assembly Line", "Paint Station"]
np.random.seed(42)
wip_by_equipment = pd.DataFrame(
    {
        "date": sorted(pd.date_range("2026-10-01", periods=8, freq="D").tolist() * len(equipment_list)),
        "equipment": equipment_list * 8,
        "wip_ton": np.round(np.random.uniform(5, 40, 8 * len(equipment_list)), 2),
    }
)

# ── 4. WIP Waterfall (used in the "WIP Waterfall" tab) ───────────────────────
wip_waterfall = pd.DataFrame(
    {
        "stage": ["Opening WIP", "New Orders", "Completed", "Scrapped", "Rework Added", "Closing WIP"],
        "value_ton": [120.0, 85.5, -95.3, -8.2, 12.6, 114.6],
        "waterfall_type": ["start", "increase", "decrease", "decrease", "increase", "end"],
    }
)

data = [
    {
        "scenario_name": "Increased high-end product",
        "baseline": False,
        "id": "8d256fb2-5d6e-4a1b-9c3f-2e7d8b1a4f05",
        "date_created": datetime(2026, 1, 27, 18, 28),
        "status": "Optimized",
        "created_ago": "A DAY AGO",
        "Scenario action": "Action",
    },
    {
        "scenario_name": "Baseline",
        "baseline": True,
        "id": "7c84c233-53f1-4b2d-8e6a-1f9c3d7e2b40",
        "date_created": datetime(2026, 1, 22, 18, 51),
        "status": "Optimized",
        "created_ago": "6 DAYS AGO",
        "Scenario action": "Action",
    },
    {
        "scenario_name": "Reduced pricing tier",
        "baseline": False,
        "id": "a1f3b892-7c4d-4e5f-b6a2-3d8e1c9f0b12",
        "date_created": datetime(2026, 1, 15, 10, 5),
        "status": "Optimized",
        "created_ago": "13 DAYS AGO",
        "Scenario action": "Action",
    },
    {
        "scenario_name": "Aggressive discounting",
        "baseline": False,
        "id": "d4e72c1a-8b3f-4a6d-9e5c-2f1b7a4d3e08",
        "date_created": datetime(2026, 1, 10, 14, 42),
        "status": "Failed",
        "created_ago": "18 DAYS AGO",
        "Scenario action": "Action",
    },
    {
        "scenario_name": "Bundle promotion strategy",
        "baseline": False,
        "id": "e9c15d3b-2a7f-4b8e-a3c6-5d2e8f1b4a09",
        "date_created": datetime(2026, 1, 3, 9, 17),
        "status": "Running",
        "created_ago": "25 DAYS AGO",
        "Scenario action": "Action",
    },
]

scenario_data = pd.DataFrame(data)
scenario_data["date_created"] = pd.to_datetime(scenario_data["date_created"])

# Comparison KPI: actual + two scenarios (for custom kpi_card_actual_vs_scenarios)
kpi_comparison_production = pd.DataFrame(
    [
        {
            "actual": 1285.00,
            "scenario_1": 1608.00,
            "scenario_2": 1710.28,
            "unit": "ton",
        }
    ]
)

kpi_comparison_avg = pd.DataFrame(
    [
        {
            "actual": 25.02,
            "scenario_1": 14.56,
            "scenario_2": 18.15,
            "unit": "ton",
        }
    ]
)

kpi_comparison_avg_lead = pd.DataFrame(
    [
        {
            "actual": 8.25,
            "scenario_1": 3.31,
            "scenario_2": 3.45,
            "unit": "day",
        }
    ]
)

kpis_per_product_type = pd.DataFrame(
    [
        {"product_type": "12K", "total_production_volume_ton": -1, "avg_lead_time_day": -1770.00},
        {"product_type": "1C", "total_production_volume_ton": -44, "avg_lead_time_day": -1747.50},
        {"product_type": "1K", "total_production_volume_ton": -3, "avg_lead_time_day": -2790.00},
        {"product_type": "1TC", "total_production_volume_ton": -15, "avg_lead_time_day": -4236.00},
        {"product_type": "2H", "total_production_volume_ton": -38, "avg_lead_time_day": -2985.11},
        {"product_type": "2K", "total_production_volume_ton": -22, "avg_lead_time_day": -3102.75},
        {"product_type": "3C", "total_production_volume_ton": -9, "avg_lead_time_day": -1563.00},
        {"product_type": "3K", "total_production_volume_ton": -51, "avg_lead_time_day": -4418.50},
        {"product_type": "4H", "total_production_volume_ton": -7, "avg_lead_time_day": -2241.25},
        {"product_type": "5TC", "total_production_volume_ton": -30, "avg_lead_time_day": -3677.00},
    ]
)
