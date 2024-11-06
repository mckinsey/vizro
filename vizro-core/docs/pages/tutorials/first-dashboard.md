# A first dashboard

There is no setup needed for your first dashboard, thanks to the amazing [PyCafe](https://py.cafe/).

Click on the **Run and edit this code in PyCafe** link below to live-edit the dashboard.

!!! example "First dashboard"
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

    === "Result"

        [![FirstDash]][FirstDash]

    [FirstDash]: ../../assets/tutorials/dashboard/first-dashboard.png

<!-- vale off -->
## Can I break this code?
<!-- vale on -->
When you click the link to "Edit live on PyCafe" the dashboard is running inside your browser. Any changes you make are local and you don't need to worry about breaking the code for others. Nobody else sees the changes you make unless you save a copy of the project as your own Vizro PyCafe project.

<!-- vale off -->
## How can I make my own dashboards?
<!-- vale on -->
You can use PyCafe to experiment with your own Vizro dashboards by dropping code onto a new project. Check out the [PyCafe documentation](https://py.cafe/docs/apps/vizro) for more information.

If you need inspiration or a starting point, we make all our examples available for you to try out on PyCafe. Throughout our documentation, follow the "**Run and edit this code in PyCafe**" link below the code snippets to open them in PyCafe.

## Where next?
You are now ready to explore Vizro further, by working through the ["Explore Vizro" tutorial](explore-components.md) or by consulting the [how-to guides](../user-guides/dashboard.md).
