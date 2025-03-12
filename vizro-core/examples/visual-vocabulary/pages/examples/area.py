import vizro.plotly.express as px

stocks = px.data.stocks()

fig = px.area(stocks, x="date", y="GOOG")
