import vizro.plotly.express as px

tips = px.data.tips()

fig = px.pie(tips, values="tip", names="day")
