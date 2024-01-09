from vizro import Vizro
import vizro.models as vm
import vizro.plotly.express as px

df = px.data.gapminder()
gapminder_data = (
    df.groupby(by=["continent", "year"]).
        agg({"lifeExp": "mean", "pop": "sum", "gdpPercap": "mean"}).reset_index()
)

first_page = vm.Page(
    title="First Page",
    components=[
        vm.Graph(
            id="box_cont",
            figure=px.box(gapminder_data, x="continent", y="lifeExp", color="continent",
                          labels={"lifeExp": "Life Expectancy", "continent": "Continent"}),
        ),
    ],
)

dashboard = vm.Dashboard(pages=[first_page])
Vizro().build(dashboard).run()
