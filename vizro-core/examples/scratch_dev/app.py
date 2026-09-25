import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.themes import colors, palettes

df = px.data.iris()

# Automatically pair each category with a color from the qualitative palette (uncomment to use):
# species_colors = dict(zip(df["species"].unique(), palettes.qualitative))  # (1)

# Or pin each category to a specific Vizro color:
species_colors = {
    "setosa": colors.blue,  # (2)!
    "versicolor": colors.dark_purple,
    "virginica": colors.turquoise,
}

page = vm.Page(
    title="Consistent category colors",
    components=[
        vm.Graph(
            figure=px.scatter(
                df, x="sepal_length", y="petal_width", color="species", color_discrete_map=species_colors
            ),
        ),
        vm.Graph(
            figure=px.histogram(
                df[df["species"] != "setosa"],  # second chart omits setosa
                x="sepal_width",
                color="species",
                color_discrete_map=species_colors,
            ),
        ),
    ],
    controls=[vm.Filter(column="species")],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()