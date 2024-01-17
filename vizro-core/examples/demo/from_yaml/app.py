"""Example to show dashboard configuration specified as a YAML file."""
from pathlib import Path

import pandas as pd
import yaml

import vizro.plotly.express as px
from vizro import Vizro
from vizro.managers import data_manager
from vizro.models import Dashboard

df = px.data.gapminder()
df_mean = (
    df.groupby(by=["continent", "year"]).agg({"lifeExp": "mean", "pop": "mean", "gdpPercap": "mean"}).reset_index()
)

df_transformed = df.copy()
df_transformed["lifeExp"] = df.groupby(by=["continent", "year"])["lifeExp"].transform("mean")
df_transformed["gdpPercap"] = df.groupby(by=["continent", "year"])["gdpPercap"].transform("mean")
df_transformed["pop"] = df.groupby(by=["continent", "year"])["pop"].transform("sum")
df_concat = pd.concat([df_transformed.assign(color="Continent Avg."), df.assign(color="Country")], ignore_index=True)


data_manager["df"] = df
data_manager["df_2007"] = df.query("year == 2007")
data_manager["df_mean"] = df_mean
data_manager["df_mean_2007"] = df_mean.query("year == 2007")
data_manager["df_concat"] = df_concat

dashboard = yaml.safe_load(Path("dashboard.yaml").read_text(encoding="utf-8"))
dashboard = Dashboard(**dashboard)

if __name__ == "__main__":
    Vizro(assets_folder="../assets").build(dashboard).run()
