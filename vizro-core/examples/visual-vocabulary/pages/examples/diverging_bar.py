import pandas as pd
import vizro.plotly.express as px

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
).sort_values("Profit Ratio")

fig = px.bar(pastries, x="Profit Ratio", y="pastry")
