"""Example to show dashboard configuration."""
import pandas as pd
from d3_beeswarm_chart import D3BeeswarmChart

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.models.types import capture

data_frame = [
    {"category": "A", "value": 40, "value2": 20},
    {"category": "C", "value": 35, "value2": 65},
]


@capture("graph")
def beeswarm(data_frame=None, **kwargs):
    return D3BeeswarmChart(data_frame=data_frame.to_dict(orient="records"), **kwargs)


@capture("graph")
def custom_box(x: str, y: str, color: str, data_frame=None):
    fig = px.box(data_frame=data_frame, x=x, y=y, color=color)
    fig.update_layout(showlegend=False)
    return fig


page_1 = vm.Page(
    title="Beeswarm",
    layout=vm.Layout(grid=[[0, 1]]),
    components=[
        vm.Table(
            id="custom_beeswarm",
            figure=beeswarm(
                data_frame=pd.DataFrame(data_frame), value="value", label="category", x_axis="value", y_axis="value2"
            ),
        ),
        vm.Graph(
            id="custom_box",
            figure=custom_box(x="continent", y="lifeExp", color="continent", data_frame=px.data.gapminder()),
        ),
    ],
)

page_2 = vm.Page(
    title="Beeswarm 2",
    components=[
        vm.Graph(
            id="custom_box_3",
            figure=custom_box(x="continent", y="lifeExp", color="continent", data_frame=px.data.gapminder()),
        ),
    ],
)


dashboard = vm.Dashboard(pages=[page_1, page_2], navigation=vm.Navigation(nav_selector=vm.NavBar()))

if __name__ == "__main__":
    Vizro(assets_folder="../assets").build(dashboard).run()
