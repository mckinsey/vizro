# Chart gallery dashboard

This dashboard shows a gallery of charts. It includes guidance on when to use each chart type and sample Python code
to create them using [Plotly](https://plotly.com/python/) and [Vizro](https://vizro.mckinsey.com/).

Inspired by the [FT Visual Vocabulary](https://github.com/Financial-Times/chart-doctor/blob/main/visual-vocabulary/README.md):
FT Graphics: Alan Smith, Chris Campbell, Ian Bott, Liz Faunce, Graham Parrish, Billy Ehrenberg, Paul McCallum, Martin Stabe.

## Chart types

The dashboard is still in development. Below is an overview of the chart types for which a completed page is available.

| Chart Type            | Status | Category                 |
| --------------------- | ------ | ------------------------ |
| Arc                   | ❌     | Part-to-whole            |
| Area                  | ❌     | Time                     |
| Bar                   | ✅     | Magnitude                |
| Barcode               | ❌     | Distribution             |
| Beeswarm              | ❌     | Distribution             |
| Boxplot               | ✅     | Distribution             |
| Bubble                | ❌     | Correlation, Magnitude   |
| Bubble Map            | ❌     | Spatial                  |
| Bubble Timeline       | ❌     | Time                     |
| Bullet                | ❌     | Magnitude                |
| Bump                  | ❌     | Ranking                  |
| Butterfly             | ✅     | Deviation, Distribution  |
| Chord                 | ❌     | Flow                     |
| Choropleth            | ✅     | Spatial                  |
| Column                | ✅     | Magnitude, Time          |
| Column-Line           | ❌     | Correlation, Time        |
| Connected Scatter     | ❌     | Correlation, Time        |
| Cumulative Curve      | ❌     | Distribution             |
| Diverging Bar         | ❌     | Deviation                |
| Diverging Stacked Bar | ❌     | Deviation                |
| Donut                 | ✅     | Part-to-whole            |
| Dot Map               | ❌     | Spatial                  |
| Dot Plot              | ❌     | Distribution             |
| Fan                   | ❌     | Time                     |
| Flow Map              | ❌     | Spatial                  |
| Funnel                | ❌     | Part-to-whole            |
| Gantt                 | ❌     | Time                     |
| Gridplot              | ❌     | Part-to-whole            |
| Heatmap               | ❌     | Time                     |
| Heatmap-Matrix        | ❌     | Correlation              |
| Histogram             | ❌     | Distribution             |
| Line                  | ✅     | Time                     |
| Lollipop              | ❌     | Ranking, Magnitude       |
| Marimekko             | ❌     | Magnitude, Part-to-whole |
| Network               | ❌     | Flow                     |
| Ordered Bar           | ✅     | Ranking                  |
| Ordered Bubble        | ❌     | Ranking                  |
| Ordered Column        | ✅     | Ranking                  |
| Paired Bar            | ❌     | Magnitude                |
| Paired Column         | ❌     | Magnitude                |
| Parallel Coordinates  | ❌     | Magnitude                |
| Pictogram             | ❌     | Magnitude                |
| Pie                   | ✅     | Part-to-whole            |
| Radar                 | ❌     | Magnitude                |
| Radial                | ❌     | Magnitude                |
| Sankey                | ✅     | Flow                     |
| Scatter               | ✅     | Correlation              |
| Scatter Matrix        | ❌     | Correlation              |
| Slope                 | ❌     | Ranking, Time            |
| Sparkline             | ❌     | Time                     |
| Stacked Bar           | ❌     | Part-to-whole            |
| Stacked Column        | ❌     | Part-to-whole            |
| Stepped Line          | ❌     | Ranking                  |
| Surplus-Deficit-Line  | ❌     | Deviation                |
| Treemap               | ✅     | Part-to-whole            |
| Venn                  | ❌     | Part-to-whole            |
| Violin                | ✅     | Distribution             |
| Waterfall             | ❌     | Part-to-whole, Flow      |

To contribute a chart, follow the steps below:

1. Place an `svg` file named after the chart type in the `assets` folder if not already available.
2. Create a new page for the chart type in `pages.py` and a code sample in `pages/examples`. Refer to existing pages for guidance.
3. Add any new datasets to `pages/_page_utils.py`.
4. Remove the page from `incomplete_pages` in the relevant `ChartGroup`(s) in `chart_groups.py`.
5. Update this `README.md` with the new chart type.

## How to run the example locally

1. If you have `hatch` set up, run the example with the command `hatch run example _chart-gallery`.
   Otherwise, with a virtual Python environment activated, run `pip install -r requirements.txt` and then `python app.py`.
2. You should now be able to access the app locally via http://127.0.0.1:8050/.
