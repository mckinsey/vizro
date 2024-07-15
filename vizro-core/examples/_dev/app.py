"""Dev app to try things out."""

import json
from urllib.request import urlopen

import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

with urlopen(
    "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
) as response:
    counties = json.load(response)

fips_unemp = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv",
    dtype={"fips": str},
)


page = vm.Page(
    title="Choropleth",
    components=[
        vm.Graph(
            figure=px.choropleth(
                fips_unemp,
                geojson=counties,
                locations="fips",
                color="unemp",
                range_color=(0, 12),
                scope="usa",
            )
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
