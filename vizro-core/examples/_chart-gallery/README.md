# Chart gallery dashboard

This dashboard shows a gallery of charts. It includes guidance on when to use each chart type and sample Python code
to create them using [Plotly](https://plotly.com/python/) and [Vizro](https://github.com/mckinsey/vizro).

Inspired by the [FT Visual Vocabulary](https://github.com/Financial-Times/chart-doctor/blob/main/visual-vocabulary/README.md):
FT Graphics: Alan Smith, Chris Campbell, Ian Bott, Liz Faunce, Graham Parrish, Billy Ehrenberg, Paul McCallum, Martin Stabe.

## Chart types

The dashboard is still in development. Below is an overview of the chart types for which a completed page is available.

| Chart Type            | Status | Category                 |
| --------------------- | ------ | ------------------------ |
| Arc                   | ❌     | Part-to-whole            |
| Area                  | ✅     | Time                     |
| Bar                   | ✅     | Magnitude                |
| Barcode               | ❌     | Distribution             |
| Beeswarm              | ❌     | Distribution             |
| Boxplot               | ✅     | Distribution             |
| Bubble                | ❌     | Correlation, Magnitude   |
| Bubble map            | ❌     | Spatial                  |
| Bubble timeline       | ❌     | Time                     |
| Bullet                | ❌     | Magnitude                |
| Bump                  | ❌     | Ranking                  |
| Butterfly             | ✅     | Deviation, Distribution  |
| Chord                 | ❌     | Flow                     |
| Choropleth            | ✅     | Spatial                  |
| Column                | ✅     | Magnitude, Time          |
| Column line           | ❌     | Correlation, Time        |
| Connected scatter     | ✅     | Correlation, Time        |
| Cumulative curve      | ❌     | Distribution             |
| Diverging bar         | ❌     | Deviation                |
| Diverging stacked bar | ❌     | Deviation                |
| Donut                 | ✅     | Part-to-whole            |
| Dot map               | ❌     | Spatial                  |
| Dot plot              | ❌     | Distribution             |
| Fan                   | ❌     | Time                     |
| Flow map              | ❌     | Spatial                  |
| Funnel                | ❌     | Part-to-whole            |
| Gantt                 | ❌     | Time                     |
| Gridplot              | ❌     | Part-to-whole            |
| Heatmap               | ❌     | Time                     |
| Heatmap matrix        | ❌     | Correlation              |
| Histogram             | ✅     | Distribution             |
| Line                  | ✅     | Time                     |
| Lollipop              | ❌     | Ranking, Magnitude       |
| Marimekko             | ❌     | Magnitude, Part-to-whole |
| Network               | ❌     | Flow                     |
| Ordered bar           | ✅     | Ranking                  |
| Ordered bubble        | ❌     | Ranking                  |
| Ordered column        | ✅     | Ranking                  |
| Paired bar            | ✅     | Magnitude                |
| Paired column         | ✅     | Magnitude                |
| Parallel coordinates  | ❌     | Magnitude                |
| Pictogram             | ❌     | Magnitude                |
| Pie                   | ✅     | Part-to-whole            |
| Radar                 | ❌     | Magnitude                |
| Radial                | ❌     | Magnitude                |
| Sankey                | ✅     | Flow                     |
| Scatter               | ✅     | Correlation              |
| Scatter matrix        | ❌     | Correlation              |
| Slope                 | ❌     | Ranking, Time            |
| Sparkline             | ❌     | Time                     |
| Stacked bar           | ✅     | Part-to-whole            |
| Stacked column        | ✅     | Part-to-whole            |
| Stepped line          | ❌     | Ranking                  |
| Surplus deficit line  | ❌     | Deviation                |
| Treemap               | ✅     | Part-to-whole            |
| Venn                  | ❌     | Part-to-whole            |
| Violin                | ✅     | Distribution             |
| Waterfall             | ❌     | Part-to-whole, Flow      |

To contribute a chart, follow the steps below:

1. Place an `svg` file named after the chart type in the `assets` folder if it doesn't already exist.
2. Add the data set to `_pages_utils.py` if it doesn't already exist.
3. Create a new page for the chart type and add it to the relevant category `.py` file such as `correlation.py`,
   `deviation.py`, `distribution.py`, etc.
4. Add a `.py` file containing a code example of the chart type in the `pages/examples` folder, for instance, `area.py`
5. Remove the `IncompletePage(..)` entry for that chart type in `chart_groups.py`.
6. Update this `README.md` with the new chart type.

## How to run the example locally

1. If you have `hatch` set up, run the example with the command `hatch run example _chart-gallery`.
   Otherwise, with a virtual Python environment activated, run `pip install -r requirements.txt` and then `python app.py`.
2. You should now be able to access the app locally via http://127.0.0.1:8050/.
