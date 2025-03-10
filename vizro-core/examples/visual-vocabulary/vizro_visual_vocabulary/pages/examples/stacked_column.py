import vizro.plotly.express as px

tips = px.data.tips()

fig = px.histogram(tips, x="sex", y="total_bill", color="day")
