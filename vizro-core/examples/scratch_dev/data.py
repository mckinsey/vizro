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
        "actual": 1500,
    }
)
# Scenario a: solid teal line in chart
daily_scenario_a = pd.DataFrame(
    {
        "date": _dates,
        "date_label": _date_labels,
        "ton": [38, 65, 49, 50, 45, 52, 42, 68],
        "actual": 1470,
    }
)

daily_scenario_b = pd.DataFrame(
    {
        "date": _dates,
        "date_label": _date_labels,
        "ton": [48, 65, 59, 50, 40, 52, 41, 58],
        "actual": 1720,
    }
)

daily_scenario_c = pd.DataFrame(
    {
        "date": _dates,
        "date_label": _date_labels,
        "ton": [38, 45, 49, 56, 47, 32, 41, 68],
        "actual": 1550,
    }
)

daily_scenario_d = pd.DataFrame(
    {
        "date": _dates,
        "date_label": _date_labels,
        "ton": [37, 35, 39, 56, 67, 62, 51, 68],
        "actual": 1350,
    }
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
        "status": "Optimized",
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

kpi_comparison_baseline = pd.DataFrame(
    [
        {
            "production_volume": 1285.00,
            "average_wip": 25.02,
            "average_lead": 8.25,
        }
    ]
)

kpi_comparison_scenario_a = pd.DataFrame(
    [
        {
            "scenario_name": "Increased high-end product",
            "production_volume": 1885.00,
            "average_wip": 35.02,
            "average_lead": 9.25,
        }
    ]
)

kpi_comparison_scenario_b = pd.DataFrame(
    [
        {
            "scenario_name": "Reduced pricing tier",
            "production_volume": 1485.00,
            "average_wip": 15.02,
            "average_lead": 4.25,
        }
    ]
)
kpi_comparison_scenario_c = pd.DataFrame(
    [
        {
            "scenario_name": "Aggressive discounting",
            "production_volume": 1585.00,
            "average_wip": 39.02,
            "average_lead": 5.65,
        }
    ]
)
kpi_comparison_scenario_d = pd.DataFrame(
    [
        {
            "scenario_name": "Bundle promotion strategy",
            "production_volume": 1155.00,
            "average_wip": 29.92,
            "average_lead": 4.15,
        }
    ]
)

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
