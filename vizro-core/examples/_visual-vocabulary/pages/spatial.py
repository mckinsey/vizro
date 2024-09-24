"""Spatial charts."""

import vizro.models as vm
import vizro.plotly.express as px

from pages._pages_utils import PAGE_GRID, carshare, gapminder, make_code_clipboard_from_py_file

choropleth = vm.Page(
    title="Choropleth",
    path="spatial/choropleth",
    layout=vm.Layout(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""
            #### What is a choropleth map?

            A choropleth map is a map in which geographical areas are colored, shaded or patterned in relation to a
            specific data variable.

            &nbsp;

            #### When should I use it?

            Use a chloropleth map when you wish to show how a measurement varies across a geographic area, or to show
            variability or patterns within a region. Typically, you will blend one color into another, take a color
            shade from light to dark, or introduce patterns to depict the variation in the data.

            Be aware that it may be difficult for your audience to accurately read or compare values on the map
            depicted by color.

        """
        ),
        vm.Graph(
            figure=px.choropleth(
                gapminder.query("year == 2007"),
                locations="iso_alpha",
                color="lifeExp",
                hover_name="country",
            )
        ),
        make_code_clipboard_from_py_file("choropleth.py"),
    ],
)

dot_map = vm.Page(
    title="Dot map",
    path="spatial/dot-map",
    layout=vm.Layout(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""
            #### What is a dot map?

            A dot map, or scatter map, uses dots to represent the value of a specific variable at geographic locations.

            &nbsp;

            #### When should I use it?

            Use a dot map to visually display the distribution and concentration of data points across a geographic
            area. It's ideal for showing the frequency or density of an attribute, helping to identify patterns,
            clusters, or anomalies.

            Dot maps offer a clear visual impression of spatial distributions, but overlapping dots can make it hard to
            distinguish individual data points in dense areas. Consider adding opacity to your dots to improve clarity.
        """
        ),
        vm.Graph(
            figure=px.scatter_map(
                carshare,
                lat="centroid_lat",
                lon="centroid_lon",
                opacity=0.5,
                zoom=10,
            ),
        ),
        make_code_clipboard_from_py_file("dot_map.py"),
    ],
)

bubble_map = vm.Page(
    title="Bubble map",
    path="spatial/bubble-map",
    layout=vm.Layout(grid=PAGE_GRID),
    components=[
        vm.Card(
            text="""
            #### What is a bubble map?

            A bubble map uses bubbles of varying sizes to represent the value of a specific variable at geographic
            locations.

            &nbsp;

            #### When should I use it?

            Use a bubble map to show the distribution, concentration, and size of data points on a map.
            It's great for highlighting patterns, clusters, and anomalies.

            Bubble maps clearly display spatial distributions and magnitudes, but overlapping bubbles can obscure
            details in crowded areas. Adjust the opacity and size of your bubbles to enhance clarity.
        """
        ),
        vm.Graph(
            figure=px.scatter_map(
                carshare,
                lat="centroid_lat",
                lon="centroid_lon",
                size="car_hours",
                size_max=15,
                opacity=0.5,
                zoom=10,
            ),
        ),
        make_code_clipboard_from_py_file("bubble_map.py"),
    ],
)


pages = [choropleth, dot_map, bubble_map]