import vizro.plotly.express as px

gapminder = px.data.gapminder().query("year == 2007")

fig = px.choropleth(gapminder, locations="iso_alpha", color="lifeExp", hover_name="country")
