import vizro.plotly.express as px

tips = px.data.tips()

fig = px.violin(tips, y="tip", x="day", color="day", box=True)
