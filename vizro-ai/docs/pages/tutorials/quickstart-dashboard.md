# Dashboard generation

!!! warning "Feature in Alpha Version"
    This feature is currently in **Alpha** version. It is stable but not officially released yet. We welcome feedback via the [GitHub Issues](https://github.com/mckinsey/vizro/issues). Note that the feature and its API may still undergo minor adjustments.


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

df = px.data.gapminder(datetimes=True, pretty_names=True)
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
Create a page showing 1 card, 1 chart, and 1 filter.
The first card says 'The Gapminder dataset is a detailed collection of global socioeconomic indicators over several decades. It includes data on GDP per capita, life expectancy, and population for numerous countries and regions. This dataset allows users to analyze development trends, health outcomes, economic growth, and demographic changes globally.'
The chart is a box plot showing life expectancy distribution. Put Life expectancy on the y axis, continent on the x axis, and color by continent.
The card takes 1 grid of the page space on the left and the box plot takes 3 grid space on the right.

Add a filter to filter the box plot by year.
"""
```

## 5. Call Vizro-AI

Next, submit the data and prompt string:

```py
dashboard = vizro_ai._dashboard([df], user_question)
```

The call to `_dashboard()` triggers the dashboard building process. Once Vizro-AI finishes the dashboard generation process, you can launch the dashboard with `build()`.

!!! example "Generated dashboard"

    === "Code"
        ```py
        Vizro().build(dashboard).run()
        ```

    === "Result"
        [![VizroAIDashboardPage1]][VizroAIDashboardPage1]

    [VizroAIDashboardPage1]: ../../assets/tutorials/dashboard/dashboard0_page1.png
