import vizro.plotly.express as px

tips = px.data.tips()

fig = px.histogram(
    tips, x="day", y="total_bill", color="sex", barmode="group", category_orders={"day": ["Thur", "Fri", "Sat", "Sun"]}
)
