import vizro.plotly.express as px

tips = px.data.tips()

fig = px.histogram(tips, y="sex", x="total_bill", color="day", orientation="h")
