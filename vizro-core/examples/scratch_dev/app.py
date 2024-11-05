"""Dev app to try things out."""

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro._themes._color_values import COLORS

pastry = pd.DataFrame(
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
    title="Charts UI",
    components=[
        vm.Graph(
            figure=px.bar(
                pastry.sort_values("Profit Ratio"),
                orientation="h",
                x="Profit Ratio",
                y="pastry",
                color="Profit Ratio",
                color_continuous_scale=COLORS["DIVERGING_RED_CYAN"],
            ),
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
