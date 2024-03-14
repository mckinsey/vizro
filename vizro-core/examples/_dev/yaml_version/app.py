"""Example to show dashboard configuration specified as a YAML file."""

import datetime
import random
from pathlib import Path

import pandas as pd
import vizro.plotly.express as px
import yaml
from vizro import Vizro
from vizro.managers import data_manager
from vizro.models import Dashboard

data_manager["iris"] = px.data.iris
data_manager["gapminder"] = px.data.gapminder
data_manager["gapminder_2007"] = px.data.gapminder().query("year == 2007")

date_data_frame = pd.DataFrame(
    {
        "type": [random.choice(["A", "B", "C"]) for _ in range(31)],
        "value": [random.randint(0, 100) for _ in range(31)],
        "time": [datetime.datetime(2024, 1, 1) + datetime.timedelta(days=i) for i in range(31)],
    }
)
data_manager["date_data_frame"] = date_data_frame

dashboard = yaml.safe_load(Path("dashboard.yaml").read_text(encoding="utf-8"))
dashboard = Dashboard(**dashboard)

if __name__ == "__main__":
    Vizro(assets_folder="../assets").build(dashboard).run()
