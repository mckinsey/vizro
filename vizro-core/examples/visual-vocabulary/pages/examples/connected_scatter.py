import vizro.plotly.express as px

gapminder = px.data.gapminder().query("country == 'Australia'")

fig = px.line(gapminder, x="year", y="lifeExp", markers=True)
