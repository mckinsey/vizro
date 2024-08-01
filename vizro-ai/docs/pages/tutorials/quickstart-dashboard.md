# Dashboard generation

In the previous tutorial, we explained how to use Vizro-AI to generate individual charts from text. Vizro-AI also supports text-to-dashboard functionality, enabling you to generate a complete [Vizro](https://vizro.readthedocs.io/en/stable/) dashboard containing multiple charts and pages.

You may also want to review the [Vizro dashboard tutorial](https://vizro.readthedocs.io/en/stable/pages/tutorials/first-dashboard/), which creates a dashboard from scratch rather than by generation with Vizro-AI.

## 1. Install Vizro-AI and its dependencies

If you haven't already installed Vizro-AI and set up the API key for OpenAI, follow the [installation guide](../user-guides/install.md).


## 2. Open a Notebook
A good way to initially explore Vizro-AI is from inside a Jupyter Notebook.

??? "If you haven't used Jupyter before..."

    You may need to install the Jupyter package if you . From the terminal window:

    ```bash
    pip install jupyter
    ```

Start a new Notebook as follows:

```bash
jupyter notebook
```

The command opens Jupyter in a browser tab. Use the UI to navigate to a preferred folder in which to create this new dashboard.

Create a new `Python 3 (ipykernel)` Notebook from the "New" dropdown. Confirm your Vizro installation by typing the following into a cell in the Notebook and running it.

```py
import vizro_ai

print(vizro_ai.__version__)
```

You should see a return output of the form `x.y.z`.


## 3. Prepare the data
Next, prepare the data to pass to Vizro-AI. In this example, we use the [gapminder data](https://plotly.com/python-api-reference/generated/plotly.express.data.html#plotly.express.data.gapminder).

```py
import vizro.plotly.express as px

df1 = px.data.gapminder()
df2 = px.data.stocks()
df3 = px.data.tips()
```

## 4. Prepare the user prompt

Put together a string of text which is the prompt to request Vizro-AI to generate the dashboard.

Vizro-AI can generate a multi-page dashboard that includes the following features:

- Vizro components including `Graph`, `AgGrid` (basic), and `Card`
- Vizro filters including `Dropdown`, `Checklist`, `RadioItems`, `RangeSlider`, `Slider`, and `DatePicker`
- Vizro `Layout`
- Multi-dataframe and multi-page support

```text
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

## 5. Call Vizro-AI

Next, submit the data and prompt string:

```py
dashboard = vizro_ai.dashboard([df1, df2, df3], user_question)
```

The call to `dashboard()` triggers the dashboard building process. Once Vizro-AI finishes the dashboard generation process, you can launch the dashboard with `build()`.

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
