"""Contains re-usable constants, data sets and custom charts."""

import json
from urllib.request import urlopen

import pandas as pd
import vizro.plotly.express as px

# DATA --------------------------------------------------------------
with urlopen("https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json") as response:
    counties = json.load(response)

gapminder = px.data.gapminder()
gapminder_2007 = gapminder.query("year == 2007")
iris = px.data.iris()
stocks = px.data.stocks()
tips = px.data.tips()
tips_agg = tips.groupby("day").agg({"total_bill": "sum"}).sort_values("total_bill").reset_index()
ages = pd.DataFrame(
    {
        "Age": ["0-19", "20-29", "30-39", "40-49", "50-59", ">=60"],
        "Male": [800, 2000, 4200, 5000, 2100, 800],
        "Female": [1000, 3000, 3500, 3800, 3600, 700],
    }
)
fips_unemp = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv",
    dtype={"fips": str},
)

sankey_data = pd.DataFrame(
    {
        "Origin": [0, 1, 2, 1, 2, 4, 0],  # indices inside labels
        "Destination": [1, 2, 3, 4, 5, 5, 6],  # indices inside labels
        "Value": [10, 4, 8, 6, 4, 8, 8],
    }
)

# CONSTANTS ---------------------------------------------------------
PAGE_GRID = [[0, 0, 0, 0, 0]] * 2 + [[1, 1, 1, 2, 2]] * 5
