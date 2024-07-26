# How to generate a Vizro dashboard using Vizro-AI

Vizro-AI now supports text-to-dashboard functionality. It can generate a multi-page dashboard including the following features:

- Vizro components including Graph, AgGrid (basic), and Card
- Vizro Filters including Dropdown, Checklist, Dropdown, RadioItems, RangeSlider, Slider, DatePicker(in development)
- Vizro Layout
- Multi-dataframe and multi-page support

## Setup
Install Vizro-AI
```bash
pip install vizro_ai
```
Vizro-AI setup
```py
from vizro import Vizro
from vizro_ai import VizroAI

vizro_ai = VizroAI(model="gpt-4-turbo")
```

## Prepare the data and user prompt
```py
import vizro.plotly.express as px

df1 = px.data.gapminder()
df2 = px.data.stocks()
df3 = px.data.tips()


user_question = """
<page1> it's the dashboard landing page with 4 cards.
The first card says 'This is a dashboard created by Vizro-AI'.
The second card has text 'Gapminder data';
The third card has text 'Tips data';.
The fourth card has text 'Stock data';.
In terms of layout, arrange these 4 cards in this way:
divide the page space into a grid with 3 columns and 2 rows.
Row 1: first card takes the all 3 columns in this row.
Row 2: The second row also has three columns:

- The first column is for the second card.
- The second column is occupied by the third card.
- The third column is occupied by the fourth card.

<page2> 1 card, 1 chart, 1 filter.
The card says 'The Gapminder dataset provides historical data on countries' development indicators.'
Use a scatter matrix to visualize GDP per capita and life expectancy, colored by continent.
Layout the card on the left and the chart on the right. The card takes 1/3 of the whole page on the left. The chart takes 2/3 of the page and is on the right.
Add a filter to filter the scatter plot by year.

Add another filter to filter the chart by continent, using checkbox as selector.

<page3> 2 chart, 2 filters.
This page displays the tips dataset. use two different charts to show data
distributions. one chart should be a histogram chart showing the distribution of tip. Keep the chart title short.
and the other should be a scatter plot. total_bill is on x-axis and tip is on y-axis. the bubble size is controlled by columns `size`.
first chart is on the right and the second chart is on the left.
Add a filter to filter data in the scatter plot by column `sex`.
add a second filter to filter the histogram chart by column `time` using radio buttons as selector.

<page4> 1 table. The table shows the tech companies stock data.
"""
```
## Call Vizro-AI
```py
dashboard = vizro_ai.dashboard([df1, df2, df3], user_question)
```
This will trigger the dashboard building process. Once Vizro-AI finishes the dashboard generation process, you can now launch the dashboard.

!!! example "Generated dashboard"

    === "Code"
        ```py
        Vizro().build(dashboard).run()
        ```

    === "Page1"
        [![VizroAIDashboardPage1]][VizroAIDashboardPage1]

    === "Page2"
        [![VizroAIDashboardPage2]][VizroAIDashboardPage2]

    === "Page3"
        [![VizroAIDashboardPage3]][VizroAIDashboardPage3]

    === "Page4"
        [![VizroAIDashboardPage4]][VizroAIDashboardPage4]

    [VizroAIDashboardPage1]: ../../assets/tutorials/dashboard/dashboard1_page1.png
    [VizroAIDashboardPage2]: ../../assets/tutorials/dashboard/dashboard1_page2.png
    [VizroAIDashboardPage3]: ../../assets/tutorials/dashboard/dashboard1_page3.png
    [VizroAIDashboardPage4]: ../../assets/tutorials/dashboard/dashboard1_page4.png
