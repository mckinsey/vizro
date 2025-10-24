import vizro.plotly.express as px

tips = px.data.tips()

fig = px.box(tips, y="total_bill", x="day", color="day", custom_data=["sex"])
