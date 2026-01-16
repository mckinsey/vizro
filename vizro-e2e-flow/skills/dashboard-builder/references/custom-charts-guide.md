# How to create Vizro custom charts

## Overview
Custom charts are Python code that generates a plotly go.Figure object. It must fulfill the following criteria:
0. Must be decorated with the Vizro @capture("graph") decorator, imported from `vizro.models.types`
1. Must be wrapped in a function that is snake case named appropriately, e.g. `custom_gdp_vs_life_expectancy_chart`
2. Must accept as first argument argument `data_frame` which is a pandas DataFrame
3. Must return a plotly go.Figure object
4. All data used in the chart must be derived from the data_frame argument, all data manipulations must be done within the function.
5. DO NOT modify the background (with plot_bgcolor) or color sequences unless explicitly asked for
6. When creating hover templates, explicitly ensure that it works on light and dark mode

## How to integrate into script
Add the code you created into the PYTHON script in the `#### CUSTOM CHART SETUP ####` section. You can move all imports to the top of the file.

## Example
```python
import plotly.graph_objects as go
import pandas as pd
from vizro.models.types import capture

@capture("graph")
def gapminder_life_expectancy_chart(data_frame: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    
    for continent in data_frame['continent'].unique():
        continent_data = data_frame[data_frame['continent'] == continent]
        fig.add_trace(go.Scatter(
            x=continent_data['gdpPercap'],
            y=continent_data['lifeExp'],
            mode='markers',
            name=continent,
            marker=dict(size=continent_data['pop'] / 1_000_000),
            hovertemplate='<b>%{text}</b><br>GDP: %{x}<br>Life Exp: %{y}<extra></extra>',
            text=continent_data['country']
        ))
    
    fig.update_layout(
        title="Life Expectancy vs GDP per Capita",
        xaxis_title="GDP per Capita",
        yaxis_title="Life Expectancy (years)",
        xaxis_type="log"
    )
    
    return fig
```