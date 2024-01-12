"""Example to show dashboard configuration specified as a JSON file."""
import json
from pathlib import Path

import pandas as pd

import vizro.plotly.express as px
from vizro import Vizro
from vizro.managers import data_manager
from vizro.models import Dashboard


def retrieve_gapminder():
    """This is a function that returns gapminder data."""
    return px.data.gapminder()


def retrieve_gapminder_year(year: int):
    """This is a function that returns gapminder data for a year."""
    return px.data.gapminder().query(f"year == {year}")


def retrieve_gapminder_continent_comparison():
    """This is a function adds aggregated continent information to gapminder data."""
    df_gapminder = px.data.gapminder()
    df_gapminder_agg = px.data.gapminder()

    df_gapminder_agg["lifeExp"] = df_gapminder_agg.groupby(by=["continent", "year"])["lifeExp"].transform("mean")
    df_gapminder_agg["gdpPercap"] = df_gapminder_agg.groupby(by=["continent", "year"])["gdpPercap"].transform("mean")
    df_gapminder_agg["pop"] = df_gapminder_agg.groupby(by=["continent", "year"])["pop"].transform("sum")

    df_gapminder["data"] = "Country"
    df_gapminder_agg["data"] = "Continent"

    df_gapminder_comp = pd.concat([df_gapminder_agg, df_gapminder], ignore_index=True)

    return df_gapminder_comp


def retrieve_avg_gapminder():
    """This is a function that returns aggregated gapminder data."""
    df = px.data.gapminder()
    mean = (
        df.groupby(by=["continent", "year"]).agg({"lifeExp": "mean", "pop": "mean", "gdpPercap": "mean"}).reset_index()
    )
    return mean


def retrieve_avg_gapminder_year(year: int):
    """This is a function that returns aggregated gapminder data for a specific year."""
    return retrieve_avg_gapminder().query(f"year == {year}")


# If you're not interested in lazy loading then you could just do data_manager["gapminder"] = px.data.gapminder()
data_manager["gapminder"] = retrieve_gapminder
data_manager["gapminder_2007"] = lambda: retrieve_gapminder_year(2007)
data_manager["gapminder_avg"] = retrieve_avg_gapminder
data_manager["gapminder_avg_2007"] = lambda: retrieve_avg_gapminder_year(2007)
data_manager["gapminder_country_analysis"] = retrieve_gapminder_continent_comparison

dashboard = json.loads(Path("dashboard.json").read_text(encoding="utf-8"))
dashboard = Dashboard(**dashboard)

if __name__ == "__main__":
    Vizro(assets_folder="../assets").build(dashboard).run()
