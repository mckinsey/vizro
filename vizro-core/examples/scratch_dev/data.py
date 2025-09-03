import random

import numpy as np
import pandas as pd


def create_market_data():
    """Creates fake data."""
    np.random.seed(42)

    industry_verticals = ["Dairy", "Bakery", "Culinary", "Bars & Confectionary", "Industrial", "Beverages"]

    industry_data = pd.DataFrame(
        {
            "Industry": industry_verticals,
            "2024_Revenue": np.random.randint(15, 45, size=len(industry_verticals)),
            "Opportunity": np.random.randint(10, 35, size=len(industry_verticals)),
        }
    )

    industry_data["Total"] = industry_data["2024_Revenue"] + industry_data["Opportunity"]
    industry_data["Estimated_Share"] = [
        f"{low}-{high}%"
        for low, high in zip(
            np.random.randint(30, 70, len(industry_verticals)), np.random.randint(60, 85, len(industry_verticals))
        )
    ]
    return industry_data


def create_map_chart_data():
    """Creates fake data."""
    state_data = {
        "state": [
            "AL",
            "AK",
            "AZ",
            "AR",
            "CA",
            "CO",
            "CT",
            "DE",
            "FL",
            "GA",
            "HI",
            "ID",
            "IL",
            "IN",
            "IA",
            "KS",
            "KY",
            "LA",
            "ME",
            "MD",
            "MA",
            "MI",
            "MN",
            "MS",
            "MO",
            "MT",
            "NE",
            "NV",
            "NH",
            "NJ",
            "NM",
            "NY",
            "NC",
            "ND",
            "OH",
            "OK",
            "OR",
            "PA",
            "RI",
            "SC",
            "SD",
            "TN",
            "TX",
            "UT",
            "VT",
            "VA",
            "WA",
            "WV",
            "WI",
            "WY",
        ],
        "market_level": [
            "Medium",
            "Low",
            "Medium",
            "Medium",
            "High",
            "Medium",
            "High",
            "Medium",
            "High",
            "High",
            "Medium",
            "Medium",
            "High",
            "High",
            "High",
            "Medium",
            "Medium",
            "Medium",
            "High",
            "High",
            "High",
            "High",
            "High",
            "Low",
            "Medium",
            "Low",
            "Medium",
            "Medium",
            "High",
            "High",
            "Low",
            "High",
            "High",
            "Medium",
            "High",
            "Medium",
            "High",
            "High",
            "High",
            "Medium",
            "Medium",
            "Medium",
            "High",
            "Low",
            "High",
            "High",
            "High",
            "Low",
            "High",
            "Low",
        ],
        "market_value": [
            3,
            1,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            1,
            3,
            1,
            3,
            3,
            3,
            3,
            1,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            3,
            1,
            3,
            3,
            3,
            1,
            3,
            1,
        ],  # Numeric values for coloring
    }

    market_mapping = {"High": 3, "Medium": 2, "Low": 1}
    state_data["market_numeric"] = [market_mapping[level] for level in state_data["market_level"]]

    df_map = pd.DataFrame(state_data)
    return df_map


def create_market_category_data():
    """Creates fake data."""
    categories_sb = [
        "Protein Solutions",
        "Emulsifiers & Sweeteners",
        "Cellulosics & Food Protection",
        "Core Texturants",
        "Systems",
        "Savory Solutions",
        "Inclusions",
    ]

    revenue_sb = [63, 32, 34, 39, 26, 0, 0]
    opportunity_sb = [16, 39, 29, 21, 21, 7, 2]

    industry_verticals = ["Dairy", "Bakery", "Culinary", "Bars & Confectionary", "Industrial", "Beverages"]

    data_sb = []
    for cat, rev, opp in zip(categories_sb, revenue_sb, opportunity_sb):
        # Pick a random industry for each row
        industry = random.choice(industry_verticals)
        data_sb.append({"Category": cat, "Type": "2024 Revenue", "Value": rev, "Industry": industry})
        data_sb.append({"Category": cat, "Type": "Opportunity", "Value": opp, "Industry": industry})

    return pd.DataFrame(data_sb)


# Show labels inside big-enough segments (and always for "Current")
def label_for_row(row, min_to_show=5):
    """Show labels inside big-enough segments."""
    v = int(row["Value"])
    if row["Component"] == "Current" or v >= min_to_show:
        return f"{v}M" if v > 0 else ""
    return ""


def create_market_summary_data():
    """Creates fake data."""
    data = [
        # Protein Solutions (≈79)
        ("Protein<br>Solutions", "Churn", 2),
        ("Protein<br>Solutions", "Cross-sell", 0),
        ("Protein<br>Solutions", "Current", 63),
        ("Protein<br>Solutions", "Pricing", 9),
        ("Protein<br>Solutions", "Whitespace", 5),
        # Emulsifiers & Sweeteners (≈71)
        ("Emulsifiers<br>& Sweeteners", "Churn", 12),
        ("Emulsifiers<br>& Sweeteners", "Cross-sell", 11),
        ("Emulsifiers<br>& Sweeteners", "Current", 32),
        ("Emulsifiers<br>& Sweeteners", "Pricing", 3),
        ("Emulsifiers<br>& Sweeteners", "Whitespace", 13),
        # Cellulosics & Food Protection (≈63)
        ("Cellulosics<br>& Food Protection", "Churn", 6),
        ("Cellulosics<br>& Food Protection", "Cross-sell", 9),
        ("Cellulosics<br>& Food Protection", "Current", 34),
        ("Cellulosics<br>& Food Protection", "Pricing", 5),
        ("Cellulosics<br>& Food Protection", "Whitespace", 9),
        # Core Texturants (≈59)
        ("Core<br>Texturants", "Churn", 2),
        ("Core<br>Texturants", "Cross-sell", 2),
        ("Core<br>Texturants", "Current", 39),
        ("Core<br>Texturants", "Pricing", 8),
        ("Core<br>Texturants", "Whitespace", 8),
        # Systems (≈47)
        ("Systems", "Churn", 5),
        ("Systems", "Cross-sell", 3),
        ("Systems", "Current", 26),
        ("Systems", "Pricing", 5),
        ("Systems", "Whitespace", 8),
        # Savory Solutions (≈7)
        ("Savory<br>Solutions", "Churn", 1),
        ("Savory<br>Solutions", "Cross-sell", 1),
        ("Savory<br>Solutions", "Current", 3),
        ("Savory<br>Solutions", "Pricing", 1),
        ("Savory<br>Solutions", "Whitespace", 1),
        # Inclusions (≈2)
        ("Inclusions", "Churn", 0),
        ("Inclusions", "Cross-sell", 0),
        ("Inclusions", "Current", 2),
        ("Inclusions", "Pricing", 0),
        ("Inclusions", "Whitespace", 0),
    ]

    df_page3_bar = pd.DataFrame(data, columns=["Category", "Component", "Value"])
    df_page3_bar["Label"] = df_page3_bar.apply(label_for_row, axis=1)
    return df_page3_bar


def generate_aggriddata(n=100):
    """Creates fake data."""
    company_prefixes = [
        "Agropur",
        "Almanace Foods",
        "Alpenrose",
        "Alta Dena",
        "Aurora",
        "Heritage",
        "Summit",
        "Evergreen",
        "Brookfield",
        "Riverdale",
        "Golden Valley",
        "Greenfield",
        "Crescent",
        "Highland",
        "Pioneer",
        "Silver Creek",
        "Maple Hill",
        "Lakeshore",
        "Crystal Farms",
        "Blue Ridge",
    ]

    company_suffixes = [
        "Dairy",
        "Foods",
        "Creamery",
        "Beverages",
        "Organics",
        "Cheese Co.",
        "Ice Cream",
        "Holdings",
        "Enterprises",
        "Brands",
        "Products, Inc.",
        "Corp.",
        "LLC",
        "Industries",
        "Group",
    ]

    # Create random company-style names
    business_names = [f"{random.choice(company_prefixes)} {random.choice(company_suffixes)}" for _ in range(n)]

    tiers = ["Bronze", "Silver", "Gold", "Platinum"]
    likelihood_scores = ["High", "Medium", "Low"]
    industry_priorities = ["High", "Medium", "Low"]
    churn_risks = ["High", "Medium", "Low"]
    industry_verticals = ["Dairy", "Bakery", "Culinary", "Bars & Confectionary", "Industrial", "Beverages"]

    data = {
        "Business Name": business_names,
        "Tier": random.choices(tiers, k=n),
        "Current Sales": [f"{round(x, 1)}M" for x in np.random.uniform(0, 5, n)],
        "Potential Opportunity": [f"{round(x, 1)}M" for x in np.random.uniform(0, 5, n)],
        "Likelihood Score": random.choices(likelihood_scores, k=n),
        "Industry Priority": random.choices(industry_priorities, k=n),
        "Growth Opportunity": [f"{round(x, 1)}M" for x in np.random.uniform(0, 3, n)],
        "Price Opportunity": [f"{round(x, 1)}M" for x in np.random.uniform(0, 2, n)],
        "Churn Risk": random.choices(churn_risks, k=n),
        "Industry": random.choices(industry_verticals, k=n),
    }

    return pd.DataFrame(data)


market_industry_data = create_market_data()
market_category_data = create_market_category_data()
map_chart_data = create_map_chart_data()
market_summary_data = create_market_summary_data()
aggrid_data = generate_aggriddata(100)
