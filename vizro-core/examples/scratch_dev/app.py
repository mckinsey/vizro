"""DDev app to try things out."""

import plotly.io as pio
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

iris = px.data.iris()
pio.templates["vizro_dark"]["layout"]["font_family"] = "Times New Roman, Inter, sans-serif, Arial, serif"
pio.templates["vizro_light"]["layout"]["font_family"] = "Times New Roman, Inter, sans-serif, Arial, serif"


page = vm.Page(
    title="Page with different font",
    components=[
        vm.Card(
            text="""
        # Lorem ipsum

        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam nec nunc nec libero ultricies ultricies.
        """
        ),
        vm.Graph(figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species")),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
