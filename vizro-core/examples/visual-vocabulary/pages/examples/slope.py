import pandas as pd
import vizro.plotly.express as px

gapminder_2007 = px.data.gapminder().query("year == 2007")
gapminder_1952 = px.data.gapminder().query("year == 1952")

data = pd.merge(
    gapminder_1952[["country", "lifeExp"]].rename(columns={"lifeExp": "1952"}),
    gapminder_2007[["country", "lifeExp"]].rename(columns={"lifeExp": "2007"}),
    on="country",
)
data = data[data["1952"] > 30].sort_values("2007")
data["change"] = data["2007"] - data["1952"]
data = data.nlargest(10, "change")

data_long = data.melt(id_vars=["country"], var_name="year", value_name="life_exp")

fig = px.line(
    data_long,
    x="year",
    y="life_exp",
    color="country",
    markers=True,
    title="Life expectancy: 1952 vs 2007",
)
fig.update_yaxes(title="Life expectancy (years)")
