# Explore Vizro

In this tutorial, we will build an interactive dashboard with multiple pages, incorporating a wide range of Vizro's components. If you're seeking a quickstart guide, consider reviewing the \[first dashboard tutorial\]([first dashboard tutorial](../tutorials/first-dashboard.md)) before diving into this one.

By the end of this tutorial, we will:

- Explore most of [Vizro's components](../user-guides/components.md)
- Use the [Vizro visual vocabulary](https://vizro-demo-visual-vocabulary.hf.space/) to guide our chart creation.
- Design custom charts with [Plotly Express](https://plotly.com/python-api-reference/plotly.express.html).
- Develop multiple pages for our dashboard.
- Customize the layout of these pages.
- Add interactivity to our dashboard using controls and actions.
- Set up navigation within the dashboard.
- Incorporate a logo into our dashboard.

We will use the [tips dataset](https://plotly.com/python-api-reference/generated/plotly.express.data.html#plotly.express.data.tips) for this example. This dataset was collected by a waiter who recorded information about each tip he received over several months at a restaurant. **Let's find out when he received the highest tips! 🚀**

## 1. (Optional) Install Vizro and get ready to run your code

The code for this tutorial is all available for you to experiment with in [PyCafe](https://py.cafe/huong-li-nguyen/vizro-analyzing-restaurant-tips) so there is no need to install Vizro and run it locally. For more about how this works, check out the [PyCafe documentation](https://py.cafe/docs/apps/vizro).

However, if you prefer working in a Notebook or Python script, you should [install Vizro](../user-guides/install.md).

??? note "To run the dashboard in a Notebook or script"
    Paste the code in a Notebook cell, run the Notebook, and evaluate it.

    ---

    If you prefer to use Python scripts to Notebooks, here's how to try out the dashboard:

    1. Create a new script called `app.py`.
    1. Copy the code above into the script.
    1. Navigate to the directory where `app.py` file is located using your terminal.
    1. Run the script by executing the command `python app.py`.

    Once the script is running, open your web browser and go to `localhost:8050`. You should see the dashboard page with the gapminder data displayed, as shown in the `Result` tab above.

!!! warning "Running the code in a Jupyter Notebook"
    If you are following this tutorial in a Jupyter Notebook, you might need to restart the kernel each time you evaluate the code. If you do not, you will see error messages such as "Components must uniquely map..." because those components already exist from the previous evaluation.

## 2. Create a first page

In this section, we will create a new [`Page`][vizro.models.Page] and store it inside a variable called `first_page`.

A [Page][vizro.models.Page] model is the foundation of any Vizro dashboard. A page uses a set of [component types](../user-guides/components.md) to display content. For a comprehensive list of available components, refer to the [components overview page](../user-guides/components.md).

### 2.1. Add a table

To start, let's get an overview of the data and display it in a table using [AgGrid][vizro.models.AgGrid]. To create a page and add a table to it, follow these steps:

1. Import all relevant packages and load in the data for this tutorial.
1. Create a [Page][vizro.models.Page] and set the title to "Data".
1. Add a Vizro [AgGrid][vizro.models.AgGrid] to the components list.
1. Inside the `figure` argument of the `AgGrid`, use the `dash_ag_grid` function.
1. Provide details about the data source in the `footer` argument of the `AgGrid`.

!!! example "First Page"
    === "Code - dashboard"
        ```{.python pycafe-link}
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.tables import dash_ag_grid
        from vizro.models.types import capture
        from vizro.figures import kpi_card

        tips = px.data.tips()

        first_page = vm.Page(
            title="Data",
            components=[
                vm.AgGrid(
                    figure=dash_ag_grid(tips),
                    footer="""**Data Source:** Bryant, P. G. and Smith, M (1995) Practical Data Analysis: Case Studies in Business Statistics. Homewood, IL: Richard D. Irwin Publishing.""",
                ),
            ],
        )

        dashboard = vm.Dashboard(pages=[first_page])
        Vizro().build(dashboard).run()
        ```

    === "Result"
        [![FirstPage]][firstpage]

As you can see from the code, `first_page` is added to the [`Dashboard`][vizro.models.Dashboard] and the dashboard is displayed by running `Vizro().build(dashboard).run()`.

Take a moment to explore the data in the table. You can sort, filter, and search within the \`AgGrid columns to gain a better understanding of the dataset.

You'll notice a toggle in the top-right corner of the dashboard. This allows you to switch between dark and light themes. Give it a try!

**Great job! We've successfully created our first page! 🎉**

## 3. Create a second page

Next, we'll add a second page to our dashboard, featuring charts and KPI (key performance indicator) cards.

### 3.1. Add a chart

Vizro leverages [Graph][vizro.models.Graph] models and Plotly Express functions to create various types of charts. You can explore the available chart types and their code examples in our [visual-vocabulary](https://vizro-demo-visual-vocabulary.hf.space).

Follow these steps to add a histogram to the page:

1. Create a second [Page][vizro.models.Page] and store it in a variable called second_page. Set its title to "Summary".
1. Add a Vizro [Graph][vizro.models.Graph] to the components list.
1. Inside the `figure` argument of the `Graph`, use the code for the [px.histogram from the visual-vocabulary](https://vizro-demo-visual-vocabulary.hf.space/distribution/histogram).
1. Add the new page to the list of pages in the [Dashboard][vizro.models.Dashboard].

!!! example "Second Page"
    === "Snippet - second page"
        ```py

        second_page = vm.Page(
            title="Summary",
            components=[
                vm.Graph(figure=px.histogram(tips, x="total_bill")),
                vm.Graph(figure=px.histogram(tips, x="tip")),
            ],
        )
        dashboard = vm.Dashboard(pages=[first_page, second_page])
        ```

    === "Code - dashboard"
        ```{.python pycafe-link}
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.tables import dash_ag_grid
        from vizro.models.types import capture
        from vizro.figures import kpi_card

        tips = px.data.tips()

        first_page = vm.Page(
            title="Data",
            components=[
                vm.AgGrid(
                    figure=dash_ag_grid(tips),
                    footer="""**Data Source:** Bryant, P. G. and Smith, M (1995) Practical Data Analysis: Case Studies in Business Statistics. Homewood, IL: Richard D. Irwin Publishing.""",
                ),
            ],
        )

        second_page = vm.Page(
            title="Summary",
            components=[
                vm.Graph(figure=px.histogram(tips, x="total_bill")),
                vm.Graph(figure=px.histogram(tips, x="tip")),
            ],
        )

        dashboard = vm.Dashboard(pages=[first_page, second_page])
        Vizro().build(dashboard).run()
        ```

    === "Result"
        [![SecondPage]][secondpage]

Notice that the charts are automatically stacked vertically in the specified order, each occupying equal space. This is Vizro's default behavior, but we'll customize the layout later! Additionally, note that a page navigation menu has been added to the left side of the dashboard. This allows you to switch between the two pages we have created.

### 3.2. Add KPI cards

You can combine and arrange various types of `components` on a dashboard page. Refer to the [components overview page](../user-guides/components.md) for a comprehensive list of available components.

Let's add two KPI cards to our second page. Follow these steps:

1. Add a [Figure][vizro.models.Figure] to the list of components
1. Inside the `figure` argument of the `Figure`, use the \`kpi_card function.
1. Configure your `kpi_card` by setting the `value_column`, `agg_func`, and `value_format` and `title` arguments. To learn more about how to configure KPI cards, check out [our how-to-guide on KPI vards](../user-guides/figure.md#key-performance-indicator-kpi-cards).
1. Repeat the above steps to add another KPI card to the page.

!!! example "Add KPI Cards"
    === "Snippet - KPI Card I"
        ```py

        vm.Figure(
            figure=kpi_card(
                data_frame=tips,
                value_column="total_bill",
                agg_func="mean",
                value_format="${value:.2f}",
                title="Average Bill",
            )
        )
        ```

    === "Snippet - KPI Card II"
        ```py

        vm.Figure(
            figure=kpi_card(
                data_frame=tips,
                value_column="tip",
                agg_func="mean",
                value_format="${value:.2f}",
                title="Average Tips"
            )
        )
        ```

    === "Code - dashboard"
        ```{.python pycafe-link}
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.tables import dash_ag_grid
        from vizro.models.types import capture
        from vizro.figures import kpi_card

        tips = px.data.tips()

        first_page = vm.Page(
            title="Data",
            components=[
                vm.AgGrid(
                    figure=dash_ag_grid(tips),
                    footer="""**Data Source:** Bryant, P. G. and Smith, M (1995) Practical Data Analysis: Case Studies in Business Statistics. Homewood, IL: Richard D. Irwin Publishing.""",
                ),
            ],
        )

        second_page = vm.Page(
            title="Summary",
            components=[
                vm.Figure(
                    figure=kpi_card(
                        data_frame=tips,
                        value_column="total_bill",
                        agg_func="mean",
                        value_format="${value:.2f}",
                        title="Average Bill",
                    )
                ),
                vm.Figure(
                    figure=kpi_card(
                        data_frame=tips,
                        value_column="tip",
                        agg_func="mean",
                        value_format="${value:.2f}",
                        title="Average Tips"
                    )
                ),
                vm.Graph(figure=px.histogram(tips, x="total_bill")),
                vm.Graph(figure=px.histogram(tips, x="tip")),
            ],
        )

        dashboard = vm.Dashboard(pages=[first_page, second_page])
        Vizro().build(dashboard).run()
        ```

    === "Result"
        [![SecondPage2]][secondpage2]

### 3.3. Add Tabs to switch views

Suppose we don't want to display both histograms simultaneously and prefer to switch between these views. We can achieve this by using the [Tabs](vizro.models.tabs) component to organize the content on the page. For more details on using the Tabs component, refer to our [Tabs user-guide](../user-guides/tabs.md).

Let's place the two histograms in separate tabs. Follow these steps:

1. Add each `Graph` to the `components` list of a [Container](vizro.models.Container).
1. Set the `title` argument inside each `Container` to the desired tab name.
1. Add the Containers to the `tabs` list of the `Tabs` component.
1. Add the `Tabs` component to the `components` list of the Page.

!!! example "Add Tabs"
    === "Snippet - Tabs"
        ```py

        vm.Tabs(
            tabs=[
                vm.Container(
                    title="Total Bill ($)",
                    components=[
                        vm.Graph(figure=px.histogram(tips, x="total_bill")),
                    ],
                ),
                vm.Container(
                    title="Total Tips ($)",
                    components=[
                        vm.Graph(figure=px.histogram(tips, x="tip")),
                    ],
                ),
            ],
        )
        ```

    === "Code - dashboard"
        ```{.python pycafe-link}
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.tables import dash_ag_grid
        from vizro.models.types import capture
        from vizro.figures import kpi_card

        tips = px.data.tips()

        first_page = vm.Page(
        title="Data",
        components=[
            vm.AgGrid(
                figure=dash_ag_grid(tips),
                footer="""**Data Source:** Bryant, P. G. and Smith, M (1995) Practical Data Analysis: Case Studies in Business Statistics. Homewood, IL: Richard D. Irwin Publishing.""",
            ),
        ],
        )

        second_page = vm.Page(
                    title="Summary",
                    components=[
                        vm.Figure(
                            figure=kpi_card(
                                data_frame=tips,
                                value_column="total_bill",
                                agg_func="mean",
                                value_format="${value:.2f}",
                                title="Average Bill",
                            )
                        ),
                        vm.Figure(
                            figure=kpi_card(
                                data_frame=tips, value_column="tip", agg_func="mean", value_format="${value:.2f}", title="Average Tips"
                            )
                        ),
                       vm.Tabs(
                        tabs=[
                            vm.Container(
                                title="Total Bill ($)",
                                components=[
                                    vm.Graph(figure=px.histogram(tips, x="total_bill")),
                                ],
                            ),
                            vm.Container(
                                title="Total Tips ($)",
                                components=[
                                    vm.Graph(figure=px.histogram(tips, x="tip")),
                                ],
                            ),
                        ],
                    )
                ],
            )

        dashboard = vm.Dashboard(pages=[first_page, second_page])
        Vizro().build(dashboard).run()
        ```

    === "Result"
        [![SecondPage3]][secondpage3]

Take a moment to switch between the Tabs! As you explore the dashboard, you might notice that the current layout could use some adjustments. The histograms appear cramped, while the KPI cards have too much space. In the next section, we'll learn how to configure the layout and better arrange the components.

### 3.4. Configure the layout

By default, Vizro places each element in the order it was added to `components` list, and spaces them equally. You can use the [`Layout`][vizro.models.Layout] object to specify the placement and size of components on the page. To learn more about how to configure layouts, check out [How to use layouts](../user-guides/layouts.md).

In the following layout configuration, the layout is divided into four columns and four rows. The two KPI cards are positioned at the top, each occupying one cell in the first row, with two empty cells to the right. The `Tabs` component is placed below the KPI cards, spanning all cells across the remaining three rows, providing it with more space compared to the KPI cards.

```
grid = [[0, 1, -1, -1],
        [2, 2, 2, 2],
        [2, 2, 2, 2],
        [2, 2, 2, 2]]
```

Run the code below to apply the layout to the dashboard page:

!!! example "Code - Layout"
    === "Code"
        ```py
        layout=vm.Layout(
            grid=[[0, 1,-1,-1],
                  [2, 2, 2, 2],
                  [2, 2, 2, 2],
                  [2, 2, 2, 2]])
        ```

    === "app.py"
        ```{.python pycafe-link}
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.tables import dash_ag_grid
        from vizro.models.types import capture
        from vizro.figures import kpi_card

        tips = px.data.tips()

        first_page = vm.Page(
        title="Data",
        components=[
            vm.AgGrid(
                figure=dash_ag_grid(tips),
                footer="""**Data Source:** Bryant, P. G. and Smith, M (1995) Practical Data Analysis: Case Studies in Business Statistics. Homewood, IL: Richard D. Irwin Publishing.""",
            ),
        ],
        )

        second_page = vm.Page(
                    title="Summary",
                    layout=vm.Layout(grid=[[0, 1, -1, -1],
                                    [2, 2, 2, 2],
                                    [2, 2, 2, 2],
                                    [2, 2, 2, 2]]),
                    components=[
                        vm.Figure(
                            figure=kpi_card(
                                data_frame=tips,
                                value_column="total_bill",
                                agg_func="mean",
                                value_format="${value:.2f}",
                                title="Average Bill",
                            )
                        ),
                        vm.Figure(
                            figure=kpi_card(
                                data_frame=tips,
                                value_column="tip",
                                agg_func="mean",
                                value_format="${value:.2f}",
                                title="Average Tips"
                            )
                        ),
                       vm.Tabs(
                        tabs=[
                            vm.Container(
                                title="Total Bill ($)",
                                components=[
                                    vm.Graph(figure=px.histogram(tips, x="total_bill")),
                                ],
                            ),
                            vm.Container(
                                title="Total Tips ($)",
                                components=[
                                    vm.Graph(figure=px.histogram(tips, x="tip")),
                                ],
                            ),
                        ],
                    )
                ],
            )

        dashboard = vm.Dashboard(pages=[first_page, second_page])
        Vizro().build(dashboard).run()
        ```

    === "Result"
        [![SecondPage4]][secondpage4]

### 3.5. Add a filter

[Filters][vizro.models.Filter] enable you to interact with the dashboard by selecting specific data points to display.

To add a filter to the dashboard, follow these steps:

1. Add a [`Filter`][vizro.models.Filter] to the `controls` list of the page.
1. Specify the column to be filtered using the `column` argument of the [Filter][vizro.models.Filter].
1. Change the `selector` in of the [`Filter`][vizro.models.Filter] to a [`Checklist`][vizro.models.Checklist]. For further customization, refer to the guide on [`How to use selectors`](../user-guides/selectors.md).

!!! example "Add a filter"
    === "Snippet - Filter"
        ```py
        controls=[vm.Filter(column="day"), vm.Filter(column="time", selector=vm.Checklist()), vm.Filter(column="size")]
        ```

    === "app.py"
        ```{.python pycafe-link}
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro
        from vizro.tables import dash_ag_grid
        from vizro.models.types import capture
        from vizro.figures import kpi_card

        tips = px.data.tips()

        first_page = vm.Page(
            title="Data",
            components=[
                vm.AgGrid(
                    figure=dash_ag_grid(tips),
                    footer="""**Data Source:** Bryant, P. G. and Smith, M (1995) Practical Data Analysis: Case Studies in Business Statistics. Homewood, IL: Richard D. Irwin Publishing.""",
                ),
            ],
        )

        second_page = vm.Page(
                    title="Summary",
                    layout=vm.Layout(grid=[[0, 1, -1, -1],
                                            [2, 2, 2, 2],
                                            [2, 2, 2, 2],
                                            [2, 2, 2, 2]]),
                    components=[
                        vm.Figure(
                            figure=kpi_card(
                                data_frame=tips,
                                value_column="total_bill",
                                agg_func="mean",
                                value_format="${value:.2f}",
                                title="Average Bill",
                            )
                        ),
                        vm.Figure(
                            figure=kpi_card(
                                data_frame=tips, value_column="tip", agg_func="mean", value_format="${value:.2f}", title="Average Tips"
                            )
                        ),
                       vm.Tabs(
                        tabs=[
                            vm.Container(
                                title="Total Bill ($)",
                                components=[
                                    vm.Graph(figure=px.histogram(tips, x="total_bill")),
                                ],
                            ),
                            vm.Container(
                                title="Total Tips ($)",
                                components=[
                                    vm.Graph(figure=px.histogram(tips, x="tip")),
                                ],
                            ),
                        ],
                    )
                ],
                controls=[vm.Filter(column="day"), vm.Filter(column="time", selector=vm.Checklist()), vm.Filter(column="size")],
            )

        dashboard = vm.Dashboard(pages=[first_page, second_page])
        Vizro().build(dashboard).run()
        ```

    === "Result"
        [![SecondPage5]][secondpage5]

You will see that a [Dropdown](vizro.models.Dropdown) is selected for categorical data and a [RangeSlider](vizro.models.RangeSlider) for numerical data. Additionally, the Filters are applied to all components on the page by default. If you want to apply a filter to specific components only, check out the [How to use filters](../user-guides/filters.md) guide.

**Great work! 📖 We've just completed our second dashboard page and learned how to:**

1. [Add a chart to a page using the visual vocabulary](#31-add-a-chart)
1. [Add KPI cards to display summary statistics](#32-add-kpi-cards)
1. [Add Tabs to switch views](#33-add-tabs-to-switch-views)
1. [Arrange our components by customizing the layout](#34-configure-the-layout).
1. [Add a filter to interact with the dashboard](#35-add-a-filter).

## 3. Create a second dashboard page

This section adds a second dashboard page and explains how to use controls and selectors. The new page is structured similarly to the page you created, but contains two charts that visualize the [iris data](https://plotly.com/python-api-reference/generated/plotly.express.data.html#plotly.express.data.iris).

Every [`Page`][vizro.models.Page] that you want to display needs to be added to the [`Dashboard`][vizro.models.Dashboard] object. The code below illustrates how to add the page, titled `second_page` to the dashboard by calling `vm.Dashboard(pages=[first_page,second_page])`. There are two `Graph` objects added to the list of components. To enable interactivity on those components, we add two [`Parameters`][vizro.models.Parameter] to the list of `controls`.

In creating a [`Parameter`][vizro.models.Parameter] object, you define the `target` it applies to. In the code below:

- The first parameter enables the user to change the color mapping for the `virginica` category of the iris data, targeting both charts.
- The second parameter adjusts the opacity of the first chart alone, through `scatter_iris.opacity`.

In general, `targets` for [`Parameters`][vizro.models.Parameter] are set following the structure of `component_id.argument`. In certain cases, you may see a nested structure for the `targets`. An example of this is `scatter_iris.color_discrete_map.virginica`. A nested structure targets a specific attribute within a component. In this particular example, it specifies that only the color of the virginica flower type should be changed. More information on how to set `targets` for [`Parameters`][vizro.models.Parameter] can be found in the [how-to guide for parameters](../user-guides/parameters.md).

!!! example "Second page"
    === "Code"
        ```py
        iris_data = px.data.iris()
        second_page = vm.Page(
            title="Second Page",
            components=[
                vm.Graph(
                    id="scatter_iris",
                    figure=px.scatter(iris_data, x="sepal_width", y="sepal_length", color="species",
                        color_discrete_map={"setosa": "#00b4ff", "versicolor": "#ff9222"},
                        labels={"sepal_width": "Sepal Width", "sepal_length": "Sepal Length",
                                "species": "Species"},
                    ),
                ),
                vm.Graph(
                    id="hist_iris",
                    figure=px.histogram(iris_data, x="sepal_width", color="species",
                        color_discrete_map={"setosa": "#00b4ff", "versicolor": "#ff9222"},
                        labels={"sepal_width": "Sepal Width", "count": "Count",
                                "species": "Species"},
                    ),
                ),
            ],
            controls=[
                vm.Parameter(
                    targets=["scatter_iris.color_discrete_map.virginica",
                                "hist_iris.color_discrete_map.virginica"],
                    selector=vm.Dropdown(
                        options=["#ff5267", "#3949ab"], multi=False, value="#3949ab", title="Color Virginica"),
                    ),
                vm.Parameter(
                    targets=["scatter_iris.opacity"],
                    selector=vm.Slider(min=0, max=1, value=0.8, title="Opacity"),
                ),
            ],
        )
        ```

    === "app.py"
        ```{.python pycafe-link}
        from vizro import Vizro
        import vizro.models as vm
        import vizro.plotly.express as px

        df = px.data.gapminder()
        gapminder_data = (
                df.groupby(by=["continent", "year"]).
                    agg({"lifeExp": "mean", "pop": "sum", "gdpPercap": "mean"}).reset_index()
            )
        first_page = vm.Page(
            title="First Page",
            layout=vm.Layout(grid=[[0, 0], [1, 2], [1, 2], [1, 2]]),
            components=[
                vm.Card(
                    text="""
                        # First dashboard page
                        This pages shows the inclusion of markdown text in a page and how components
                        can be structured using Layout.
                    """,
                ),
                vm.Graph(
                    id="box_cont",
                    figure=px.box(gapminder_data, x="continent", y="lifeExp", color="continent",
                                    labels={"lifeExp": "Life Expectancy", "continent": "Continent"}),
                ),
                vm.Graph(
                    id="line_gdp",
                    figure=px.line(gapminder_data, x="year", y="gdpPercap", color="continent",
                                    labels={"year": "Year", "continent": "Continent",
                                    "gdpPercap":"GDP Per Cap"}),
                    ),
            ],
            controls=[
                vm.Filter(column="continent", targets=["box_cont", "line_gdp"]),
            ],
        )

        iris_data = px.data.iris()
        second_page = vm.Page(
            title="Second Page",
            components=[
                vm.Graph(
                    id="scatter_iris",
                    figure=px.scatter(iris_data, x="sepal_width", y="sepal_length", color="species",
                        color_discrete_map={"setosa": "#00b4ff", "versicolor": "#ff9222"},
                        labels={"sepal_width": "Sepal Width", "sepal_length": "Sepal Length",
                                "species": "Species"},
                    ),
                ),
                vm.Graph(
                    id="hist_iris",
                    figure=px.histogram(iris_data, x="sepal_width", color="species",
                        color_discrete_map={"setosa": "#00b4ff", "versicolor": "#ff9222"},
                        labels={"sepal_width": "Sepal Width", "count": "Count",
                                "species": "Species"},
                    ),
                ),
            ],
            controls=[
                vm.Parameter(
                    targets=["scatter_iris.color_discrete_map.virginica",
                                "hist_iris.color_discrete_map.virginica"],
                    selector=vm.Dropdown(
                        options=["#ff5267", "#3949ab"], multi=False, value="#3949ab", title="Color Virginica"),
                    ),
                vm.Parameter(
                    targets=["scatter_iris.opacity"],
                    selector=vm.Slider(min=0, max=1, value=0.8, title="Opacity"),
                ),
            ],
        )

        dashboard = vm.Dashboard(pages=[first_page,second_page])
        Vizro().build(dashboard).run()
        ```

    === "Result"
        [![SecondPage]][secondpage]

### 3.1. Customize with selectors

The code in the example above uses two different types of [`selector`](../user-guides/selectors.md) objects, namely [`Dropdown`][vizro.models.Dropdown] and [`Slider`][vizro.models.Slider] upon the [`Parameters`][vizro.models.Parameter]. The `selectors` enable configuration of the controls to customize their behavior and appearance.

The first parameter is a [`Dropdown`][vizro.models.Dropdown]. It is configured with two available options, disables multi-selection, and has a default `value` set to blue. Users can choose a single option from the dropdown.

The second parameter is a [`Slider`][vizro.models.Slider] with a default value of 0.8. Users can adjust a value within the specified range of `min=0` and `max=1`.

You can apply selectors to configure [`Filters`][vizro.models.Filter] and [`Parameters`][vizro.models.Parameter] to fine-tune the behavior and appearance of the controls. The selectors currently available are as follows:

- [`Parameter`][vizro.models.Parameter]:
- [`Checklist`][vizro.models.Checklist]
- [`Dropdown`][vizro.models.Dropdown]
- [`RadioItems`][vizro.models.RadioItems]
- [`RangeSlider`][vizro.models.RangeSlider]
- [`Slider`][vizro.models.Slider]

## 4. The final touches

Each page is added to the dashboard using the following line of code: `vm.Dashboard(pages=[first_page, second_page])`. This ensures that all the pages are accessible.

By default, a navigation panel on the left side enables the user to switch between the two pages.

!!! example "Final dashboard"
    === "Code"
        ```python
        dashboard = vm.Dashboard(pages=[home_page, first_page, second_page])
        Vizro().build(dashboard).run()
        ```

    === "app.py"
        ```{.python pycafe-link}

        from vizro import Vizro
        import vizro.models as vm
        import vizro.plotly.express as px

        df = px.data.gapminder()
        gapminder_data = (
                df.groupby(by=["continent", "year"]).
                    agg({"lifeExp": "mean", "pop": "sum", "gdpPercap": "mean"}).reset_index()
            )
        first_page = vm.Page(
            title="First Page",
            layout=vm.Layout(grid=[[0, 0], [1, 2], [1, 2], [1, 2]]),
            components=[
                vm.Card(
                    text="""
                        # First dashboard page
                        This pages shows the inclusion of markdown text in a page and how components
                        can be structured using Layout.
                    """,
                ),
                vm.Graph(
                    id="box_cont",
                    figure=px.box(gapminder_data, x="continent", y="lifeExp", color="continent",
                                    labels={"lifeExp": "Life Expectancy", "continent": "Continent"}),
                ),
                vm.Graph(
                    id="line_gdp",
                    figure=px.line(gapminder_data, x="year", y="gdpPercap", color="continent",
                                    labels={"year": "Year", "continent": "Continent",
                                    "gdpPercap":"GDP Per Cap"}),
                    ),
            ],
            controls=[
                vm.Filter(column="continent", targets=["box_cont", "line_gdp"]),
            ],
        )

        iris_data = px.data.iris()
        second_page = vm.Page(
            title="Second Page",
            components=[
                vm.Graph(
                    id="scatter_iris",
                    figure=px.scatter(iris_data, x="sepal_width", y="sepal_length", color="species",
                        color_discrete_map={"setosa": "#00b4ff", "versicolor": "#ff9222"},
                        labels={"sepal_width": "Sepal Width", "sepal_length": "Sepal Length",
                                "species": "Species"},
                    ),
                ),
                vm.Graph(
                    id="hist_iris",
                    figure=px.histogram(iris_data, x="sepal_width", color="species",
                        color_discrete_map={"setosa": "#00b4ff", "versicolor": "#ff9222"},
                        labels={"sepal_width": "Sepal Width", "count": "Count",
                                "species": "Species"},
                    ),
                ),
            ],
            controls=[
                vm.Parameter(
                    targets=["scatter_iris.color_discrete_map.virginica",
                                "hist_iris.color_discrete_map.virginica"],
                    selector=vm.Dropdown(
                        options=["#ff5267", "#3949ab"], multi=False, value="#3949ab", title="Color Virginica"),
                    ),
                vm.Parameter(
                    targets=["scatter_iris.opacity"],
                    selector=vm.Slider(min=0, max=1, value=0.8, title="Opacity"),
                ),
            ],
        )

        dashboard = vm.Dashboard(pages=[first_page, second_page])
        Vizro().build(dashboard).run()
        ```

    === "Subpage1"
        \[![FinalPage1]\][finalpage1]

    === "Subpage2"
        \[![FinalPage2]\][finalpage2]

Congratulations on completing this tutorial! You have acquired the knowledge to configure layouts, add components, and implement interactivity in Vizro dashboards, working across two navigable pages.

## Find out more

After completing the tutorial you now have a solid understanding of the main elements of Vizro and how to bring them together to create dynamic and interactive data visualizations.

You can find out more about the Vizro by reading the [components overview page](../user-guides/components.md). To gain more in-depth knowledge about the usage and configuration details of individual controls, check out the guides dedicated to [Filters](../user-guides/filters.md), [Parameters](../user-guides/parameters.md), and [Selectors](../user-guides/selectors.md). If you'd like to understand more about different ways to configure the navigation of your dashboard, head to [Navigation](../user-guides/navigation.md).

Vizro doesn't end here, and we only covered the key features, but there is still much more to explore! You can learn:

- How to create you own components under [custom components](../user-guides/custom-components.md).
- How to add custom styling using [static assets](../user-guides/assets.md) such as custom css or JavaScript files.
- How to use [Actions](../user-guides/actions.md) for example, for chart interaction or custom controls.
- How to create dashboards from `yaml`, `dict` or `json` following the [dashboard guide](../user-guides/dashboard.md).

!!! note "An introduction to Vizro-AI"
    In the example above, the code to create the line graph was generated using [Vizro-AI](https://vizro.readthedocs.io/en/latest/pages/tutorials/first-dashboard/). Vizro-AI enables you to use English, or other languages, to create interactive charts with [Plotly](https://plotly.com/python/) by simplifying the process through use of a large language model. In essence, Vizro-AI generates code from natural language instructions so that you can add it into a Vizro dashboard, such as in the example above.

    Find out more in the [Vizro-AI documentation](https://vizro.readthedocs.io/projects/vizro-ai/)!

[firstpage]: ../../assets/tutorials/dashboard/01-first-page.png
[secondpage]: ../../assets/tutorials/dashboard/02-second-page.png
[secondpage2]: ../../assets/tutorials/dashboard/03-second-page-kpi.png
[secondpage3]: ../../assets/tutorials/dashboard/04-second-page-tabs.png
[secondpage4]: ../../assets/tutorials/dashboard/05-second-page-layout.png
[secondpage5]: ../../assets/tutorials/dashboard/06-second-page-controls.png
