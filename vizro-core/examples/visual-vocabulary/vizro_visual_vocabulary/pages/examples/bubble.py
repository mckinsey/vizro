import vizro.plotly.express as px

gapminder = px.data.gapminder().query("year==2007")

fig = px.scatter(gapminder, x="gdpPercap", y="lifeExp", size="pop", size_max=60)
