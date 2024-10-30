import vizro.plotly.express as px

stocks = px.data.stocks()

fig = px.line(stocks, x="date", y="GOOG")
