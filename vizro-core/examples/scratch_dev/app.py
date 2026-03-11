"""Dev app to try things out."""

import vizro.models as vm
import vizro.plotly.express as px

from vizro import Vizro

df = px.data.iris()

page = vm.Page(
    title="Card with code snippet",
    components=[
        vm.Card(
            text="""

Block code snippet:
```python

import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm

df = px.data.iris()

page = vm.Page(
    title="My first dashboard",
    components=[
        vm.Graph(figure=px.histogram(df, x="sepal_width", color="species"))],
    controls=[
        vm.Filter(column="species"),
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()

```"""
        )
    ],
)


dashboard = vm.Dashboard(
    pages=[page],
    title="QB",
)

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
