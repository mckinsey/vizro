import vizro.plotly.express as px

tips = px.data.tips()

fig = px.histogram(tips, x="total_bill")
