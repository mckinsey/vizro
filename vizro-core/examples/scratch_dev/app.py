import pandas as pd

import vizro.plotly.express as px
import vizro.models as vm
import vizro.actions as va
from vizro import Vizro
from dash import dcc
from vizro.models.types import capture


df = px.data.iris()


@capture("action")
def download_data():
    return dcc.send_data_frame(df.to_csv, "mydf.csv")


@capture("graph")
def custom_bar(data_frame):
    return px.bar(data_frame, x="species", y="sepal_width")


page_1 = vm.Page(
    title="Vizro download",
    components=[
        vm.Graph(figure=custom_bar(df)),
        vm.Button(text="Download data", actions=vm.Action(function=download_data(), outputs=["vizro_download"])),
    ],
)


dashboard = vm.Dashboard(pages=[page_1])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
