# Gallery of examples

Take a look at some dashboard examples that can be created with Vizro-AI using data from [Plotly Express](https://plotly.com/python-api-reference/generated/plotly.express.data.html). The examples below use the OpenAI `"gpt-4o"` model as for a reasonably complex dashboard we recommend the flagship models of the leading vendors.

### Elections and stocks dashboard

In this example, we are requesting a multi-dataframe and multi-page dashboard, which includes all types of components, one filter, and customized layout.
We will use the [election data](https://plotly.com/python-api-reference/generated/plotly.express.data.html#plotly.express.data.election) and the [stocks data](https://plotly.com/python-api-reference/generated/plotly.express.data.html#plotly.express.data.stocks).

!!! example "Complex dashboard"

    === "Code for the cell"

        ```py
        import vizro_ai
        from vizro_ai import VizroAI
        import plotly.express as px

        from dotenv import load_dotenv
        load_dotenv()

        df1 = px.data.election()
        df2 = px.data.stocks(datetimes=True)

        user_question = """
        Create a 2-page dashabord.

        <Page 1>
        Visualize the election result.

        NOTE:
        1. use consistent and default color scheme.
           1. make axis label and chart title simple and readable.

        I need 3 pie charts, 3 bar charts, 1 table, and 1 radio button as filter.

        pie chart 1: shows number of votes Coderre received, compared to total votes.
        pie chart 2: shows number of votes Bergeron received, compared to total votes.
        pie chart 3: shows number of votes Joly received, compared to total votes.

        bar chart 1: shows number of districts Coderre winned. put `result` on y-axis, put "count of districts" on x-axis.
        bar chart 2: shows number of districts Bergeron winned. put `result` on y-axis, put "count of districts" on x-axis.
        bar chart 3: shows number of districts Joly winned. put `result` on y-axis, put "count of districts" on x-axis.

        use table to show the election data.

        Layout of page 1:
        Imaging the whole page is divided by a (3 by 3) grid, with 3 rows and 3 columns.
        Row 1 - pie chart 1 takes column 1; pie chart 2 takes column 2; pie chart 3 takes column 3.
        Row 2 - bar chart 1 takes column 1; bar chart 2 takes column 2; bar chart 3 takes column 3.
        Row 3 - the table span all three columns.

        Add a filter to filter all pie charts by district, using radio button as selelctor.


        <Page 2>
        Visualize the tech company stock data.
        I need 1 line chart, 6 cards.

        line chart: shows the stock price history of all comanies. put data on x-axis, company names as facet_row. make the y-axis label simple and readable.

        For cards, render the exact text as requested.
        Card 1 has text `> Dow Jones \n\n ## **39,737.26**\n`
        Card 2 has text `> S&P 500 \n\n ## **4,509.61**\n`
        Card 3 has text `> NASDAQ Composite \n\n ## **14,141.48**\n`
        Card 4 has text `> FTSE 100 \n\n ## **7,592.66**\n`
        Card 5 has text `> DAX \n\n ## **15,948.85**\n`
        Card 6 has text `> Nikkei 225 \n\n ## **32,210.78**\n`

        Page Layout:
        In a grid of 7 rows and 6 columns:
        column 1 to column 5 - the line chart spans 5 columns (all 7 rows) from the left.
        column 6 - card 1 takes row 1; card 2 takes row 2; card 3 takes row 3; ... card 6 takes row 6; row 7 is empty.
        """

        vizro_ai = VizroAI(model="gpt-4o")
        dashboard = vizro_ai.dashboard([df1, df2], user_question)

        Vizro().build(dashboard).run()

        ```

    === "Page1"
        [![VizroAIDashboardPage1]][VizroAIDashboardPage1]

    === "Page2"
        [![VizroAIDashboardPage2]][VizroAIDashboardPage2]

    [VizroAIDashboardPage1]: ../../assets/user_guides/dashboard/dashboard1_page1.png
    [VizroAIDashboardPage2]: ../../assets/user_guides/dashboard/dashboard1_page2.png


### Exploring tips data

In this example, we will work with [tips data](https://plotly.com/python-api-reference/generated/plotly.express.data.html#plotly.express.data.tips) where we will describe
the position of components in the layout.


!!! example "Tips dashboard"

    === "Code"
        ```py
        import vizro.plotly.express as px
        from vizro_ai import VizroAI
        from vizro import Vizro

        df = px.data.tips()
        user_question = """
        Create a one-page dashboard layout with the following components:

        1. Card:
           - Position: Left of the page
           - Size: Takes up 1/4 of the total page width
           - Content: Display the text "This is Tips dataset"

        1. Table:
           - Position: Right of the card
           - Size: Takes up the remaining 3/4 of the page width
           - Content: Display the Tips dataset
        """

        vizro_ai = VizroAI(model="gpt-4o-mini")
        dashboard = vizro_ai.dashboard([df], user_question)

        Vizro().build(dashboard).run()
        ```

    === "Result"
        [![VizroAIDashboardPage1]][VizroAIDashboardPage1]


    [VizroAIDashboardPage1]: ../../assets/user_guides/dashboard/dashboard2_page1.png


### Exploring gapminder data

In this example, we are requesting a multi-page dashboard, which includes various types of components, filter, and customized layout.
We will use the [gapminder data](https://plotly.com/python-api-reference/generated/plotly.express.data.html#plotly.express.data.gapminder)


!!! example "Gapminder dashboard"

    === "Code"
        ```py
        import vizro.plotly.express as px
        from vizro_ai import VizroAI
        from vizro import Vizro

        df = px.data.gapminder()
        user_question = """
        Create a two-page dashboard with the following components:

        <Page 1>
        I need one card that has this exact text: """Population, GDP per capita, and life expectancy are interconnected metrics that provide insights into the socioeconomic well-being of a country. Rapid population growth can strain resources and infrastructure, impacting GDP per capita. Higher GDP per capita often enables better healthcare and improved life expectancy, but other factors such as healthcare quality and social policies also play significant roles."""

        I need map chart to visualize GDP per capita over the years for each country. Improve the layout of the chart, so that individual countries are clearly visible on the map.

        Use table to show the gapminder data.

        Add a filter on the table, to filter the table by the continent.

        Layout of page 1:
        The whole page is divided by a (6 by 2) grid, with 6 rows and 2 columns.
        Row 1 -card spans all two columns
        Row 2, 3 & 4 - animated map chart span all two columns
        Row 5 & 6 - the table span all two columns.

        <Page 2>
        I need page with three charts.

        First chart: Visualize the distribution of life expectancy across continents using boxplot chart.
        Second chart:  Compares the most recent life expectancy for each continent.
        Third chart: Visualize the progress of each continent when it comes to life expectancy numbers. Use average life expectancy for each continent as comparison metric.

        Page Layout:
        The whole page is divided by a (2 by 2) grid, with 3 rows and 2 columns.
        Row 1 - first chart spans both columns
        Row 2  - second chart spans column 1; third chart spans column 2.
        """

        vizro_ai = VizroAI(model="gpt-4o")
        dashboard = vizro_ai.dashboard([df1, df2], user_question)

        Vizro().build(dashboard).run()

        ```

    === "Page1"
        [![VizroAIGapminderPage1]][VizroAIDashboardPage1]

    === "Page2"
        [![VizroAIGapminderdPage2]][VizroAIDashboardPage2]

    [VizroAIGapminderPage1]: ../../assets/user_guides/dashboard/dashboard3_page1.png
    [VizroAIGapminderdPage2]: ../../assets/user_guides/dashboard/dashboard3_page2.png
