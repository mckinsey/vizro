# Get started with Vizro-AI
This tutorial serves as an introduction to Vizro-AI.
It is a step-by-step guide to help you experiment and create your initial Vizro chart using Vizro-AI, our English-to-visualization package. The goal is to provide you with the necessary knowledge to explore further into our documentation.

## Let's get started!
### 1. Install Vizro-AI and its dependencies
If you haven't already installed `vizro_ai` package, follow the [installation guide](../user_guides/install.md)
to do so inside a virtual environment.

??? tip "Beginners/Code novices"
    If you consider yourself a beginner to python and/or virtual environments, there is also a section in the [installation guide](../user_guides/install.md) that avoids any use of terminals and relies only upon a graphical user interface.

### 2. Set up jupyter notebook
A good way to initially explore Vizro-AI is from a Jupyter notebook.
Activate your previously created virtual environment and install Jupyter using the following command:

```console
pip install jupyter
```

Next, you can start your jupyter notebook in your activated environment by:

```console
jupyter notebook
```
This opens a browser tab, and you can navigate to your preferred folder for this new project. Create a new notebook Python 3 (ipykernel) notebook from the "New" dropdown. Make sure that you select your environment as kernel.

??? tip "Beginners/Code novices"
    If you followed the beginners steps in the [installation guide](../user_guides/install.md), you should already be set, and you can continue below.

Confirm that `vizro_ai` is installed by typing the following into a jupyter cell in your notebook and running it.

```py
import vizro_ai
print(vizro_ai.__version__)
```

You should see a return output of the version.

### 3. Large Language Model (LLM) API KEY

A prerequisite to use Vizro-AI is access to one of the supported LLMs. Refer to the [user guide](../user_guides/api_setup.md) on how to set up the API.

After successful setup, your API key is loaded in Jupyter with the following two lines:

```py
from dotenv import load_dotenv
load_dotenv()
```

### 4. Ask your first question using Vizro-AI

For your first visualization, we will create a chart illustrating the GDP of various continents while including a reference line for the average.

Let's go through the code step-by-step to understand how to use Vizro-AI. First, we create `pandas` DataFrame using the gapminder data from `plotly express`. Next, we instantiate `VizroAI` to call the `plot()` method to generate your visualization.

By passing your prepared data and your written visualization request to this method, Vizro-AI takes care of the processing. It generates the necessary code for data manipulation and chart creation, and then it proceeds to render the chart by executing the generated code.

!!! example "Vizro AI Syntax"
    === "Code for the cell"
        ```py
        from vizro_ai import VizroAI
        import vizro.plotly.express as px

        from dotenv import load_dotenv
        load_dotenv()

        df = px.data.gapminder()
        vizro_ai = VizroAI()
        vizro_ai.plot(df, "describe the composition of gdp in continent and color by continent, and add a horizontal line for avg gdp")
        ```
    === "Result"
        [![BarChart]][BarChart]

    [BarChart]: ../../assets/tutorials/chart/GDP_Composition_Bar.png

The created chart is interactive, and you can hover over the data for additional information.

### 5. Get an explanation with your chart

By passing `explain=True` to the `plot()` method will provide additional insights in addition to the rendered chart.

Let's create another example and read through the additional information.

!!! example "Specify  `explain=True`"
    === "Code for the cell"
        ```py
        vizro_ai.plot(df, "show me the geo distribution of life expectancy", explain=True)
        ```
    === "Result"
        [![GeoDistribution]][GeoDistribution]

    [GeoDistribution]: ../../assets/tutorials/chart/GeoDistribution.png

### 6. Explore further

Now, you have created your first charts with Vizro-AI and are ready to explore the documentation further.

A good place to start would be to go through the [model configuration](../user_guides/model_config.md) or different [run options](../user_guides/run_vizro_ai.md) including application integration.
