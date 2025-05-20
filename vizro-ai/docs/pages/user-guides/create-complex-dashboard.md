# Generate a complex dashboard

!!! warning "Vizro-AI has been replaced by Vizro-MCP"

    Vizro-AI has largely been replaced by [Vizro-MCP](https://github.com/mckinsey/vizro/blob/main/vizro-mcp/README.md) and only supports chart generation from version 0.4.0.

This guide shows you how to instruct Vizro-AI to create a complex dashboard.

In general, Vizro-AI can follow user requirements well and generate high-quality dashboards, but the nature of LLMs means that the output generated at first is not always an exact match for your expectations. When the text length of user requirements increases, the LLMs can start to miss part of the user requirements or make mistakes. Apart from choosing more advanced models for harder tasks, improving the user prompt can help too.

The following example shows how to use Vizro-AI to generate a complex Vizro dashboard.

If you haven't already installed Vizro-AI and set up the API key for OpenAI, follow the [installation guide](../user-guides/install.md).

## 1. Prepare the data

Next, prepare the data to pass to Vizro-AI. In this example, we use the [election data](https://plotly.com/python-api-reference/generated/plotly.express.data.html#plotly.express.data.election) and the [stocks data](https://plotly.com/python-api-reference/generated/plotly.express.data.html#plotly.express.data.stocks).

```py
import vizro.plotly.express as px

df1 = px.data.election()
df2 = px.data.stocks(datetimes=True)
```

## 2. Prepare the user prompt

Devise a string of text to form the prompt that requests Vizro-AI to generate the Vizro dashboard.

Vizro-AI can generate a multi-page dashboard that includes the following features:

- Vizro components including `Graph`, `AgGrid` (basic), and `Card`
- Vizro filters including `Dropdown`, `Checklist`, `RadioItems`, `RangeSlider`, `Slider`, and `DatePicker`
- Vizro `Layout`
- Multi-dataframe and multi-page support

In this example, we are requesting a multi-dataframe and multi-page dashboard, which includes all types of components, one filter, and customized layout.

```text
user_question = """
Create a 2-page dashabord.

<Page 1>
Visualize the election result.

NOTE:
1. use consistent and default color scheme.
2. make axis label and chart title simple and readable.

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
```

It's worth noting that a more structured user request is also more machine readable.

- Top down instructions can help Vizro-AI to make better plans on what to build.
- Using line breaks and special characters can help in making instructions clearer for a language model. It helps in parsing and understanding the structure and emphasis in your request.

## 3. Call Vizro-AI

Next, submit the data and prompt string:

```py
from vizro_ai import VizroAI

vizro_ai = VizroAI(model="gpt-4o")
dashboard = vizro_ai.dashboard([df1, df2], user_question)
```

The call to `dashboard()` triggers the dashboard building process. Once Vizro-AI finishes this process, you can launch the dashboard with `build()`.

!!! example "Generated dashboard"

    === "Code"

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

        bar chart 1: shows number of districts Coderre won. Put `result` on y-axis, put "count of districts" on x-axis.
        bar chart 2: shows number of districts Bergeron won. Put `result` on y-axis, put "count of districts" on x-axis.
        bar chart 3: shows number of districts Joly won. Put `result` on y-axis, put "count of districts" on x-axis.

        use table to show the election data.

        Layout of page 1:
        Imagine the whole page is divided by a (3 by 3) grid, with 3 rows and 3 columns.
        Row 1 - pie chart 1 takes column 1; pie chart 2 takes column 2; pie chart 3 takes column 3.
        Row 2 - bar chart 1 takes column 1; bar chart 2 takes column 2; bar chart 3 takes column 3.
        Row 3 - the table span all three columns.

        Add a filter to filter all pie charts by district, using radio button as selector.


        <Page 2>
        Visualize the tech company stock data.
        I need 1 line chart, 6 cards.

        line chart: shows the stock price history of all companies. Put data on x-axis, company names as facet_row. make the y-axis label simple and readable.

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

        [![VizroAIDashboardPage1]][vizroaidashboardpage1]

    === "Page2"

        [![VizroAIDashboardPage2]][vizroaidashboardpage2]

[vizroaidashboardpage1]: ../../assets/user_guides/dashboard/dashboard1_page1.png
[vizroaidashboardpage2]: ../../assets/user_guides/dashboard/dashboard1_page2.png
