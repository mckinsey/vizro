"""Example to show dashboard configuration specified as a YAML file."""

from pathlib import Path

import pandas as pd
import vizro.plotly.express as px
import yaml
from vizro import Vizro
from vizro.managers import data_manager
from vizro.models import Dashboard

data_manager["iris"] = px.data.iris()
data_manager["gapminder"] = px.data.gapminder()
data_manager["gapminder_2007"] = px.data.gapminder().query("year == 2007")
data_manager["tips"] = px.data.tips()

df_stocks_long = pd.melt(
    px.data.stocks(datetimes=True),
    id_vars="date",
    value_vars=["GOOG", "AAPL", "AMZN", "FB", "NFLX", "MSFT"],
    var_name="stocks",
    value_name="value",
)
data_manager["df_stocks_long"] = df_stocks_long

df_kpi = pd.DataFrame({"Actual": [100, 200, 700], "Reference": [100, 300, 500], "Category": ["A", "B", "C"]})
data_manager["df_kpi"] = df_kpi

dashboard = yaml.safe_load(Path("dashboard.yaml").read_text(encoding="utf-8"))
dashboard = Dashboard(**dashboard)

if __name__ == "__main__":
    Vizro(assets_folder="../assets").build(dashboard).run()
