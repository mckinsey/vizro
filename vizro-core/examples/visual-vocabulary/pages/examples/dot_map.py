import vizro.plotly.express as px

carshare = px.data.carshare()

fig = px.scatter_map(carshare, lat="centroid_lat", lon="centroid_lon", opacity=0.5, zoom=10)
