import vizro.plotly.express as px

gapminder = px.data.gapminder()

fig = px.treemap(
    gapminder.query("year == 2007"), path=[px.Constant("world"), "continent", "country"], values="pop", color="lifeExp"
)
