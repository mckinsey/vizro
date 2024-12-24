easy_prompt = """
I need a page with 1 table.
The table shows the tech companies stock data.

I need a second page showing 2 cards and one chart.
The first card says 'The Gapminder dataset provides historical data on countries' development indicators.'
The chart is an scatter plot showing life expectancy vs. GDP per capita by country.
Life expectancy on the y axis, GDP per capita on the x axis, and colored by continent.
The second card says 'Data spans from 1952 to 2007 across various countries.'
The layout uses a grid of 3 columns and 2 rows.

Row 1: The first row has three columns:
The first column is occupied by the first card.
The second and third columns are spanned by the chart.

Row 2: The second row mirrors the layout of the first row with respect to chart,
but the first column is occupied by the second card.

Add a filter to filter the scatter plot by continent.
Add a second filter to filter the chart by year.
"""

medium_prompt = """
<Page 1>
I need a page with 1 table and 1 line chart.
The chart shows the stock price trends of GOOG and AAPL.
The table shows the stock prices data details.

<Page 2>
I need a second page showing 3 cards and 4 charts.
The cards says 'The Gapminder dataset provides historical data on countries' development indicators.'
The charts are the scatter plots showing GDP per capita vs. life expectancy.
GDP per capita on the x axis, life expectancy on the y axis, and colored by continent.
Layout the cards on the left and the chart on the right.
Add a filter to filter the scatter plots by continent.
Add a second filter to filter the charts by year.

<Page 3>
This page displays the tips dataset. use four different charts to show data
distributions. one chart should be a bar chart. the other should be a scatter plot.
next chart should be a line chart. last one should be an area plot.
first and second charts are on the left and the third and fourth charts are on the right.
Add a filter to filter data in every plot by smoker.

<Page 4>
Create 3 cards on this page:
1. The first card on top says "This page combines data from various sources
 including tips, stock prices, and global indicators."
2. The second card says "Insights from Gapminder dataset."
3. The third card says "Stock price trends over time."

Layout these 3 cards in this way:
create a grid with 3 columns and 2 rows.
Row 1: The first row has three columns:
- The first column is empty.
- The second and third columns span the area for card 1.

Row 2: The second row also has three columns:
- The first column is empty.
- The second column is occupied by the area for card 2.
- The third column is occupied by the area for card 3.
    """


complex_prompt = """
<Page 1>
I need a page with 1 table and 3 line charts.
The chart shows the stock price trends of GOOG and AAPL.
The table shows the stock prices data details.
Add 3 filters to filter the line chart by companies.

<Page 2>
I need a second page showing 1 card and 1 chart.
The card says 'The Gapminder dataset provides historical data on countries' development indicators.'
The chart is a scatter plot showing GDP per capita vs. life expectancy.
GDP per capita on the x axis, life expectancy on the y axis, and colored by continent.
Layout the card on the left and the chart on the right. The card takes 1/3 of the whole space on the left.
The chart takes 2/3 of the whole space and is on the right.
Add a filter to filter the scatter plot by continent.
Add a second filter to filter the chart by year.

<Page 3>
This page displays the tips dataset. use two different charts to show data
distributions. one chart should be a bar chart and the other should be a scatter plot.
first chart is on the left and the second chart is on the right.
Add a filter to filter data in the scatter plot by smoker.

<Page 4>
Create 3 cards on this page:
1. The first card on top says "This page combines data from various sources
 including tips, stock prices, and global indicators."
2. The second card says "Insights from Gapminder dataset."
3. The third card says "Stock price trends over time."

Layout these 3 cards in this way:
create a grid with 3 columns and 2 rows.
Row 1: The first row has three columns:
- The first column is empty.
- The second and third columns span the area for card 1.

Row 2: The second row also has three columns:
- The first column is empty.
- The second column is occupied by the area for card 2.
- The third column is occupied by the area for card 3.
    """