"""Simple Vizro app demonstrating palettes."""

from dataclasses import dataclass
from typing import Optional
import pandas as pd
import plotly.graph_objects as go
import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm

# Prepare data
tips = px.data.tips()
iris = px.data.iris()
gapminder_full = px.data.gapminder()
gapminder = gapminder_full.query("year == 2007")
gapminder_continent = gapminder_full.groupby(['year', 'continent'])['pop'].sum().reset_index()
gapminder_continent_lifeexp = gapminder_full.groupby(['year', 'continent'])['lifeExp'].mean().reset_index()
gapminder_oceania = gapminder_full.query("continent=='Oceania'")
gapminder_brazil_argentina_chile = gapminder_full.query("country in ['Brazil', 'Argentina', 'Chile']")
gapminder_brazil = gapminder_full.query("country=='Brazil'")
wind = px.data.wind()
election = px.data.election()
election_geojson = px.data.election_geojson()
carshare = px.data.carshare()
carshare["time_of_day"] = pd.cut(carshare["peak_hour"], bins=[-1, 6, 12, 18, 24], labels=["Night", "Morning", "Afternoon", "Evening"])
us_cities = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/us-cities-top-1k.csv").query("State in ['New York', 'Ohio']")
earthquakes = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/earthquakes-23k.csv')

timeline_discrete_df = pd.DataFrame([
    dict(Task="Job A", Start='2009-01-01', Finish='2009-02-28', Resource="Alex"),
    dict(Task="Job B", Start='2009-03-05', Finish='2009-04-15', Resource="Alex"),
    dict(Task="Job C", Start='2009-02-20', Finish='2009-05-30', Resource="Max")
])
timeline_continuous_df = pd.DataFrame([
    dict(Task="Job A", Start='2009-01-01', Finish='2009-02-28', Completion_pct=50),
    dict(Task="Job B", Start='2009-03-05', Finish='2009-04-15', Completion_pct=25),
    dict(Task="Job C", Start='2009-02-20', Finish='2009-05-30', Completion_pct=75)
])

funnel_montreal_df = pd.DataFrame(dict(
    number=[39, 27.4, 20.6, 11, 3],
    stage=["Website visit", "Downloads", "Potential customers", "Requested price", "invoice sent"],
    office=['Montreal']*5
))
funnel_toronto_df = pd.DataFrame(dict(
    number=[52, 36, 18, 14, 5],
    stage=["Website visit", "Downloads", "Potential customers", "Requested price", "invoice sent"],
    office=['Toronto']*5
))
funnel_df = pd.concat([funnel_montreal_df, funnel_toronto_df], axis=0)
funnel_area_df = pd.DataFrame(dict(
    names=["The 1st", "The 2nd", "The 3rd", "The 4th", "The 5th"],
    values=[5, 4, 3, 2, 1]
))


@dataclass
class ChartExample:
    """Dataclass representing a chart example with discrete and continuous figures."""
    trace_type: str
    title: str
    px_function: str
    discrete_figure: Optional[go.Figure] = None
    continuous_figure: Optional[go.Figure] = None


# Create the dictionary structure grouped by category
charts_by_category = {
    "Basic Charts": [
        ChartExample(
            trace_type="bar",
            title="Bar",
            px_function="px.bar",
            discrete_figure=px.bar(gapminder_oceania, x="year", y="pop", hover_data=["lifeExp", "gdpPercap"], color="country", labels={"pop": "population of Oceania"}, height=400),
            continuous_figure=px.bar(gapminder_brazil, x="year", y="pop", hover_data=["lifeExp", "gdpPercap"], color="lifeExp", labels={"pop": "population of Brazil"}, height=400),
        ),
        ChartExample(
            trace_type="scatter",
            title="Scatter",
            px_function="px.scatter",
            discrete_figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species"),
            continuous_figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="petal_length"),
        ),
        ChartExample(
            trace_type="scatter",
            title="Line",
            px_function="px.line",
            discrete_figure=px.line(gapminder_oceania, x="year", y="lifeExp", color="country"),
        ),
        ChartExample(
            trace_type="scatter",
            title="Area",
            px_function="px.area",
            discrete_figure=px.area(gapminder_continent, x="year", y="pop", color="continent"),
        ),
    ],
    "Distribution": [
        ChartExample(
            trace_type="histogram",
            title="Histogram",
            px_function="px.histogram",
            discrete_figure=px.histogram(tips, x="total_bill", color="sex"),
        ),
        ChartExample(
            trace_type="box",
            title="Box",
            px_function="px.box",
            discrete_figure=px.box(tips, x="day", y="total_bill", color="smoker", notched=True),
        ),
        ChartExample(
            trace_type="violin",
            title="Violin",
            px_function="px.violin",
            discrete_figure=px.violin(tips, x="day", y="total_bill", color="smoker", box=True),
        ),
        ChartExample(
            trace_type="box",
            title="Strip",
            px_function="px.strip",
            discrete_figure=px.strip(tips, x="day", y="total_bill", color="smoker"),
        ),
    ],
    "Hierarchical": [
        ChartExample(
            trace_type="pie",
            title="Pie",
            px_function="px.pie",
            discrete_figure=px.pie(tips, values="tip", names="day"),
        ),
        ChartExample(
            trace_type="sunburst",
            title="Sunburst",
            px_function="px.sunburst",
            discrete_figure=px.sunburst(tips, path=[px.Constant("all"), 'sex', 'day', 'time'], values="total_bill", color="day"),
            continuous_figure=px.sunburst(tips, path=[px.Constant("all"), 'sex', 'day', 'time'], values="total_bill", color="total_bill"),
        ),
        ChartExample(
            trace_type="treemap",
            title="Treemap",
            px_function="px.treemap",
            discrete_figure=px.treemap(tips, path=[px.Constant("all"), 'sex', 'day', 'time'], values="total_bill", color="day"),
            continuous_figure=px.treemap(tips, path=[px.Constant("all"), 'sex', 'day', 'time'], values="total_bill", color="total_bill"),
        ),
        ChartExample(
            trace_type="icicle",
            title="Icicle",
            px_function="px.icicle",
            discrete_figure=px.icicle(tips, path=[px.Constant("all"), 'sex', 'day', 'time'], values="total_bill", color="day"),
            continuous_figure=px.icicle(tips, path=[px.Constant("all"), 'sex', 'day', 'time'], values="total_bill", color="total_bill"),
        ),
        ChartExample(
            trace_type="funnel",
            title="Funnel",
            px_function="px.funnel",
            discrete_figure=px.funnel(
                funnel_df,
                x="number",
                y="stage",
                color="office"
            ),
        ),
        ChartExample(
            trace_type="funnelarea",
            title="Funnel Area",
            px_function="px.funnel_area",
            discrete_figure=px.funnel_area(funnel_area_df, names="names", values="values"),
        ),
    ],
    "Statistical": [
        ChartExample(
            trace_type="scatter",
            title="ECDF",
            px_function="px.ecdf",
            discrete_figure=px.ecdf(tips, x="total_bill", color="sex"),
        ),
        ChartExample(
            trace_type="histogram2dcontour",
            title="Density Contour",
            px_function="px.density_contour",
            discrete_figure=px.density_contour(iris, x="sepal_width", y="sepal_length", color="species"),
        ),
        ChartExample(
            trace_type="histogram2d",
            title="Density Heatmap",
            px_function="px.density_heatmap",
            continuous_figure=px.density_heatmap(iris, x="sepal_width", y="sepal_length", nbinsx=30, nbinsy=30),
        ),
        ChartExample(
            trace_type="splom",
            title="Scatter Matrix",
            px_function="px.scatter_matrix",
            discrete_figure=px.scatter_matrix(iris, dimensions=["sepal_width", "sepal_length", "petal_width", "petal_length"], color="species"),
            continuous_figure=px.scatter_matrix(iris, dimensions=["sepal_width", "sepal_length", "petal_width", "petal_length"], color="petal_length"),
        ),
    ],
    "Maps": [
        ChartExample(
            trace_type="scattergeo",
            title="Scatter Geo (Outline-based)",
            px_function="px.scatter_geo",
            discrete_figure=px.scatter_geo(gapminder, locations="iso_alpha", color="continent", hover_name="country", size="pop", projection="natural earth"),
            continuous_figure=px.scatter_geo(gapminder, locations="iso_alpha", color="lifeExp", hover_name="country", size="pop", projection="natural earth"),
        ),
        ChartExample(
            trace_type="scattergeo",
            title="Line Geo (Outline-based)",
            px_function="px.line_geo",
            discrete_figure=px.line_geo(gapminder, locations="iso_alpha", color="continent", projection="orthographic"),
        ),
        ChartExample(
            trace_type="choropleth",
            title="Choropleth (Outline-based)",
            px_function="px.choropleth",
            discrete_figure=px.choropleth(election, geojson=election_geojson, locations="district", featureidkey="properties.district", color="winner", projection="mercator"),
            continuous_figure=px.choropleth(election, geojson=election_geojson, locations="district", featureidkey="properties.district", color="Bergeron", projection="mercator"),
        ),
        ChartExample(
            trace_type="scattermap",
            title="Scatter Map (Tile-based)",
            px_function="px.scatter_map",
            discrete_figure=px.scatter_map(carshare, lat="centroid_lat", lon="centroid_lon", color="time_of_day", size="car_hours", size_max=15, zoom=10),
            continuous_figure=px.scatter_map(carshare, lat="centroid_lat", lon="centroid_lon", color="car_hours", size="car_hours", size_max=15, zoom=10),
        ),
        ChartExample(
            trace_type="scattermap",
            title="Line Map (Tile-based)",
            px_function="px.line_map",
            discrete_figure=px.line_map(us_cities, lat="lat", lon="lon", color="State", zoom=3, height=300),
        ),
        ChartExample(
            trace_type="choroplethmap",
            title="Choropleth Map (Tile-based)",
            px_function="px.choropleth_map",
            discrete_figure=px.choropleth_map(election, geojson=election_geojson, locations="district", featureidkey="properties.district", color="winner"),
            continuous_figure=px.choropleth_map(election, geojson=election_geojson, locations="district", featureidkey="properties.district", color="Bergeron"),
        ),
        ChartExample(
            trace_type="densitymap",
            title="Density Map (Tile-based)",
            px_function="px.density_map",
            continuous_figure=px.density_map(earthquakes, lat="Latitude", lon="Longitude", z="Magnitude", radius=10, center=dict(lat=0, lon=180), zoom=0, map_style="open-street-map"),
        ),
    ],
    "Specialised": [
        ChartExample(
            trace_type="scatterpolar",
            title="Scatter Polar",
            px_function="px.scatter_polar",
            discrete_figure=px.scatter_polar(wind, r="frequency", theta="direction", color="strength", symbol="strength"),
            continuous_figure=px.scatter_polar(wind, r="frequency", theta="direction", color="frequency"),
        ),
        ChartExample(
            trace_type="scatterpolar",
            title="Line Polar",
            px_function="px.line_polar",
            discrete_figure=px.line_polar(wind, r="frequency", theta="direction", color="strength", line_close=True),
        ),
        ChartExample(
            trace_type="barpolar",
            title="Bar Polar",
            px_function="px.bar_polar",
            discrete_figure=px.bar_polar(wind, r="frequency", theta="direction", color="strength"),
            continuous_figure=px.bar_polar(wind, r="frequency", theta="direction", color="frequency"),
        ),
        ChartExample(
            trace_type="scatter3d",
            title="Scatter 3D",
            px_function="px.scatter_3d",
            discrete_figure=px.scatter_3d(iris, x="sepal_length", y="sepal_width", z="petal_width", color="species"),
            continuous_figure=px.scatter_3d(iris, x="sepal_length", y="sepal_width", z="petal_width", color="petal_length"),
        ),
        ChartExample(
            trace_type="scatter3d",
            title="Line 3D",
            px_function="px.line_3d",
            discrete_figure=px.line_3d(gapminder_brazil_argentina_chile, x="gdpPercap", y="pop", z="year", color="country"),
        ),
        ChartExample(
            trace_type="scatterternary",
            title="Scatter Ternary",
            px_function="px.scatter_ternary",
            discrete_figure=px.scatter_ternary(election, a="Joly", b="Coderre", c="Bergeron", hover_name="district", color="winner", size="total", size_max=15),
            continuous_figure=px.scatter_ternary(election, a="Joly", b="Coderre", c="Bergeron", color="Joly"),
        ),
        ChartExample(
            trace_type="scatterternary",
            title="Line Ternary",
            px_function="px.line_ternary",
            discrete_figure=px.line_ternary(election, a="Joly", b="Coderre", c="Bergeron", color="winner"),
        ),
        ChartExample(
            trace_type="parcoords",
            title="Parallel Coordinates",
            px_function="px.parallel_coordinates",
            continuous_figure=px.parallel_coordinates(iris, color="species_id"),
        ),
        ChartExample(
            trace_type="parcats",
            title="Parallel Categories",
            px_function="px.parallel_categories",
            continuous_figure=px.parallel_categories(tips, dimensions=["sex", "smoker", "day"], color="size"),
        ),
        ChartExample(
            trace_type="bar",
            title="Timeline",
            px_function="px.timeline",
            discrete_figure=px.timeline(
                timeline_discrete_df,
                x_start="Start",
                x_end="Finish",
                y="Task",
                color="Resource"
            ),
            continuous_figure=px.timeline(
                timeline_continuous_df,
                x_start="Start",
                x_end="Finish",
                y="Task",
                color="Completion_pct"
            ),
        ),
    ],
}

# Create containers for each category
containers = []
for category, charts in charts_by_category.items():
    components = []
    grid = []
    graph_index = 0
    
    for chart_example in charts:
        description = f"**Trace type:** `{chart_example.trace_type}`  \n**Plotly Express function:** `{chart_example.px_function}`"
        
        row = []
        for figure, suffix in [(chart_example.discrete_figure, "Discrete"), (chart_example.continuous_figure, "Continuous")]:
            if figure is not None:
                components.append(
                    vm.Graph(
                        title=f"{chart_example.title} ({suffix})",
                        figure=figure,
                        description=description,
                    )
                )
                row.append(graph_index)
                graph_index += 1
            else:
                row.append(-1)
        
        grid.append(row)
    
    containers.append(
        vm.Container(
            title=category,
            layout=vm.Grid(grid=grid),
            components=components,
            variant="outlined"
        )
    )

page = vm.Page(
    title="Palettes Demo",
    layout=vm.Flex(),
    components=[
        vm.Tabs(tabs=containers)
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
