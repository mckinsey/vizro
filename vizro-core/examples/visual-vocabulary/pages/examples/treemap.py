import vizro.plotly.express as px

gapminder = px.data.gapminder().query("year == 2007")

fig = px.treemap(gapminder, path=[px.Constant("world"), "continent", "country"], values="pop", color="lifeExp")
