"""Example to show dashboard configuration specified as a YAML file."""

from pathlib import Path

import vizro.plotly.express as px
import yaml
from vizro import Vizro
from vizro.managers import data_manager
from vizro.models import Dashboard
from vizro.models.types import capture

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

gapminder = px.data.gapminder().query("country.isin(@selected_countries)")

data_manager["gapminder"] = gapminder
data_manager["gapminder_2007"] = gapminder.query("year == 2007")


@capture("graph")
def bar_with_highlight(data_frame, highlight_country=None):  # (1)!
    country_is_highlighted = data_frame["country"] == highlight_country  # (2)!
    fig = px.bar(
        data_frame,
        x="lifeExp",
        y="country",
        labels={"lifeExp": "lifeExp in 2007"},
        color=country_is_highlighted,
        category_orders={"country": sorted(data_frame["country"])},  # (3)!
    )
    fig.update_layout(showlegend=False)
    return fig


dashboard = yaml.safe_load(Path("dashboard.yaml").read_text(encoding="utf-8"))
dashboard = Dashboard(**dashboard)

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
