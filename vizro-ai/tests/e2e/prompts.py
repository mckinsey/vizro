from data_classes import Component, Control

easy_prompt = {
    "tier_type": "easy",
    "prompt_name": "one page + table + card + chart + 2 filters",
    "prompt_text": """
    I need a page with 1 table, 1 card and 1 chart.
    The table shows the tech companies stock data.
    The card says 'The Gapminder dataset provides historical data on countries' development indicators.'
    The chart is the scatter plot which uses gapminder dataframe
    and showing life expectancy vs. GDP per capita by country.
    Life expectancy on the y axis, GDP per capita on the x axis, and colored by continent.

    The layout uses a grid of 2 columns and 3 rows.
    The first row contains card
    The second row contains chart
    The third row contains table

    Add a filter to filter the scatter plot by continent.
    Add a second filter to filter the table by companies.
    """,
    "expected_config": {
        "pages": [
            {
                "components": [
                    Component(type="ag_grid"),
                    Component(type="card"),
                    Component(type="graph"),
                ],
                "controls": [
                    Control(type="filter"),
                    Control(type="filter"),
                ],
            },
        ],
    },
}

medium_prompt = {
    "tier_type": "medium",
    "prompt_name": "4 pages with supported prompt instructions",
    "prompt_text": """
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
    """,
    "expected_config": {
        "pages": [
            {
                "components": [
                    Component(type="ag_grid"),
                    Component(type="graph"),
                ],
                "controls": [],
            },
            {
                "components": [
                    Component(type="card"),
                    Component(type="graph"),
                ],
                "controls": [
                    Control(type="filter"),
                    Control(type="filter"),
                ],
            },
            {
                "components": [
                    Component(type="graph"),
                    Component(type="graph"),
                ],
                "controls": [
                    Control(type="filter"),
                ],
            },
            {
                "components": [
                    Component(type="card"),
                    Component(type="card"),
                    Component(type="card"),
                ],
                "controls": [],
            },
        ],
    },
}

complex_prompt = {
    "tier_type": "complex",
    "prompt_name": "4 pages with mix of supported and unsupported prompt instructions",
    "prompt_text": """
    <Page 1>
    Show me 1 table on the first page that shows tips and sorted by day
    Using export button I want to export data to csv
    Add filters by bill and by tip amount using slider

    <Page 2>
    Second page should contain kpi cards with population trends and
    two popular charts that display population per capita vs. continent.
    Filter charts by GDP using dropdown.
    Align kpi cards in one row and charts in different.
    Both charts should be in tabs.

    <Page 3>
    Third page should contain 6 charts showing stocks.
    Each should have separate filter by date.
    Filter types should include dropdown, datepicker, slider, checklist and radio items.
    Add parameter for any chart.

    <Page 4>
    Fourth page contains chart with wind data.
    Table with population per capita data.
    Two more charts with stocks and tips representations.
    Align table beautifully relative to the charts.
    Every chart should have 2 filters.
    Table should have 1 filter.
    """,
    "expected_config": {
        "pages": [
            {
                "components": [
                    Component(type="ag_grid"),
                ],
                "controls": [Control(type="filter"), Control(type="filter")],
            },
            {
                "components": [Component(type="graph"), Component(type="graph")],
                "controls": [Control(type="filter")],
            },
            {
                "components": [
                    Component(type="graph"),
                    Component(type="graph"),
                    Component(type="graph"),
                    Component(type="graph"),
                    Component(type="graph"),
                    Component(type="graph"),
                ],
                "controls": [
                    Control(type="filter"),
                    Control(type="filter"),
                    Control(type="filter"),
                    Control(type="filter"),
                    Control(type="filter"),
                    Control(type="filter"),
                ],
            },
            {
                "components": [
                    Component(type="ag_grid"),
                    Component(type="graph"),
                    Component(type="graph"),
                    Component(type="graph"),
                ],
                "controls": [
                    Control(type="filter"),
                    Control(type="filter"),
                    Control(type="filter"),
                    Control(type="filter"),
                    Control(type="filter"),
                    Control(type="filter"),
                    Control(type="filter"),
                ],
            },
        ],
    },
}
