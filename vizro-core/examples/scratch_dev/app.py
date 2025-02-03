"""Dev app to try things out."""

import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
import pandas as pd
from urllib.request import urlopen
import json

with urlopen("https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json") as response:
    counties = json.load(response)


fips = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv", dtype={"fips": str})
us_cities = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/us-cities-top-1k.csv")
us_cities = us_cities.query("State in ['New York', 'Ohio']")
carshare = px.data.carshare()

page_one = vm.Page(
    title="Scatter map",
    components=[
        vm.Graph(
            figure=px.scatter_map(
                carshare,
                lat="centroid_lat",
                lon="centroid_lon",
                color="peak_hour",
                size="car_hours",
                color_continuous_scale=px.colors.cyclical.IceFire,
                size_max=15,
                zoom=10,
            )
        ),
    ],
)


page_two = vm.Page(
    title="Line map",
    components=[
        vm.Graph(figure=px.line_map(us_cities, lat="lat", lon="lon", color="State", zoom=3, height=300)),
    ],
)


page_three = vm.Page(
    title="Choropleth Map",
    components=[
        vm.Graph(
            figure=px.choropleth_map(
                fips,
                geojson=counties,
                locations="fips",
                color="unemp",
                color_continuous_scale="Viridis",
                range_color=(0, 12),
                map_style="carto-positron",
                zoom=3,
                center={"lat": 37.0902, "lon": -95.7129},
                opacity=0.5,
                labels={"unemp": "unemployment rate"},
            )
        ),
    ],
)

page_four = vm.Page(
    title="Density map",
    components=[
        vm.Graph(
            figure=px.density_map(
                carshare,
                lat="centroid_lat",
                lon="centroid_lon",
            )
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page_one, page_two, page_three, page_four])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
