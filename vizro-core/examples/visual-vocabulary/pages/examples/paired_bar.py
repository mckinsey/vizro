import vizro.plotly.express as px

tips = px.data.tips()

fig = px.histogram(
    tips,
    y="day",
    x="total_bill",
    color="sex",
    barmode="group",
    orientation="h",
    category_orders={"day": ["Thur", "Fri", "Sat", "Sun"]},
)
