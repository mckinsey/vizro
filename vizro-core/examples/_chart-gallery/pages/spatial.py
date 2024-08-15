"""Spatial charts."""

import vizro.models as vm
import vizro.plotly.express as px

from pages._pages_utils import PAGE_GRID, gapminder, make_code_clipboard_from_py_file

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

pages = [choropleth]
