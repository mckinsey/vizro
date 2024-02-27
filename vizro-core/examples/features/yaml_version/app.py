"""Example to show dashboard configuration specified as a YAML file."""

from pathlib import Path

import numpy as np
import vizro.plotly.express as px
import yaml
from vizro import Vizro
from vizro.managers import data_manager
from vizro.models import Dashboard

tips = px.data.tips()
tips["smoker"] = np.where(tips["smoker"] == "Yes", 1, 0)
data_manager["tips"] = tips
gapminder = px.data.gapminder()
data_manager["gapminder"] = gapminder
data_manager["gapminder_2007"] = gapminder.query("year == 2007")
data_manager["iris"] = px.data.iris()

dashboard = yaml.safe_load(Path("dashboard.yaml").read_text(encoding="utf-8"))
dashboard = Dashboard(**dashboard)

if __name__ == "__main__":
    Vizro(assets_folder="../assets").build(dashboard).run()
