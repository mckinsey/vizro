import vizro.plotly.express as px

iris = px.data.iris()

fig = px.parallel_coordinates(
    iris, color="species_id", dimensions=["sepal_width", "sepal_length", "petal_width", "petal_length"]
)
