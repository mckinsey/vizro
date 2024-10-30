import vizro.plotly.express as px

tips = px.data.tips()

fig = px.violin(tips, y="total_bill", x="day", color="day", box=True)
