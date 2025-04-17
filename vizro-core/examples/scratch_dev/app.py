# Vizro is an open-source toolkit for creating modular data visualization applications.
# check out https://github.com/mckinsey/vizro for more info about Vizro
# and checkout https://vizro.readthedocs.io/en/stable/ for documentation.

import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm

df = px.data.iris()

page = vm.Page(
    title="Page with lots of extra information",
    components=[
        vm.Graph(id="scatter_chart", figure=px.scatter(df, x="sepal_length", y="petal_width", color="species")),
    ],
    controls=[
        vm.Filter(
            column="species",
            selector=vm.Dropdown(
                description="""
                    Select which species of iris you like.

                    [Click here](www.google.com) to learn more about flowers.""",
                # You could also do this with vm.Tooltip(text=...)
            ),
        ),
        vm.Filter(
            column="species",
            selector=vm.RadioItems(
                description="""
                    Select which species of iris you like.

                    [Click here](www.google.com) to learn more about flowers.""",
                # You could also do this with vm.Tooltip(text=...)
            ),
        ),
        vm.Filter(
            column="sepal_length",
            selector=vm.RangeSlider(
                description="""
                    Select which species of iris you like.

                    [Click here](www.google.com) to learn more about flowers.""",
                # You could also do this with vm.Tooltip(text=...)
            ),
        ),
        vm.Filter(
            column="species",
            selector=vm.Checklist(
                description="""
                    Select which species of iris you like.

                    [Click here](www.google.com) to learn more about flowers.""",
                # You could also do this with vm.Tooltip(text=...)
            ),
        ),
    ],
)

dashboard = vm.Dashboard(
    pages=[page],
    title="blah blah blah",
)

if __name__ == "__main__":
    Vizro().build(dashboard).run()
