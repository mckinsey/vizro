import vizro.plotly.express as px
from vizro.models.types import capture


@capture("graph")
def bar_with_highlight(data_frame, x, highlight_bar=None):
    """Custom chart to test using DatePicker with Parameter."""
    fig = px.bar(data_frame=data_frame, x=x)
    fig["data"][0]["marker"]["color"] = ["orange" if c == highlight_bar else "blue" for c in fig["data"][0]["x"]]
    return fig
