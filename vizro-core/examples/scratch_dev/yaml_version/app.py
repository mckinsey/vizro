"""Example to show dashboard configuration specified as a YAML file."""

from pathlib import Path

import vizro.plotly.express as px
import yaml
from vizro import Vizro
from vizro.managers import data_manager
from vizro.models import Dashboard
from vizro.models.types import capture

data_manager["iris"] = px.data.iris()
data_manager["gapminder"] = px.data.gapminder().query("continent == 'Europe' and year == 2007")
data_manager["tips"] = px.data.tips()


@capture("graph")
def scatter_with_highlight(data_frame, highlight_country=None):
    country_is_highlighted = data_frame["country"] == highlight_country
    fig = px.scatter(
        data_frame,
        x="gdpPercap",
        y="lifeExp",
        size="pop",
        size_max=60,
        opacity=0.3,
        color=country_is_highlighted,
        category_orders={"color": [False, True]},
    )

    if highlight_country is not None:
        fig.update_traces(selector=1, marker={"line_width": 2, "opacity": 1})

    fig.update_layout(showlegend=False)
    return fig


dashboard = yaml.safe_load(Path("dashboard.yaml").read_text(encoding="utf-8"))
dashboard = Dashboard(**dashboard)

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
