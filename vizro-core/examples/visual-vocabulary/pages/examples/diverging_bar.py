import pandas as pd
import plotly.io as pio
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

pastries = pd.DataFrame(
    {
        "pastry": [
            "Scones",
            "Bagels",
            "Muffins",
            "Cakes",
            "Donuts",
            "Cookies",
            "Croissants",
            "Eclairs",
            "Brownies",
            "Tarts",
            "Macarons",
            "Pies",
        ],
        "Profit Ratio": [-0.10, -0.15, -0.05, 0.10, 0.05, 0.20, 0.15, -0.08, 0.08, -0.12, 0.02, -0.07],
    }
)

page = vm.Page(
    title="Diverging bar",
    components=[
        vm.Graph(
            figure=px.bar(
                pastries.sort_values("Profit Ratio"),
                orientation="h",
                x="Profit Ratio",
                y="pastry",
                color="Profit Ratio",
                color_continuous_scale=pio.templates["vizro_dark"].layout.colorscale.diverging,
                color_continuous_midpoint=0,
            ),
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
