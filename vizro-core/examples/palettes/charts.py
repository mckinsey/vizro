from dataclasses import dataclass

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import vizro.plotly.express as px
from vizro.models.types import capture

tips = px.data.tips()
iris = px.data.iris()
gapminder_full = px.data.gapminder()
gapminder = gapminder_full.query("year == 2007")
gapminder_continent = gapminder_full.groupby(["year", "continent"])["pop"].sum().reset_index()
gapminder_oceania = gapminder_full.query("continent=='Oceania'")
gapminder_brazil = gapminder_full.query("country=='Brazil'")
wind = px.data.wind()
election = px.data.election()
election_geojson = px.data.election_geojson()
carshare = px.data.carshare()
carshare["time_of_day"] = pd.cut(
    carshare["peak_hour"], bins=[-1, 6, 12, 18, 24], labels=["Night", "Morning", "Afternoon", "Evening"]
)
us_cities = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/us-cities-top-1k.csv").query(
    "State in ['New York', 'Ohio']"
)
earthquakes = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/earthquakes-23k.csv")
timeline_df = pd.DataFrame(
    {
        "Task": ["Job A", "Job B", "Job C"],
        "Start": ["2009-01-01", "2009-03-05", "2009-02-20"],
        "Finish": ["2009-02-28", "2009-04-15", "2009-05-30"],
        "Resource": ["Alex", "Alex", "Max"],
        "Completion_pct": [50, 25, 75],
    }
)
funnel_df = pd.DataFrame(
    {
        "number": [39, 27.4, 20.6, 11, 3, 52, 36, 18, 14, 5],
        "stage": ["Website visit", "Downloads", "Potential customers", "Requested price", "invoice sent"] * 2,
        "office": ["Montreal"] * 5 + ["Toronto"] * 5,
    }
)
funnel_area_df = pd.DataFrame(
    {"names": ["The 1st", "The 2nd", "The 3rd", "The 4th", "The 5th"], "values": [5, 4, 3, 2, 1]}
)


@capture("graph")
def choropleth_tweaked(data_frame, **kwargs):
    """Custom outline-based choropleth map with layout tweaks."""
    fig = px.choropleth(data_frame=data_frame, **kwargs)
    fig.update_geos(fitbounds="locations", visible=False)
    return fig


@dataclass
class ChartType:
    px_function: str
    title: str
    trace_type: str
    discrete_figure: go.Figure | None = None
    continuous_figure: go.Figure | None = None
    extra_notes: str = ""

    def __post_init__(self):
        """Apply colorscale translation to continuous_figure if it exists.
        
        The Parameter sends string colorscale names like "sequential colorscale" instead of actual colorscale tuples
        because even a custom RadioItems cannot override Pydantic validation for `value` and `options` easily. So we translate them to actual colorscale tuples here.
        """
        if self.continuous_figure is not None:
            original_figure = self.continuous_figure

            @capture("graph")
            def wrapped_figure(data_frame, **kwargs):
                # data_frame is not used, but required by the @capture decorator.
                if "color_continuous_scale" in kwargs:
                    # Doesn't matter whether we look at vizro_light or vizro_dark, because the colorscales are the same.
                    template_colorscales = pio.templates["vizro_light"].layout.colorscale
                    colorscales_map = {
                        "sequential colorscale": template_colorscales.sequential,
                        "diverging colorscale": template_colorscales.diverging,
                        "sequentialminus colorscale": template_colorscales.sequentialminus,
                    }
                    kwargs["color_continuous_scale"] = colorscales_map[kwargs["color_continuous_scale"]]
                # Very hacky, don't repeat this pattern elsewhere...
                return original_figure._captured_callable(**kwargs)

            self.continuous_figure = wrapped_figure(data_frame=pd.DataFrame())


CHARTS_BY_CATEGORY = {
    "Basic": [
        ChartType(
            px_function="px.bar",
            title="Bar",
            trace_type="go.Bar",
            discrete_figure=px.bar(gapminder_oceania, x="year", y="pop", color="country"),
            continuous_figure=px.bar(gapminder_brazil, x="year", y="pop", color="lifeExp"),
        ),
        ChartType(
            px_function="px.scatter",
            title="Scatter",
            trace_type="go.Scatter",
            discrete_figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="species"),
            continuous_figure=px.scatter(iris, x="sepal_width", y="sepal_length", color="petal_length"),
        ),
        ChartType(
            px_function="px.line",
            title="Line",
            trace_type="go.Scatter",
            discrete_figure=px.line(gapminder_oceania, x="year", y="lifeExp", color="country"),
        ),
        ChartType(
            px_function="px.area",
            title="Area",
            trace_type="go.Scatter",
            discrete_figure=px.area(gapminder_continent, x="year", y="pop", color="continent"),
        ),
    ],
    "Distribution": [
        ChartType(
            px_function="px.histogram",
            title="Histogram",
            trace_type="go.Histogram",
            discrete_figure=px.histogram(tips, x="total_bill", color="smoker"),
        ),
        ChartType(
            px_function="px.box",
            title="Box",
            trace_type="go.Box",
            discrete_figure=px.box(tips, x="day", y="total_bill", color="smoker"),
        ),
        ChartType(
            px_function="px.violin",
            title="Violin",
            trace_type="go.Violin",
            discrete_figure=px.violin(tips, x="day", y="total_bill", color="smoker"),
        ),
        ChartType(
            px_function="px.strip",
            title="Strip",
            trace_type="go.Box",
            discrete_figure=px.strip(tips, x="day", y="total_bill", color="smoker"),
        ),
    ],
    "Hierarchical": [
        ChartType(
            px_function="px.pie",
            title="Pie",
            trace_type="go.Pie",
            discrete_figure=px.pie(tips, values="tip", names="day"),
        ),
        ChartType(
            px_function="px.sunburst",
            title="Sunburst",
            trace_type="go.Sunburst",
            discrete_figure=px.sunburst(tips, path=[px.Constant("all"), 'sex', 'day', 'time'], values="total_bill", color="day"),
            continuous_figure=px.sunburst(tips, path=[px.Constant("all"), 'sex', 'day', 'time'], values="total_bill", color="total_bill"),
        ),
        ChartType(
            px_function="px.treemap",
            title="Treemap",
            trace_type="go.Treemap",
            discrete_figure=px.treemap(tips, path=[px.Constant("all"), 'sex', 'day', 'time'], values="total_bill", color="day"),
            continuous_figure=px.treemap(tips, path=[px.Constant("all"), 'sex', 'day', 'time'], values="total_bill", color="total_bill"),
        ),
        ChartType(
            px_function="px.icicle",
            title="Icicle",
            trace_type="go.Icicle",
            discrete_figure=px.icicle(tips, path=[px.Constant("all"), 'sex', 'day', 'time'], values="total_bill", color="day"),
            continuous_figure=px.icicle(tips, path=[px.Constant("all"), 'sex', 'day', 'time'], values="total_bill", color="total_bill"),
        ),
        ChartType(
            px_function="px.funnel",
            title="Funnel",
            trace_type="go.Funnel",
            discrete_figure=px.funnel(funnel_df, x="number", y="stage", color="office"),
        ),
        ChartType(
            px_function="px.funnel_area",
            title="Funnel Area",
            trace_type="go.Funnelarea",
            discrete_figure=px.funnel_area(funnel_area_df, names="names", values="values"),
        ),
    ],
    "Maps": [
        ChartType(
            px_function="px.scatter_geo",
            title="Outline-based Scatter Map",
            trace_type="go.Scattergeo",
            discrete_figure=px.scatter_geo(
                gapminder, locations="iso_alpha", color="continent", size="pop", projection="natural earth"
            ),
            continuous_figure=px.scatter_geo(
                gapminder, locations="iso_alpha", color="lifeExp", size="pop", projection="natural earth"
            ),
        ),
        ChartType(
            px_function="px.line_geo",
            title="Outline-based Line Map",
            trace_type="go.Scattergeo",
            discrete_figure=px.line_geo(gapminder, locations="iso_alpha", color="continent", projection="orthographic"),
        ),
        ChartType(
            px_function="px.choropleth",
            title="Outline-based Choropleth Map",
            trace_type="go.Choropleth",
            discrete_figure=choropleth_tweaked(
                election,
                geojson=election_geojson,
                locations="district",
                featureidkey="properties.district",
                color="winner",
                projection="mercator"
            ),
            continuous_figure=choropleth_tweaked(
                election,
                geojson=election_geojson,
                locations="district",
                featureidkey="properties.district",
                color="Bergeron",
                projection="mercator"
            ),
        ),
        ChartType(
            px_function="px.scatter_map",
            title="Tile-based Scatter Map",
            trace_type="go.Scattermap",
            discrete_figure=px.scatter_map(
                carshare,
                lat="centroid_lat",
                lon="centroid_lon",
                color="time_of_day",
                size="car_hours",
                size_max=15,
                zoom=10
            ),
            continuous_figure=px.scatter_map(
                carshare,
                lat="centroid_lat",
                lon="centroid_lon",
                color="car_hours",
                size="car_hours",
                size_max=15,
                zoom=10
            ),
        ),
        ChartType(
            px_function="px.line_map",
            title="Tile-based Line Map",
            trace_type="go.Scattermap",
            discrete_figure=px.line_map(us_cities, lat="lat", lon="lon", color="State", zoom=4),
        ),
        ChartType(
            px_function="px.choropleth_map",
            title="Tile-based Choropleth Map",
            extra_notes="Works but can't get it to automatically zoom in on Montreal so you need to pan and zoom yourself.",
            trace_type="go.Choroplethmap",
            discrete_figure=px.choropleth_map(
                election,
                geojson=election_geojson,
                locations="district",
                featureidkey="properties.district",
                color="winner"
            ),
            continuous_figure=px.choropleth_map(
                election,
                geojson=election_geojson,
                locations="district",
                featureidkey="properties.district",
                color="Bergeron"
            ),
        ),
        ChartType(
            px_function="px.density_map",
            title="Tile-based Density Map",
            trace_type="go.Densitymap",
            continuous_figure=px.density_map(
                earthquakes,
                lat="Latitude",
                lon="Longitude",
                z="Magnitude",
                radius=10,
                center=dict(lat=0, lon=180),
                zoom=0,
                map_style="open-street-map"
            ),
        ),
    ],
    "Statistical": [
        ChartType(
            px_function="px.ecdf",
            title="ECDF",
            trace_type="go.Scatter",
            discrete_figure=px.ecdf(tips, x="total_bill", color="smoker"),
        ),
        ChartType(
            px_function="px.density_contour",
            title="Density Contour",
            trace_type="go.Histogram2dContour",
            discrete_figure=px.density_contour(iris, x="sepal_width", y="sepal_length", color="species"),
        ),
        ChartType(
            px_function="px.density_heatmap",
            title="Density Heatmap",
            trace_type="go.Histogram2d",
            continuous_figure=px.density_heatmap(iris, x="sepal_width", y="sepal_length", nbinsx=30, nbinsy=30),
        ),
        ChartType(
            px_function="px.scatter_matrix",
            title="Scatter Matrix",
            trace_type="go.Splom",
            discrete_figure=px.scatter_matrix(iris, dimensions=["sepal_width", "sepal_length", "petal_width"], color="species"),
            continuous_figure=px.scatter_matrix(iris, dimensions=["sepal_width", "sepal_length", "petal_width"], color="petal_length"),
        ),
    ],
    "Specialised": [
        ChartType(
            px_function="px.timeline",
            title="Timeline",
            trace_type="go.Bar",
            discrete_figure=px.timeline(timeline_df, x_start="Start", x_end="Finish", y="Task", color="Resource"),
            continuous_figure=px.timeline(timeline_df, x_start="Start", x_end="Finish", y="Task", color="Completion_pct"),
        ),
        ChartType(
            px_function="px.parallel_coordinates",
            title="Parallel Coordinates",
            trace_type="go.Parcoords",
            continuous_figure=px.parallel_coordinates(iris, color="species_id"),
        ),
        ChartType(
            px_function="px.parallel_categories",
            title="Parallel Categories",
            trace_type="go.Parcats",
            continuous_figure=px.parallel_categories(tips, dimensions=["sex", "smoker", "day"], color="size"),
        ),
        ChartType(
            px_function="px.scatter_3d",
            title="Scatter 3D",
            trace_type="go.Scatter3d",
            discrete_figure=px.scatter_3d(iris, x="sepal_length", y="sepal_width", z="petal_width", color="species"),
            continuous_figure=px.scatter_3d(iris, x="sepal_length", y="sepal_width", z="petal_width", color="petal_length"),
        ),
        ChartType(
            px_function="px.line_3d",
            title="Line 3D",
            trace_type="go.Scatter3d",
            discrete_figure=px.line_3d(gapminder_oceania, x="gdpPercap", y="pop", z="year", color="country"),
        ),
        ChartType(
            px_function="px.scatter_polar",
            title="Scatter Polar",
            trace_type="go.Scatterpolar",
            discrete_figure=px.scatter_polar(wind, r="frequency", theta="direction", color="strength"),
            continuous_figure=px.scatter_polar(wind, r="frequency", theta="direction", color="frequency"),
        ),
        ChartType(
            px_function="px.line_polar",
            title="Line Polar",
            trace_type="go.Scatterpolar",
            discrete_figure=px.line_polar(wind, r="frequency", theta="direction", color="strength", line_close=True),
        ),
        ChartType(
            px_function="px.bar_polar",
            title="Bar Polar",
            trace_type="go.Barpolar",
            discrete_figure=px.bar_polar(wind, r="frequency", theta="direction", color="strength"),
            continuous_figure=px.bar_polar(wind, r="frequency", theta="direction", color="frequency"),
        ),
        ChartType(
            px_function="px.scatter_ternary",
            title="Scatter Ternary",
            trace_type="go.Scatterternary",
            discrete_figure=px.scatter_ternary(election, a="Joly", b="Coderre", c="Bergeron", color="winner"),
            continuous_figure=px.scatter_ternary(election, a="Joly", b="Coderre", c="Bergeron", color="Joly"),
        ),
        ChartType(
            px_function="px.line_ternary",
            title="Line Ternary",
            trace_type="go.Scatterternary",
            discrete_figure=px.line_ternary(election, a="Joly", b="Coderre", c="Bergeron", color="winner"),
        ),
    ],
}
