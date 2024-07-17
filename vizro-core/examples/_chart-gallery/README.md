# Chart gallery dashboard

This demo dashboard provides a gallery of charts. It includes guidance on when to use each chart type and sample code
to create them using Plotly and Vizro.

Inspired by the [FT Visual Vocabulary](https://github.com/Financial-Times/chart-doctor/blob/main/visual-vocabulary/README.md):
FT Graphics: Alan Smith, Chris Campbell, Ian Bott, Liz Faunce, Graham Parrish, Billy Ehrenberg, Paul McCallum, Martin Stabe

## Chart types

The dashboard is still in development. Below is an overview of the chart types for which a completed page is available.

| Chart Type           | Status | Category                 |
| -------------------- | ------ | ------------------------ |
| Arc                  | ❌     | Part-to-whole            |
| Barcode              | ❌     | Distribution             |
| Bar                  | ✅     | Magnitude                |
| Boxplot              | ✅     | Distribution             |
| Bubble               | ❌     | Correlation, Magnitude   |
| Bubble Map           | ❌     | Spatial                  |
| Bubble Timeline      | ❌     | Time                     |
| Bullet               | ❌     | Magnitude                |
| Butterfly            | ✅     | Deviation, Distribution  |
| Chord                | ❌     | Flow                     |
| Choropleth           | ✅     | Spatial                  |
| Column               | ✅     | Magnitude, Time          |
| Column-Line          | ❌     | Correlation, Time        |
| Cumulative Curve     | ❌     | Distribution             |
| Diverging Bar        | ❌     | Deviation                |
| Dot Map              | ❌     | Spatial                  |
| Dot Plot             | ❌     | Distribution             |
| Donut                | ✅     | Part-to-whole            |
| Fan                  | ❌     | Time                     |
| Flow Map             | ❌     | Spatial                  |
| Funnel               | ❌     | Part-to-whole            |
| Gantt                | ❌     | Time                     |
| Heatmap              | ❌     | Time                     |
| Heatmap-Matrix       | ❌     | Correlation              |
| Histogram            | ❌     | Distribution             |
| Line                 | ❌     | Time                     |
| Lollipop             | ❌     | Ranking, Magnitude       |
| Marimekko            | ❌     | Magnitude, Part-to-whole |
| Ordered Bar          | ✅     | Ranking                  |
| Ordered Bubble       | ❌     | Ranking                  |
| Ordered Column       | ✅     | Ranking                  |
| Parallel Coordinates | ❌     | Magnitude                |
| Pictogram            | ❌     | Magnitude                |
| Pie                  | ✅     | Part-to-whole            |
| Radar                | ❌     | Magnitude                |
| Radial               | ❌     | Magnitude                |
| Sankey               | ✅     | Flow                     |
| Scatter              | ✅     | Correlation              |
| Scatter Matrix       | ❌     | Correlation              |
| Slope                | ❌     | Ranking, Time            |
| Sparkline            | ❌     | Time                     |
| Stacked Bar          | ❌     | Part-to-whole            |
| Stacked Column       | ❌     | Part-to-whole            |
| Stepped Line         | ❌     | Ranking                  |
| Surplus-Deficit-Line | ❌     | Deviation                |
| Treemap              | ✅     | Part-to-whole            |
| Venn                 | ❌     | Part-to-whole            |
| Violin               | ✅     | Distribution             |
| Waterfall            | ❌     | Part-to-whole, Flow      |

To contribute a chart, follow the steps below:

1. Ensure there is a `svg` in the `assets` folder with the same name as the chart type.
2. Add a new page for the chart type inside `chart_pages.py`. Take a look at the existing pages for guidance.
3. Add any new data set to the `DATA_DICT` inside `_page_utils.py`.
4. Add the new chart type to the `COMPLETED_CHARTS` list in `tab_containers.py` to enable navigation.
5. Add the new chart page to the navigation inside the `app.py`
6. Update this `README.md` with the new chart type.

## How to run the example locally

1. If you have `hatch` set up, run the example with the command `hatch run example charts`.
   Otherwise, run the `app.py` file with your environment activated where `vizro` is installed.
2. You should now be able to access the app locally via http://127.0.0.1:8050/.
