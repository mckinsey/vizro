import vizro.plotly.express as px

gapminder = (
    px.data.gapminder()
    .query("year == 2007 and country.isin(['United States', 'Pakistan', 'India', 'China', 'Indonesia'])")
    .sort_values("pop")
)

fig = px.bar(gapminder, x="pop", y="country", orientation="h")
