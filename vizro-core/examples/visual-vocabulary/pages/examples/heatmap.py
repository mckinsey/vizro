import vizro.plotly.express as px

tips = px.data.tips()

fig = px.density_heatmap(tips, x="day", y="size", z="tip", histfunc="avg", text_auto="$.2f")
