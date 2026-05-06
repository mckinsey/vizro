import vizro.plotly.express as px

tips = px.data.tips()

fig = px.pie(tips, values="tip", names="day", hole=0.7)
fig.update_layout(title="Arc Chart")
