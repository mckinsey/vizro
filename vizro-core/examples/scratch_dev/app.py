"""Dev app to try things out."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.managers import data_manager

df = px.data.iris()
data_manager["iris"] = df

# page = vm.Page(
#     title="My first dashboard",
#     components=[
#         vm.Graph(figure=px.scatter(df, x="sepal_length", y="petal_width", color="species")),
#         vm.Graph(figure=px.histogram(df, x="sepal_width", color="species")),
#     ],
#     controls=[
#         vm.Filter(column="species"),
#     ],
# )

# dashboard = vm.Dashboard(pages=[page])

# Same configuration as JSON
dashboard_config = {
    "type": "dashboard",
    "pages": [
        {
            "type": "page",
            "title": "My first dashboard",
            "components": [
                {
                    "type": "graph",
                    "figure": {
                        "_target_": "scatter",
                        "data_frame": "iris",
                        "x": "sepal_length",
                        "y": "petal_width",
                        "color": "species",
                    },
                },
                {
                    "type": "graph",
                    "figure": {
                        "_target_": "histogram",
                        "data_frame": "iris",
                        "x": "sepal_width",
                        "color": "species",
                    },
                },
            ],
            "controls": [
                {
                    "type": "filter",
                    "column": "species",
                }
            ],
        }
    ],
}

dashboard = vm.Dashboard.model_validate(dashboard_config)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
