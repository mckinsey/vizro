# A first dashboard

Thanks to the amazing work at [`py.cafe`](https://py.cafe/), there is no setup needed for your first dashboard. Simply head to [`py.cafe`](https://py.cafe/) and code to your hearts desire. You can paste any example in this documentation to get going.

The example below might be a good starting point - in order to edit the code powering that dashboard, simply follow the link below that dashboard.

<iframe src="https://py.cafe/embed/maxi.schulz/vizro-tutorial-first-dashboard" width="100%" height="600px"></iframe>


You are now ready to explore Vizro further, by working through the ["Explore Vizro" tutorial](explore-components.md) or by consulting the [how-to guides](../user-guides/dashboard.md).


## Testing

### Without embed

```{.python pycafe-link}
import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm

df = px.data.iris()

page = vm.Page(
    title="My first dashboard",
    components=[
        vm.Graph(id="scatter_chart", figure=px.scatter(df, x="sepal_length", y="petal_width", color="species")),
        vm.Graph(id="hist_chart", figure=px.histogram(df, x="sepal_width", color="species")),
    ],
    controls=[
        vm.Filter(column="species", selector=vm.Dropdown(value=["ALL"])),
    ],
)

dashboard = vm.Dashboard(pages=[page])

Vizro().build(dashboard).run()
```

### With embed

```{.python pycafe-embed pycafe-embed-style="border: 1px solid #e6e6e6; border-radius: 8px;" pycafe-embed-width="100%" pycafe-embed-height="400px" pycafe-embed-scale="0.5"}
import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm

df = px.data.iris()

page = vm.Page(
    title="My second dashboard",
    components=[
        vm.Graph(id="scatter_chart", figure=px.scatter(df, x="sepal_length", y="petal_width", color="species")),
        vm.Graph(id="hist_chart", figure=px.histogram(df, x="sepal_width", color="species")),
    ],
    controls=[
        vm.Filter(column="species", selector=vm.Dropdown(value=["ALL"])),
    ],
)

dashboard = vm.Dashboard(pages=[page])

Vizro().build(dashboard).run()
```

## In Code example tab

!!! example "First component"
    === "app.py"
        ```{.python pycafe-link}
        import vizro.plotly.express as px
        from vizro import Vizro
        import vizro.models as vm

        df = px.data.iris()

        page = vm.Page(
            title="My first dashboard",
            components=[
                vm.Graph(id="scatter_chart", figure=px.scatter(df, x="sepal_length", y="petal_width", color="species")),
                vm.Graph(id="hist_chart", figure=px.histogram(df, x="sepal_width", color="species")),
            ],
            controls=[
                vm.Filter(column="species", selector=vm.Dropdown(value=["ALL"])),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])

        Vizro().build(dashboard).run()
        ```
    === "Screenshot"
        ![Dashboard](https://py.cafe/preview/maxi.schulz/vizro-tutorial-explore-vizro-1)

    <!-- === "Live App"
        <iframe src="https://py.cafe/embed/maxi.schulz/vizro-tutorial-explore-vizro-1" width="100%" height="800px" border="0"></iframe> -->


## Test blacken

```python
def hello():
    print('hello world')
```
