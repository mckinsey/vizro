import vizro.plotly.express as px

tips = px.data.tips()

fig = px.strip(tips, x="day", y="total_bill", color="day")
