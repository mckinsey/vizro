import vizro.plotly.express as px

# Need to have a string name here, otherwise it displays the other years
X = {1952: "Y1952", 2007: "Y2007"}
COUNTRIES = "Japan", "Norway", "Korea, Rep.", "United States", "China", "Brazil", "India"

gm = px.data.gapminder()
df = gm.loc[gm["year"].isin(X) & gm["country"].isin(COUNTRIES), ["country", "year", "lifeExp"]]
df["x"] = df["year"].map(X)

fig = px.line(df, x="x", y="lifeExp", color="country", markers=True)
