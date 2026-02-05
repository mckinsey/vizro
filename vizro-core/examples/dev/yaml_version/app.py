"""Example to show dashboard configuration specified as a YAML file."""

from pathlib import Path

import pandas as pd
import vizro.plotly.express as px
import yaml
from vizro import Vizro
from vizro.managers import data_manager
from vizro.models import Dashboard

selected_countries = [
    "Singapore",
    "Malaysia",
    "Thailand",
    "Indonesia",
    "Philippines",
    "Vietnam",
    "Cambodia",
    "Myanmar",
]

gapminder = px.data.gapminder()
gapminder_2007 = gapminder.query("year == 2007").copy()
gapminder_2007["is_europe"] = gapminder_2007["continent"] == "Europe"
selected_countries_gapminder = px.data.gapminder()[gapminder["country"].isin(selected_countries)]
selected_countries_gapminder_2007 = selected_countries_gapminder.query("year == 2007")
data_manager["iris"] = px.data.iris()
data_manager["tips"] = px.data.tips()
data_manager["stocks"] = px.data.stocks(datetimes=True)
data_manager["gapminder_2007"] = gapminder_2007
data_manager["df_kpi"] = pd.DataFrame(
    {"Actual": [100, 200, 700], "Reference": [100, 300, 500], "Category": ["A", "B", "C"]}
)
data_manager["selected_countries_gapminder"] = selected_countries_gapminder
data_manager["selected_countries_gapminder_2007"] = selected_countries_gapminder_2007
SPECIES_COLORS = {"setosa": "#00b4ff", "versicolor": "#ff9222", "virginica": "#3949ab"}

selected_countries_gapminder["rank"] = selected_countries_gapminder.groupby("year")["lifeExp"].rank(
    method="dense", ascending=False
)


dashboard = yaml.safe_load(Path("dashboard.yaml").read_text(encoding="utf-8"))
dashboard = Dashboard(**dashboard)

if __name__ == "__main__":
    Vizro(assets_folder="../assets").build(dashboard).run()
