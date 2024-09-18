"""DDev app to try things out."""

import plotly.io as pio
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

iris = px.data.iris()

# This previously did not work, because we defined a font family for subcategories of the charts
# e.g. xaxis_title_font_size, xaxis_tickfont_size, etc. However, if we only define the font family in our template
# it will be passed on to the chart's subcomponents and this way, users only have to do the change below
# if they want to change the font globally, instead of overwriting the font for every single subcomponent.
pio.templates["vizro_dark"]["layout"]["font_family"] = "PlayfairDisplay, Inter, sans-serif, Arial, serif"
pio.templates["vizro_light"]["layout"]["font_family"] = "PlayfairDisplay, Inter, sans-serif, Arial, serif"


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
