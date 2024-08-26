"""Contains helper functions and variables."""

from functools import reduce

import numpy as np
import pandas as pd

REGION_MAPPING = {
    **dict.fromkeys(["CT", "ME", "MA", "NH", "RI", "VT", "NJ", "NY", "PA"], "North East"),
    **dict.fromkeys(
        ["IL", "IN", "MI", "OH", "WI", "IA", "KS", "MN", "MO", "NE", "ND", "SD"], "Mid West"  # codespell:ignore
    ),
    **dict.fromkeys(
        ["DE", "FL", "GA", "MD", "NC", "SC", "VA", "WV", "DC", "AL", "KY", "MS", "TN", "AR", "LA"], "South"
    ),
    **dict.fromkeys(["AZ", "NM", "OK", "TX"], "South West"),
    **dict.fromkeys(["CO", "ID", "MT", "NV", "UT", "WY", "AK", "CA", "HI", "OR", "WA"], "West"),
    **dict.fromkeys(["UM", "PR", "AP", "VI", "AE", "AS", "GU", "FM", "PW", "MP"], "Other"),
}


def fill_na_with_random(df, column):
    """Fills missing values in a column with random values from the same column."""
    non_na_values = df[column].dropna().values
    df[column] = df[column].apply(lambda x: np.random.choice(non_na_values) if pd.isna(x) else x)
    return df[column]


def clean_data_and_add_columns(data: pd.DataFrame):
    """Tidies the original data set, adds new columns, and changes cell values for the purpose of this example."""
    data = data.rename(
        columns={
            "Date Sumbited": "Date Submitted",
            "Submitted via": "Channel",
            "Company response to consumer": "Company response - detailed",
        },
    )

    # Clean cell values and/or assign different values for the purpose of this example
    data["Company response - detailed"] = data["Company response - detailed"].replace("Closed", "Closed without relief")
    data["State"] = data["State"].replace("UNITED STATES MINOR OUTLYING ISLANDS", "UM")
    data["State"] = fill_na_with_random(data, "State")
    data["Consumer disputed?"] = data["Consumer disputed?"].fillna("No")

    # Convert to correct data type
    data["Date Received"] = pd.to_datetime(data["Date Received"], format="%m/%d/%y").dt.strftime("%Y-%m-%d")

    # Create additional columns
    data["Month"] = pd.to_datetime(data["Date Received"], format="%Y-%m-%d").dt.strftime("%m")
    data["Year"] = pd.to_datetime(data["Date Received"], format="%Y-%m-%d").dt.strftime("%Y")
    data["Region"] = data["State"].map(REGION_MAPPING)
    data["Company response"] = np.where(
        data["Company response - detailed"].str.contains("Closed"), "Closed", data["Company response - detailed"]
    )
    data["Company response - Closed"] = np.where(
        data["Company response - detailed"].str.contains("Closed"), data["Company response - detailed"], "Not closed"
    )

    # Filter 2018 and 2019 only
    data = data[(data["Year"].isin(["2018", "2019"]))]
    return data


def create_data_for_kpi_cards(data):
    """Formats and aggregates the data for the KPI cards."""
    total_complaints = (
        data.groupby("Year")
        .agg({"Complaint ID": "count"})
        .rename(columns={"Complaint ID": "Total Complaints"})
        .reset_index()
    )
    closed_complaints = (
        data[data["Company response"] == "Closed"]
        .groupby("Year")
        .agg({"Complaint ID": "count"})
        .rename(columns={"Complaint ID": "Closed Complaints"})
        .reset_index()
    )
    timely_response = (
        data[data["Timely response?"] == "Yes"]
        .groupby("Year")
        .agg({"Complaint ID": "count"})
        .rename(columns={"Complaint ID": "Timely response"})
        .reset_index()
    )
    closed_without_cost = (
        data[data["Company response - Closed"] != "Closed with monetary relief"]
        .groupby("Year")
        .agg({"Complaint ID": "count"})
        .rename(columns={"Complaint ID": "Closed w/o cost"})
        .reset_index()
    )
    consumer_disputed = (
        data[data["Consumer disputed?"] == "Yes"]
        .groupby("Year")
        .agg({"Complaint ID": "count"})
        .rename(columns={"Complaint ID": "Consumer disputed"})
        .reset_index()
    )

    # Merge all data frames into one
    dfs_to_merge = [total_complaints, closed_complaints, timely_response, closed_without_cost, consumer_disputed]
    df_kpi = reduce(lambda left, right: pd.merge(left, right, on="Year", how="outer"), dfs_to_merge)

    # Calculate percentages
    df_kpi.fillna(0, inplace=True)
    df_kpi["Closed Complaints"] = df_kpi["Closed Complaints"] / df_kpi["Total Complaints"] * 100
    df_kpi["Open Complaints"] = 100 - df_kpi["Closed Complaints"]
    df_kpi["Timely response"] = df_kpi["Timely response"] / df_kpi["Total Complaints"] * 100
    df_kpi["Closed w/o cost"] = df_kpi["Closed w/o cost"] / df_kpi["Total Complaints"] * 100
    df_kpi["Consumer disputed"] = df_kpi["Consumer disputed"] / df_kpi["Total Complaints"] * 100

    # Pivot the dataframe and flatten
    df_kpi["index"] = 0
    df_kpi = df_kpi.pivot(
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
    df_kpi.columns = [f"{kpi}_{year}" for kpi, year in df_kpi.columns]
    return df_kpi
