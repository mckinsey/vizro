# Chart generation

This tutorial introduces you to chart generation using Vizro-AI. It explains the basics of creating a plotly chart that can be added to a Vizro dashboard. When you have followed it, you are set up to explore the Vizro and Vizro-AI packages further.

<!-- vale off -->

### 1. Install Vizro-AI and its dependencies

<!-- vale on -->

If you haven't already installed Vizro-AI and set up the API key for OpenAI, follow the [installation guide](../user-guides/install.md).

<!-- vale off -->

### 2. Open a Jupyter Notebook

<!-- vale on -->

A good way to initially explore Vizro-AI is from inside a Jupyter Notebook.

??? "If you haven't used Jupyter before..."

    You may need to install the Jupyter package if you . From the terminal window:

    ```bash
    pip install jupyter
    ```

Activate the virtual environment you used to install Vizro, and start a new Notebook as follows:

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

<!-- vale off -->

### 3. Create your first plotly chart using Vizro-AI

<!-- vale on -->

Let's create a chart to illustrate the GDP of various continents while including a reference line for the average. We give Vizro-AI the English language instruction "*describe the composition of GDP in continent and color by continent, and add a horizontal line for avg GDP*".

Let's go through the code step-by-step. First, we create a `pandas` DataFrame using the gapminder data from `plotly express`:

```python
from vizro_ai import VizroAI
import vizro.plotly.express as px

df = px.data.gapminder()
```

Next, we instantiate `VizroAI`:

```python
vizro_ai = VizroAI()
```

To learn how to customize the `VizroAI` class, check out the guide on [how to customize models](../user-guides/customize-vizro-ai.md).

Finally, we call the `plot()` method with our English language instruction, to generate the visualization:

```python
vizro_ai.plot(
    df,
    """create a line graph for GDP per capita since 1950 for
    each continent. Mark the x axis as Year, y axis as GDP Per Cap
    and don't include a title. Make sure to take average over continent.""",
)
```

!!! warning "Help! The LLM request was unauthorized"

    If you see an error similar to this, your LLM API key is not valid:

    `INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 401 Unauthorized"`

    Make sure you have [set up access to a large language model](../user-guides/install.md/#set-up-access-to-a-large-language-model). If you are confident that you have specified your API key correctly and have sufficient credits associated with it, check your environment. Some developers export the environment explicitly to ensure the API key is available at runtime. Call the following in your terminal:

    `export OPENAI_API_KEY="sk-YOURKEY"`.

    The call above makes the API key available from that terminal instance. If you want to access Vizro-AI from a Notebook, you should then run `jupyter notebook` (or just work within that terminal to run your Python script in `app.py`. When you restart the terminal, you'll need to call `export` again.

And that's it! By passing the prepared data and written visualization request, Vizro-AI takes care of the processing. It generates the necessary code for data manipulation and chart creation, and returns the chart by executing the generated code.

!!! example "Vizro-AI Syntax"

    === "Code for the cell"

        ```py
        import vizro.plotly.express as px
        from vizro_ai import VizroAI

        df = px.data.gapminder()

        vizro_ai = VizroAI(model="gpt-4-turbo")
        fig = vizro_ai.plot(
            df,
            """create a line graph for GDP per capita since 1950 for each continent.
            Mark the x axis as Year, y axis as GDP Per Cap and don't include a title.
            Make sure to take average over continent.""",
        )
        ```

    === "Result"

        [![LineGraph]][linegraph]

The chart created is interactive: you can hover over the data for more information.

Passing `return_elements=True` to the `plot()` method returns an object, which includes the code along with a set of insights to explain the rendered chart in detail. You can then use the code within a Vizro dashboard as illustrated in the [Vizro documentation](https://vizro.readthedocs.io/en/stable/pages/tutorials/explore-components/#22-add-further-components). For the line graph above, the code returned may be as follows:

!!! example "Returned by Vizro-AI"

    ```python
    from vizro.models.types import capture
    import vizro.plotly.express as px
    import pandas as pd


    @capture("graph")
    def custom_chart(data_frame):
        df = data_frame.groupby(["year", "continent"])["gdpPercap"].mean().unstack().reset_index()
        fig = px.line(df, x="year", y=["Africa", "Americas", "Asia", "Europe", "Oceania"])
        return fig


    fig = custom_chart(data_frame=df)
    ```

<!-- vale off -->

### 4. Get an explanation with your chart

<!-- vale on -->

Let's create another example to illustrate the code and insights returned when passing `return_elements=True` as a parameter to `plot()`:

!!! example "Specify  `return_elements=True`"

    === "Code for the cell"

        ```py
        res = vizro_ai.plot(df, "show me the geo distribution of life expectancy", return_elements=True)
        print(res.code)
        print(res.chart_insights)
        print(res.code_explanation)
        ```

    === "Result"

        Code

        ```py
        import plotly.express as px


        def custom_chart(data_frame):
            fig = px.choropleth(
                data_frame,
                locations="iso_alpha",
                color="lifeExp",
                hover_name="country",
                color_continuous_scale=px.colors.sequential.Plasma,
                labels={"lifeExp": "Life Expectancy"},
            )
            fig.update_layout(
                title="Global Life Expectancy Distribution",
                geo=dict(showframe=False, showcoastlines=True),
            )
            return fig
        ```

        Chart insights

        ```
        This choropleth map visualizes the global distribution of life expectancy across
        different countries. It highlights variations and trends in life expectancy,
        providing a clear visual representation of geographical disparities.
        ```

        Code explanation

        ```
        - Import Plotly Express.
        - Create a choropleth map using the `px.choropleth` function.
        - Set the `locations` parameter to the ISO alpha codes from the data.
        - Color the map based on life expectancy values.
        - Use a continuous color scale to represent different life expectancies.
        - Update layout to enhance map readability and aesthetics.
        ```

<!-- vale off -->

### 5. Explore further

<!-- vale on -->

Congratulations! You have created your first charts with Vizro-AI and you are ready to explore further.

A good place to start would be to review the different how-to guides to learn [the different ways to run Vizro-AI](../user-guides/run-vizro-ai.md), [how to create advanced charts](../user-guides/create-advanced-charts.md) and [how to add your Vizro-AI charts to a Vizro dashboard](../user-guides/add-generated-chart-usecase.md). You may also want to review the tutorial on [how to generate a Vizro dashboard with Vizro-AI](quickstart-dashboard.md)

[linegraph]: ../../assets/tutorials/chart/GDP_Composition_Graph.png
