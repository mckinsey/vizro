import pandas as pd

# Map state names to state codes
state_code_map = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
}

superstore_df = pd.read_csv("superstore.csv", encoding="latin1")

superstore_df["State_Code"] = superstore_df["State"].map(state_code_map)

superstore_df["Order Date"] = pd.to_datetime(superstore_df["Order Date"], errors="coerce")
superstore_df["Ship Date"] = pd.to_datetime(superstore_df["Ship Date"], errors="coerce")

superstore_df["Year"] = superstore_df["Order Date"].dt.year

# Find the latest 2 years in the dataset
latest_two_years = sorted(superstore_df["Year"].unique())[-2:]

# Filter dataframe for only those two years
superstore_df = superstore_df[superstore_df["Year"].isin(latest_two_years)].copy()

# Create Order Status - randomly assign one of three status values
import random

random.seed(42)  # For reproducibility
superstore_df["Order Status"] = superstore_df.apply(
    lambda x: random.choice(["Delivered", "In Transit", "Processing"]), axis=1
)


def create_superstore_product(data_frame):
    data_frame["Category / Sub-Category"] = data_frame["Category"] + " / " + data_frame["Sub-Category"]
    data_frame = (
        data_frame.groupby(["Category / Sub-Category", "Product Name"])
        .agg({"Sales": "sum", "Profit": "sum"})
        .reset_index()
    )
    data_frame["Profit Margin"] = data_frame["Profit"] / data_frame["Sales"]
    data_frame["Profit Absolute"] = abs(data_frame["Profit"])

    return data_frame


def pareto_customers_table(data_frame):
    df = data_frame.groupby("Customer Name")["Sales"].sum().reset_index().sort_values(by="Sales", ascending=False)

    df["Cumulative Sales"] = df["Sales"].cumsum()
    df["Cumulative %"] = 100 * df["Cumulative Sales"] / df["Sales"].sum()
    df["Rank"] = range(1, len(df) + 1)

    return df[["Rank", "Customer Name", "Sales", "Cumulative Sales", "Cumulative %"]]


def create_kpi_data(df, value_col="Sales"):
    df["Year"] = df["Order Date"].dt.year
    # sales_by_year = df.groupby('Year')[value_col].sum()

    if value_col in ["Order ID", "Customer ID"]:
        result_by_year = df.groupby("Year")[value_col].nunique()
    else:
        result_by_year = df.groupby("Year")[value_col].sum()

    new_df = pd.DataFrame({"total_2016": [result_by_year.get(2016, 0)], "total_2017": [result_by_year.get(2017, 0)]})

    return new_df
