import pandas as pd
from utils._helper import clean_data_and_add_columns

df_complaints = pd.read_csv("https://query.data.world/s/glbdstahsuw3hjgunz3zssggk7dsfu?dws=00000")
df_complaints = clean_data_and_add_columns(df_complaints)
df_complaints = df_complaints[
    (df_complaints["Year-Month Received"] >= "2018-01") & (df_complaints["Year-Month Received"] <= "2019-12")
]
df_complaints["Year"] = df_complaints["Year-Month Received"].str[:4]


# Total complaints
total_complaints = (
    df_complaints.groupby("Year")
    .agg({"Complaint ID": "count"})
    .rename(columns={"Complaint ID": "Total Complaints"})
    .reset_index()
)


# Closed and open complaints
closed_complaints = df_complaints[df_complaints["Company response"] == "Closed"]
closed_complaints = (
    closed_complaints.groupby("Year")
    .agg({"Complaint ID": "count"})
    .rename(columns={"Complaint ID": "Closed Complaints"})
    .reset_index()
)
df_kpi = pd.merge(total_complaints, closed_complaints, on="Year", how="outer")
df_kpi["Open Complaints"] = (
    (df_kpi["Total Complaints"] - df_kpi["Closed Complaints"]) / df_kpi["Total Complaints"] * 100
)
df_kpi["Closed Complaints"] = df_kpi["Closed Complaints"] / df_kpi["Total Complaints"] * 100


# Timely response
timely_response = df_complaints[df_complaints["Timely response?"] == "Yes"]
timely_response = (
    timely_response.groupby("Year")
    .agg({"Complaint ID": "count"})
    .rename(columns={"Complaint ID": "Timely response"})
    .reset_index()
)
df_kpi = pd.merge(df_kpi, timely_response, on="Year", how="outer")
df_kpi["Timely response"] = df_kpi["Timely response"] / df_kpi["Total Complaints"] * 100

# Closed w/o cost
closed_without_cost = df_complaints[df_complaints["Company response - Closed"] != "Closed with monetary relief"]
closed_without_cost = (
    closed_without_cost.groupby("Year")
    .agg({"Complaint ID": "count"})
    .rename(columns={"Complaint ID": "Closed w/o cost"})
    .reset_index()
)
df_kpi = pd.merge(df_kpi, closed_without_cost, on="Year", how="outer")
df_kpi["Closed w/o cost"] = df_kpi["Closed w/o cost"] / df_kpi["Total Complaints"] * 100

# Consumer disputed
consumer_disputed = df_complaints[df_complaints["Consumer disputed?"] == "Yes"]
consumer_disputed = (
    consumer_disputed.groupby("Year")
    .agg({"Complaint ID": "count"})
    .rename(columns={"Complaint ID": "Consumer disputed"})
    .reset_index()
)
df_kpi = pd.merge(df_kpi, consumer_disputed, on="Year", how="outer")
df_kpi["Consumer disputed"] = df_kpi["Consumer disputed"] / df_kpi["Total Complaints"] * 100
df_kpi = df_kpi.fillna(0)
print(df_kpi)
