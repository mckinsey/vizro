import vizro.plotly.express as px

iris = px.data.iris()

fig = px.scatter_matrix(iris, dimensions=["sepal_length", "sepal_width", "petal_length", "petal_width"])
