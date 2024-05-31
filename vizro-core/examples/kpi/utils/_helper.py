"""Contains helper functions."""

import numpy as np
import pandas as pd

REGION_MAPPING = {
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


def clean_data_and_add_columns(data: pd.DataFrame):
    # Rename columns
    data.rename(
        columns={
            "Date Sumbited": "Date Submitted",
            "Submitted via": "Channel",
            "Company response to consumer": "Company response - detailed",
        },
        inplace=True,
    )

    # Clean cell values and/or assign different values
    data.fillna("N/A", inplace=True)
    data["Company response - detailed"] = data["Company response - detailed"].replace("Closed", "Closed without relief")

    # Convert to correct data type
    data["Date Received"] = pd.to_datetime(data["Date Received"], format="%m/%d/%y").dt.strftime("%Y-%m-%d")
    data["Date Submitted"] = pd.to_datetime(data["Date Submitted"], format="%m/%d/%y").dt.strftime("%Y-%m-%d")

    # Create additional columns
    data["Year-Month Received"] = pd.to_datetime(data["Date Received"], format="%Y-%m-%d").dt.strftime("%Y-%m")
    data["Region"] = data["State"].map(REGION_MAPPING).fillna("N/A")

    data["Company response"] = np.where(
        data["Company response - detailed"].str.contains("Closed"), "Closed", data["Company response - detailed"]
    )
    data["Company response - Closed"] = np.where(
        data["Company response - detailed"].str.contains("Closed"), data["Company response - detailed"], "Not closed"
    )
    return data
