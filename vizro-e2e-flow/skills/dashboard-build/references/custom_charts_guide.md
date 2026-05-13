# How to create Vizro custom charts

Load the **selecting-vizro-charts** skill for when to use custom charts, color rules, and KPI card rules.

## Overview

Custom charts are Python code that generates a plotly go.Figure object. It must fulfill the following criteria:

1. Must be decorated with the Vizro @capture("graph") decorator, imported from `vizro.models.types`
1. Must be wrapped in a function that is snake case named appropriately, e.g. `custom_gdp_vs_life_expectancy_chart`
1. Must accept `data_frame` as first argument which is a pandas DataFrame
1. Must return a plotly go.Figure object
1. All data used in the chart must be derived from the data_frame argument, all data manipulations must be done within the function.
1. DO NOT modify the background (with plot_bgcolor) or color sequences unless explicitly asked for
1. When creating hover templates, explicitly ensure that it works on light and dark mode

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

    for continent in data_frame["continent"].unique():
        continent_data = data_frame[data_frame["continent"] == continent]
        fig.add_trace(
            go.Scatter(
                x=continent_data["gdpPercap"],
                y=continent_data["lifeExp"],
                mode="markers",
                name=continent,
                marker=dict(size=continent_data["pop"] / 1_000_000),
                hovertemplate="<b>%{text}</b><br>GDP: %{x}<br>Life Exp: %{y}<extra></extra>",
                text=continent_data["country"],
            )
        )

    fig.update_layout(
        title="Life Expectancy vs GDP per Capita",
        xaxis_title="GDP per Capita",
        yaxis_title="Life Expectancy (years)",
        xaxis_type="log",
    )

    return fig
```

## Highlight-Aware Custom Charts

For Pattern 3 (Comparison Spotlight) or Pattern 5 (Select & Explore) from the **wiring-vizro-actions** skill, the target chart must accept a `highlight_X=None` argument. When `None`, the chart shows all data normally. When set, the matching entity is emphasized and the rest are faded.

This file covers the chart shape only. For the action wiring (Parameter + `set_control` + `visible=False`), see the **wiring-vizro-actions** skill.

### Pattern A: Boolean color (bar / scatter)

Use when each row in the data is a separate data point and the highlighted entity is one of many points.

```python
from vizro.models.types import capture
import vizro.plotly.express as px


@capture("graph")
def scatter_with_highlight(data_frame, highlight_country=None):
    country_is_highlighted = data_frame["country"] == highlight_country
    fig = px.scatter(
        data_frame,
        x="gdpPercap",
        y="lifeExp",
        size="pop",
        size_max=60,
        opacity=0.3,
        color=country_is_highlighted,
        category_orders={"color": [False, True]},  # ensures highlighted trace is trace index 1
    )
    if highlight_country is not None:
        fig.update_traces(selector=1, marker={"line_width": 2, "opacity": 1})
    fig.update_layout(showlegend=False)
    return fig
```

Steps:

1. Build a boolean mask: `is_highlighted = data_frame["column"] == highlight_X`.
2. Pass as `color=is_highlighted`.
3. Lock color order: `category_orders={"color": [False, True]}` — guarantees the highlighted trace is index 1.
4. Set base `opacity=0.3` on the figure.
5. When a value is selected, override the highlighted trace with `update_traces(selector=1, ...)`.

### Pattern B: Name selector (line / bump)

Use when each entity is its own trace (one line per country, etc.). `selector={"name": ...}` picks the matching trace by name.

```python
@capture("graph")
def bump_chart_with_highlight(data_frame, highlight_country=None):
    rank = data_frame.groupby("year")["lifeExp"].rank(method="dense", ascending=False)
    fig = px.line(data_frame, x="year", y=rank, color="country", markers=True)

    fig.update_traces(opacity=0.3, line_width=2)  # fade all lines

    if highlight_country is not None:
        fig.update_traces(
            selector={"name": highlight_country},
            opacity=1,
            line_width=3,
        )
    return fig
```

Steps:

1. Color by entity: `px.line(..., color="country")` — each entity becomes a trace with `name=<value>`.
2. Fade all: `fig.update_traces(opacity=0.3, line_width=2)`.
3. Bold the selected trace: `fig.update_traces(selector={"name": highlight_X}, opacity=1, line_width=3)`.

### Wiring at a glance

```python
vm.Parameter(
    id="highlight_country_param",
    targets=["bump_chart.highlight_country"],
    selector=vm.RadioItems(options=["NONE", *country_names]),
    visible=False,
)
```

- Include `"NONE"` in the selector options so the chart starts in an unhighlighted state.
- `visible=False` — the highlight effect itself is the visual feedback. The "Reset controls" button clears the highlight.

Full pattern context: see the **wiring-vizro-actions** skill, Pattern 3 and Pattern 5.

## Common mistakes

### Using plain `plotly.express` instead of `vizro.plotly.express`

Always use `import vizro.plotly.express as px` — never `import plotly.express`. This applies inside `@capture("graph")` functions too. `vizro.plotly.express` is a drop-in replacement that ensures Vizro theming works correctly. Plain `plotly.express` bypasses Vizro's color templates. `import plotly.graph_objects as go` is fine (there is no vizro wrapper for it).

### Custom charts as KPI cards

Never use custom charts for building KPI cards. Use built-in `kpi_card` / `kpi_card_reference` and do data manipulation in `app.py`. See **selecting-vizro-charts** skill for full rules.
