import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

n = 3
m = 10

df = pd.DataFrame({"x": list(range(m)) * n, "z": [i for i in range(n) for _ in range(m)]})


dashboard = vm.Dashboard(
    pages=[
        vm.Page(
            title="My title",
            components=[vm.Graph(figure=px.bar(df, x="x"))],
            controls=[vm.Filter(column="z", selector=vm.RangeSlider(step=1))],
        )
    ]
)

Vizro().build(dashboard).run()
