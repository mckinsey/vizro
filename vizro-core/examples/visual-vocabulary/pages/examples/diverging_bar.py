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
        ],
        "Profit Ratio": [-0.10, -0.05, 0.10, 0.05, 0.15, -0.08, 0.08, -0.12],
    }
)

page = vm.Page(
    title="Diverging bar",
    components=[
        vm.Graph(
            figure=px.bar(pastries.sort_values("Profit Ratio"), x="Profit Ratio", y="pastry"),
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
