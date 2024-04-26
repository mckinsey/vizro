import numpy as np
import pandas as pd

region_mapping = {
    **{state: "North East" for state in ["CT", "ME", "MA", "NH", "RI", "VT", "NJ", "NY", "PA"]},
    **{state: "Mid West" for state in ["IL", "IN", "MI", "OH", "WI", "IA", "KS", "MN", "MO", "NE", "ND", "SD"]},
    **{
        state: "South"
        for state in [
            "DE",
            "FL",
            "GA",
            "MD",
            "NC",
            "SC",
            "VA",
            "WV",
            "DC",
            "AL",
            "KY",
            "MS",
            "TN",
            "AR",
            "LA",
            "OK",
            "TX",
        ]
    },
    **{state: "West" for state in ["AZ", "CO", "ID", "MT", "NV", "NM", "UT", "WY", "AK", "CA", "HI", "OR", "WA"]},
}

df_complaints = pd.read_csv("data/Financial Consumer Complaints.csv", na_values=['""'])

# Clean cell values
df_complaints.fillna("N/A", inplace=True)

# Convert to correct type
df_complaints["Date Received"] = pd.to_datetime(df_complaints["Date Received"], format="%m/%d/%y").dt.strftime(
    "%Y-%m-%d"
)
df_complaints["Date Sumbited"] = pd.to_datetime(df_complaints["Date Sumbited"], format="%m/%d/%y").dt.strftime(
    "%Y-%m-%d"
)

# Rename columns
df_complaints.rename(
    columns={
        "Date Sumbited": "Date Submitted",
        "Submitted via": "Channel",
        "Company response to consumer": "Company response - detailed",
    },
    inplace=True,
)

# Create additional columns
df_complaints["Year-Month Received"] = pd.to_datetime(df_complaints["Date Received"], format="%Y-%m-%d").dt.strftime(
    "%Y-%m"
)
df_complaints["Region"] = df_complaints["State"].map(region_mapping)
df_complaints["Company response"] = np.where(
    df_complaints["Company response - detailed"].str.contains("Closed"),
    "Closed",
    df_complaints["Company response - detailed"],
)
df_complaints["Company response - Closed"] = np.where(
    df_complaints["Company response - detailed"].str.contains("Closed"),
    df_complaints["Company response - detailed"],
    "Not closed",
)

print(df_complaints["Product"].unique())
print(df_complaints["Issue"].unique())
print(df_complaints["Sub-issue"].unique())
print(df_complaints["Company response"].unique())
print(df_complaints["Company response - Closed"].unique())
