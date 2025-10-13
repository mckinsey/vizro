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
data_manager["tips"] = px.data.tips()
data_manager["iris"] = px.data.iris()


@capture("graph")
def bar_with_highlight(data_frame, highlight_country=None):
    country_is_highlighted = data_frame["country"] == highlight_country
    fig = px.bar(
        data_frame,
        x="lifeExp",
        y="country",
        labels={"lifeExp": "lifeExp in 2007"},
        color=country_is_highlighted,
        category_orders={"country": sorted(data_frame["country"]), "color": [False, True]},
    )
    fig.update_layout(showlegend=False)
    return fig


@capture("graph")
def bump_chart_with_highlight(data_frame, highlight_country=None):
    rank = data_frame.groupby("year")["lifeExp"].rank(method="dense", ascending=False)

    fig = px.line(data_frame, x="year", y=rank, color="country", markers=True)
    fig.update_yaxes(title="Rank (1 = Highest lifeExp)", autorange="reversed", dtick=1)
    fig.update_traces(opacity=0.3, line_width=2)

    if highlight_country is not None:
        fig.update_traces(selector={"name": highlight_country}, opacity=1, line_width=3)

    return fig


dashboard = yaml.safe_load(Path("dashboard.yaml").read_text(encoding="utf-8"))
dashboard = Dashboard(**dashboard)

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
