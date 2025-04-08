"""Scratchpad for testing."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

tips = px.data.tips()

page1 = vm.Page(
    title="Default",
    layout=vm.Layout(grid=[[1, 2], [0, 0]]),
    components=[
        vm.Card(text="""# Good morning!"""),
        vm.Graph(
            title="Where do we get more tips?",
            figure=px.bar(tips, y="tip", x="day"),
        ),
        vm.Graph(
            title="Is the average driven by a few outliers?",
            figure=px.violin(tips, y="tip", x="day", color="day", box=True),
        ),
    ],
    controls=[vm.Filter(column="day")],
)


dashboard = vm.Dashboard(pages=[page1])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
