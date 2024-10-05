#Working to create the diverging bar with the Wind dataset. 
# https://colab.research.google.com/drive/1DsNkvow1cie3bo3wCP0gEiQ0T8Pjxc5C?usp=sharing 
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import vizro
import pandas as pd
import plotly.graph_objects as go
import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm
from vizro.models import Dashboard, Page, Filter, Graph
from vizro.managers import data_manager, model_manager

wind = px.data.wind()

# Extract the first letter of each direction
wind['primary_direction'] = wind['direction'].str[0]

# Aggregate frequencies based on the first letter
primary_wind = wind.groupby('primary_direction')['frequency'].sum().reset_index()

fig = go.Figure()

for i, direction in enumerate(primary_wind['primary_direction']):
  if direction in ['N', 'E']:
    fig.add_trace(go.Bar(
        y=[direction],
        x=[primary_wind['frequency'][i]],
        orientation='h',
        name=direction,
        marker_color='#66B2FF'
    ))
  else:
    fig.add_trace(go.Bar(
        y=[direction],
        x=[-primary_wind['frequency'][i]],
        orientation='h',
        name=direction,
        marker_color='#285a8d'
    ))

fig.update_layout(
    title='Wind Direction and Frequency (First Letter)',
    barmode='relative',
    yaxis_autorange='reversed',
    height=400,
    width=600,
    xaxis_title="Frequency",
    yaxis_title="Direction",
    bargap=0.2,
    legend_title_text='Directions'
)

fig.add_shape(
    type="line",
    x0=0, y0=-0.5,
    x1=0, y1=3.5,
    line=dict(color="black", width=2)
)
fig.show()

