"""Example to show dashboard configuration."""

from typing import Optional

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture

gapminder_pos = px.data.gapminder()
gapminder_neg = px.data.gapminder()
gapminder_mixed = px.data.gapminder()
gapminder_neg["lifeExp"] = gapminder_neg["lifeExp"] * (-1)
gapminder_mixed["lifeExp"].iloc[:200] = gapminder_mixed["lifeExp"].iloc[:200] * (-1)


@capture("graph")
def variable_map(data_frame: pd.DataFrame = None, color: Optional[str] = None, title: Optional[str] = None):
    """Custom choropleth figure that needs post update calls."""
    fig = px.choropleth(
        data_frame,
        locations="iso_alpha",
        color=color,
        hover_name="country",
        labels={
            "year": "year",
            "lifeExp": "Life expectancy",
            "pop": "Population",
            "gdpPercap": "GDP per capita",
        },
        title="Global development over time",
    )
    fig.update_layout(showlegend=False, title=title)
    fig.update_coloraxes(colorbar={"thickness": 10, "title": {"side": "right"}})
    return fig


page = vm.Page(
    title="Autocolorscale",
    layout=vm.Layout(grid=[[0, 1, 2]]),
    components=[
        vm.Graph(
            figure=variable_map(data_frame=gapminder_pos, color="lifeExp", title="Positive Life Expectancy"),
        ),
        vm.Graph(
            figure=variable_map(data_frame=gapminder_neg, color="lifeExp", title="Negative Life Expectancy"),
        ),
        vm.Graph(
            figure=variable_map(data_frame=gapminder_mixed, color="lifeExp", title="Mixed Life Expectancy"),
        ),
    ],
)
dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
