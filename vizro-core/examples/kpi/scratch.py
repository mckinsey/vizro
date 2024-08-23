from functools import reduce

import pandas as pd
from utils._helper import clean_data_and_add_columns

df_complaints = pd.read_csv("https://query.data.world/s/glbdstahsuw3hjgunz3zssggk7dsfu?dws=00000")
df_complaints = clean_data_and_add_columns(df_complaints)

# Filter data within the date range and extract the Year
df_complaints = df_complaints[
    (df_complaints["Year-Month Received"] >= "2019-01") & (df_complaints["Year-Month Received"] <= "2020-12")
]
df_complaints["Year"] = df_complaints["Year-Month Received"].str[:4]


# Function to calculate percentage
def calculate_percentage(df, column, total_column, new_column):
    df[new_column] = df[column] / df[total_column] * 100


# Total complaints
total_complaints = (
    df_complaints.groupby("Year")
    .agg({"Complaint ID": "count"})
    .rename(columns={"Complaint ID": "Total Complaints"})
    .reset_index()
)

# Closed complaints
closed_complaints = (
    df_complaints[df_complaints["Company response"] == "Closed"]
    .groupby("Year")
    .agg({"Complaint ID": "count"})
    .rename(columns={"Complaint ID": "Closed Complaints"})
    .reset_index()
)

# Timely response
timely_response = (
    df_complaints[df_complaints["Timely response?"] == "Yes"]
    .groupby("Year")
    .agg({"Complaint ID": "count"})
    .rename(columns={"Complaint ID": "Timely response"})
    .reset_index()
)

# Closed without cost
closed_without_cost = (
    df_complaints[df_complaints["Company response - Closed"] != "Closed with monetary relief"]
    .groupby("Year")
    .agg({"Complaint ID": "count"})
    .rename(columns={"Complaint ID": "Closed w/o cost"})
    .reset_index()
)

# Consumer disputed
consumer_disputed = (
    df_complaints[df_complaints["Consumer disputed?"] == "Yes"]
    .groupby("Year")
    .agg({"Complaint ID": "count"})
    .rename(columns={"Complaint ID": "Consumer disputed"})
    .reset_index()
)

# Merge all KPI DataFrames
dfs_to_merge = [total_complaints, closed_complaints, timely_response, closed_without_cost, consumer_disputed]
df_kpi = reduce(lambda left, right: pd.merge(left, right, on="Year", how="outer"), dfs_to_merge)


# Calculate percentages
df_kpi.fillna(0, inplace=True)
calculate_percentage(df_kpi, "Closed Complaints", "Total Complaints", "Closed Complaints")
calculate_percentage(df_kpi, "Closed Complaints", "Total Complaints", "Open Complaints")
calculate_percentage(df_kpi, "Timely response", "Total Complaints", "Timely response")
calculate_percentage(df_kpi, "Closed w/o cost", "Total Complaints", "Closed w/o cost")
calculate_percentage(df_kpi, "Consumer disputed", "Total Complaints", "Consumer disputed")

# Pivot the DataFrame
df_kpi["index"] = 0
df_pivot = df_kpi.pivot(
    index="index",
    columns="Year",
    values=[
        "Total Complaints",
        "Closed Complaints",
        "Open Complaints",
        "Timely response",
        "Closed w/o cost",
        "Consumer disputed",
    ],
)
df_pivot.columns = [f"{kpi}_{year}" for kpi, year in df_pivot.columns]

print(df_pivot)
