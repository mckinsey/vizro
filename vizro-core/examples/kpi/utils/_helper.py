"""Contains helper functions and variables."""

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

    # Convert to correct data type
    data["Date Received"] = pd.to_datetime(data["Date Received"], format="%m/%d/%y").dt.strftime("%Y-%m-%d")
    data["Date Submitted"] = pd.to_datetime(data["Date Submitted"], format="%m/%d/%y").dt.strftime("%Y-%m-%d")

    # Create additional columns
    data["Year-Month Received"] = pd.to_datetime(data["Date Received"], format="%Y-%m-%d").dt.strftime("%Y-%m")
    data["Region"] = data["State"].map(REGION_MAPPING)
    data["Company response"] = np.where(
        data["Company response - detailed"].str.contains("Closed"), "Closed", data["Company response - detailed"]
    )
    data["Company response - Closed"] = np.where(
        data["Company response - detailed"].str.contains("Closed"), data["Company response - detailed"], "Not closed"
    )
    return data
