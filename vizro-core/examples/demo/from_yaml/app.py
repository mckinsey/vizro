"""Example to show dashboard configuration specified as a YAML file."""
from pathlib import Path

import pandas as pd
import yaml

import vizro.plotly.express as px
from vizro import Vizro
from vizro.managers import data_manager
from vizro.models import Dashboard

gapminder = px.data.gapminder()
gapminder_mean = (
    gapminder.groupby(by=["continent", "year"])
    .agg({"lifeExp": "mean", "pop": "mean", "gdpPercap": "mean"})
    .reset_index()
)

gapminder_transformed = gapminder.copy()
gapminder_transformed["lifeExp"] = gapminder.groupby(by=["continent", "year"])["lifeExp"].transform("mean")
gapminder_transformed["gdpPercap"] = gapminder.groupby(by=["continent", "year"])["gdpPercap"].transform("mean")
gapminder_transformed["pop"] = gapminder.groupby(by=["continent", "year"])["pop"].transform("sum")
gapminder_concat = pd.concat(
    [gapminder_transformed.assign(color="Continent Avg."), gapminder.assign(color="Country")], ignore_index=True
)


data_manager["gapminder"] = gapminder
data_manager["gapminder_2007"] = gapminder.query("year == 2007")
data_manager["gapminder_mean"] = gapminder_mean
data_manager["gapminder_mean_2007"] = gapminder_mean.query("year == 2007")
data_manager["gapminder_concat"] = gapminder_concat

dashboard = yaml.safe_load(Path("dashboard.yaml").read_text(encoding="utf-8"))
dashboard = Dashboard(**dashboard)

if __name__ == "__main__":
    Vizro(assets_folder="../assets").build(dashboard).run()
