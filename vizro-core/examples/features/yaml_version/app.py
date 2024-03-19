"""Example to show dashboard configuration specified as a YAML file."""

from pathlib import Path

import vizro.plotly.express as px
import yaml
from vizro import Vizro
from vizro.managers import data_manager
from vizro.models import Dashboard

data_manager["iris"] = px.data.iris()
data_manager["tips"] = px.data.tips()
data_manager["stocks"] = px.data.stocks(datetimes=True)
data_manager["gapminder_2007"] = px.data.gapminder().query("year == 2007")

dashboard = yaml.safe_load(Path("dashboard.yaml").read_text(encoding="utf-8"))
dashboard = Dashboard(**dashboard)

if __name__ == "__main__":
    Vizro(assets_folder="../assets").build(dashboard).run()
