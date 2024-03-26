# Get started with Vizro-AI
This tutorial introduces you to Vizro-AI, which is an English-to-visualization package. In a series of steps, we will explain the basics and set you up with the knowledge to explore the package further.

### 1. Install Vizro and its dependencies

If you haven't already installed Vizro-AI and set up the API key for OpenAI, follow the [installation guide](../user-guides/install.md).

### 2. Open a Jupyter Notebook

A good way to initially explore Vizro-AI is from inside a Jupyter Notebook.

??? "If you haven't used Jupyter before..."

    You may need to install the Jupyter package if you . From the terminal window:

    ```bash
    pip install jupyter
    ```

    Alternatively, you can [work within Anaconda Navigator](../user-guides/install.md#use-vizro-inside-anaconda-navigator) as described in the Vizro installation guide.


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


### 3. Create your first chart using Vizro-AI

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

Finally, we call the `plot()` method with our English language instruction, to generate the visualization:

```python
vizro_ai.plot(df, "describe the composition of GDP in continent and color by continent, and add a horizontal line for avg GDP")
```

And that's it! By passing the prepared data and written visualization request, Vizro-AI takes care of the processing. It generates the necessary code for data manipulation and chart creation, and renders the chart by executing the generated code.

!!! example "Vizro AI Syntax"

    === "Code for the cell"
        ```py
        from vizro_ai import VizroAI
        import vizro.plotly.express as px

        df = px.data.gapminder()

        vizro_ai = VizroAI()
        vizro_ai.plot(df, "describe the composition of GDP in continent and color by continent, and add a horizontal line for avg GDP")
        ```
    === "Result"
        [![BarChart]][BarChart]

    [BarChart]: ../../assets/tutorials/chart/GDP_Composition_Bar.png

The created chart is interactive: you can hover over the data for more information.

### 5. Get an explanation with your chart

Passing `explain=True` to the `plot()` method provides insights to explain the rendered chart in detail. Let's create another example to illustrate the information returned:

!!! example "Specify  `explain=True`"

    === "Code for the cell"
        ```py
        vizro_ai.plot(df, "show me the geo distribution of life expectancy", explain=True)
        ```
    === "Result"
        [![GeoDistribution]][GeoDistribution]

    [GeoDistribution]: ../../assets/tutorials/chart/GeoDistribution.png

### 6. Explore further

Now, you have created your first charts with Vizro-AI you are ready to explore further.

A good place to start would be the [Explore Vizro-AI](./explore-vizro-ai.md) tutorial or you may want to review the different [run options](../user-guides/run-vizro-ai.md) including application integration.
