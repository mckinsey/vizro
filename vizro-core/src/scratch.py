# API for Table/React Charts
import d3_bar_chart
from dash import dash_table

import vizro.models as vm
from vizro.models.types import capture


# Dash Table
@capture("graph")
def dash_table(data_frame=None, **kwargs):
    """Custom table."""
    return dash_table.DataTable(
        data=data_frame.to_dict("records"), columns=[{"name": i, "id": i} for i in data_frame.columns], **kwargs
    )


# D3 Visualisation
@capture("graph")
def d3_bar_chart(data_frame=None):
    """Custom table."""
    return d3_bar_chart.D3BarChart(
        data_frame=data_frame,  # Custom D3 charts should have data_frame or other data arg
        id="input",
        value="my-value",
        label="my-label",
    )


# 1) Graph ---------------------
vm.Graph(figure=dash_table)
vm.Graph(figure=d3_bar_chart)

"""
Pro:
- One wrapper for all charts

Con:
- Returning different object based on figure -> dcc.Graph or html.Div
- Would contradict our current paradigm of naming models close to what is being used underneath

To consider
- dash keeps Graph and Table separate as well -> Graph enables all plotly.js powered charts, Table has different figure json schema and is therefore separate
- clickEvent property differs from the rest of px.charts --> needs to be refactored out of Graph
- post update calls differ (e.g. update_layout not available) --> needs to be refactored out of Graph
"""


# 2) Table & React --------------------
vm.Table2(data_frame, **kwargs)
vm.React(figure=d3_bar_chart)

"""
Pro:
- No need to create a custom chart, as datatable logic will live within the component (consistent with other components other than Graph)

Con:
- Need to enable many of the args from the dash datatable or enable users to provide *kwargs which deviates from all other models
- Would need to create a custom chart from Table instance anyways to enable more sophisticated functionality required by verticals
- Would need another wrapper for other react charts -> bad paradigm to create new model for each new react chart
"""

# 3) Table & React (currently preferred) --------------------
vm.Table(figure=dash_table)
vm.React(figure=d3_bar_chart)

"""
Pro:
- Users can customize their table to their liking and we don't maintain these args

Con:
- Users have to create a custom chart first and then provide it to the table
- Separate models for Table and other react components
- Table would only support one type of figure - does it then even deserve its own model?

To consider
- Does it make sense to have a figure argument if only one type of figure can be provided?
- Would we create our own custom react table at some point?
"""


# 4) ReactFigure --------------------
vm.React(figure=dash_table)
vm.React(figure=d3_bar_chart)

"""
Pro:
- Eventually gives us more freedom in creating custom js components
- Is only a thin wrapper and consistently returns an html.Div (one possible return type per model)

Con:
- Will have different clickEvent properties (that could be configured via custom actions though)

To consider:
- Should we actually extend the concept of this to vm.Html or vm.Container as essentially it just wraps the component inside an html.Div?
  That model could then also be re-used for several other things? (Would mix lots of different concepts then though, so maybe bad idea)
"""
