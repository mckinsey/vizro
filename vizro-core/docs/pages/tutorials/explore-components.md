# Explore Vizro

In this tutorial, we will build an interactive dashboard with multiple pages, incorporating a wide range of Vizro's components. If you're seeking a quickstart guide, consider reviewing the [first dashboard tutorial](../tutorials/first-dashboard.md) before diving into this one.

By the end of this tutorial, we will:

- Explore most of [Vizro's components](../user-guides/components.md).
- Use the [Vizro visual vocabulary](https://vizro-demo-visual-vocabulary.hf.space/) to guide our chart creation.
- Design custom charts with [Plotly Express](https://plotly.com/python-api-reference/plotly.express.html).
- Develop multiple pages for our dashboard.
- Customize the layout of these pages.
- Add interactivity to the dashboard using filters and parameters.
- Add a logo and title to the dashboard.
- Customize the navigation within the dashboard.

We will use the [tips dataset](https://plotly.com/python-api-reference/generated/plotly.express.data.html#plotly.express.data.tips) for this example. This dataset was collected by a waiter who recorded information about each tip he received over several months at a restaurant.

**Let's find out when he received the highest tips! 🚀**

## 1. (Optional) Install Vizro and get ready to run your code

You can experiment with the code for this tutorial directly on [PyCafe](https://py.cafe/vizro-official/vizro-tips-analysis-tutorial), so there's no need to install Vizro locally. However, we recommend starting with a [blank Vizro project on PyCafe](https://py.cafe/snippet/vizro/v1) and copying the code snippets from this tutorial to see how everything integrates. For more about how this works, check out the [PyCafe documentation](https://py.cafe/docs/apps/vizro).

If you prefer working in a Notebook or Python script, you should [install Vizro](../user-guides/install.md).

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

A [Page][vizro.models.Page] model is the foundation of any Vizro dashboard. A page uses a set of components to display content. For a comprehensive list of available components, refer to the [components overview page](../user-guides/components.md).

### 2.1. Add a table

To start, let's get an overview of the data and display it in a table using [AgGrid][vizro.models.AgGrid]. To create a page and add a table to it, follow these steps:

1. Import all relevant packages and load in the data for this tutorial.
1. Create a [Page][vizro.models.Page] and set the `title` to "Data".
1. Add an [AgGrid][vizro.models.AgGrid] to the `components` list.
1. Inside the `figure` argument of the `AgGrid`, use the [`dash_ag_grid`][vizro.tables.dash_ag_grid] function.
1. Provide details about the data source in the `footer` argument of the `AgGrid`.
1. Add the new page to the list of `pages` in the [Dashboard][vizro.models.Dashboard].

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
                    footer="""**Data Source:** Bryant, P. G. and Smith, M (1995)
                    Practical Data Analysis: Case Studies in Business Statistics.
                    Homewood, IL: Richard D. Irwin Publishing.""",
                ),
            ],
        )

        dashboard = vm.Dashboard(pages=[first_page])
        Vizro().build(dashboard).run()
        ```

    === "Result"
        [![FirstPage]][firstpage]

After running `Vizro().build(dashboard).run()`, you should be able to open your web browser and see the dashboard under `localhost:8050`.

Take a moment to explore the data in the table. You can sort, filter, and search within the `AgGrid` columns to gain a better understanding of the dataset.

You'll notice a toggle in the top-right corner of the dashboard. This allows you to switch between dark and light themes. Give it a try!

**Great job! We've successfully created our first page! 🎉**

## 3. Create a second page

Next, we'll add a second page to our dashboard, featuring charts and KPI (key performance indicator) cards.

### 3.1. Add a chart

Vizro leverages [Graph][vizro.models.Graph] models and [Plotly Express functions](https://plotly.com/python/plotly-express/) to create various types of charts. You can explore some of the available chart types and their code examples in our [visual-vocabulary](https://vizro-demo-visual-vocabulary.hf.space).

Follow these steps to add a histogram to the page:

1. Create a second [Page][vizro.models.Page] and store it in a variable called `second_page`. Set its `title` to "Summary".
1. Add a [Graph][vizro.models.Graph] to the `components` list.
1. Inside the `figure` argument of the `Graph`, use the code for the [px.histogram from the visual-vocabulary](https://vizro-demo-visual-vocabulary.hf.space/distribution/histogram).
1. Add the new page to the list of `pages` in the [Dashboard][vizro.models.Dashboard] by calling `vm.Dashboard(pages=[first_page,second_page])`.

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
        ```{.python pycafe-link hl_lines="22-28 30"}
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
                    footer="""**Data Source:** Bryant, P. G. and Smith, M (1995)
                    Practical Data Analysis: Case Studies in Business Statistics.
                    Homewood, IL: Richard D. Irwin Publishing.""",
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

Notice that the charts are automatically stacked vertically in the order specified under `components`, each taking up equal space. This is the default behavior in Vizro, but we'll customize the layout later!

Additionally, a page navigation has been added to the left side of the dashboard, allowing you to switch between the two pages we’ve created.

You can also notice that the left-side menu can be collapsed to provide more space for the dashboard content. **Give it a try! 🧪**

### 3.2. Add KPI cards

You can combine and arrange various types of `components` on a dashboard page. Refer to the [components overview page](../user-guides/components.md) for a comprehensive list of available components.

Let's add two KPI cards to our second page. Follow these steps:

1. Add a [Figure][vizro.models.Figure] to the list of `components`
1. Inside the `figure` argument of the `Figure`, use the [`kpi_card`][vizro.figures.kpi_card] function.
1. Configure your `kpi_card` by setting the `value_column`, `agg_func`, and `value_format` and `title`. To learn more about how to configure KPI cards, check out [our how-to-guide on KPI cards](../user-guides/figure.md#key-performance-indicator-kpi-cards).
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
        ```{.python pycafe-link hl_lines="25-42"}
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
                    footer="""**Data Source:** Bryant, P. G. and Smith, M (1995)
                    Practical Data Analysis: Case Studies in Business Statistics.
                    Homewood, IL: Richard D. Irwin Publishing.""",
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

Suppose we don't want to display both histograms simultaneously and prefer to switch between these views. We can achieve this by using the [`Tabs`][vizro.models.Tabs] component. For more details on using the `Tabs`, refer to our [Tabs user-guide](../user-guides/tabs.md).

Let's place the two histograms in separate tabs. Follow these steps:

1. Add each `Graph` to the `components` of a [`Container`][vizro.models.Container].
1. Set the `title` argument inside each `Container` to the desired tab name.
1. Add the Containers to the `tabs` list of the `Tabs` component.
1. Add the `Tabs` component to the `components` of the `Page`.

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
        ```{.python pycafe-link hl_lines="43-59"}
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
                    footer="""**Data Source:** Bryant, P. G. and Smith, M (1995)
                    Practical Data Analysis: Case Studies in Business Statistics.
                    Homewood, IL: Richard D. Irwin Publishing.""",
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

**Take a moment to switch between the Tabs! 🕰️**

As you explore the dashboard, you might notice that the current layout could use some adjustments. The histograms appear cramped, while the KPI cards have too much space. In the next section, we'll learn how to configure the layout and better arrange the components.

### 3.4. Configure the layout

By default, Vizro places each element in the order it was added to `components`, and spaces them equally. You can use the [`Layout`][vizro.models.Layout] to control the placement and size of components on the page. To learn more about how to configure layouts, check out [How to use layouts](../user-guides/layouts.md).

In the following layout configuration, the layout is divided into **four columns** and **four rows**. The numbers in the grid correspond to the index of the components in the `components` list.

- The first KPI card (0) is positioned at the top, occupying the first cell in the first row.
- The second KPI card (1) is positioned to the right of the first KPI card.
- There are two empty cells to the right of the KPI cards (-1).
- The `Tabs` component (2) is placed below the KPI cards, spanning all cells across the remaining three rows.

```
grid = [[0, 1, -1, -1],
        [2, 2, 2, 2],
        [2, 2, 2, 2],
        [2, 2, 2, 2]]
```

Run the code below to apply the layout to the dashboard page:

!!! example "Code - Layout"
    === "Snippet - Layout"
        ```py
        layout=vm.Layout(
            grid=[[0, 1,-1,-1],
                  [2, 2, 2, 2],
                  [2, 2, 2, 2],
                  [2, 2, 2, 2]]
        )
        ```

    === "Code - dashboard"
        ```{.python pycafe-link hl_lines="24"}
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
                    footer="""**Data Source:** Bryant, P. G. and Smith, M (1995)
                    Practical Data Analysis: Case Studies in Business Statistics.
                    Homewood, IL: Richard D. Irwin Publishing.""",
                ),
            ],
        )

        second_page = vm.Page(
            title="Summary",
            layout=vm.Layout(grid=[[0, 1, -1, -1], [2, 2, 2, 2], [2, 2, 2, 2], [2, 2, 2, 2]]),
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

**Much better, don't you think? 🎨 The layout now provides sufficient space to the charts!**

### 3.5. Add a filter

[Filters][vizro.models.Filter] enable you to interact with the dashboard by selecting specific data points to display.

To add a filter to the dashboard, follow these steps:

1. Add a [`Filter`][vizro.models.Filter] to the `controls` list of the `Page`.
1. Specify the column to be filtered using the `column` argument of the [Filter][vizro.models.Filter].
1. Change the `selector` in one of the `Filters` to a [`Checklist`][vizro.models.Checklist]. For further customization, refer to the guide on [`How to use selectors`](../user-guides/selectors.md).

!!! example "Add a filter"
    === "Snippet - Filter"
        ```py
        controls=[vm.Filter(column="day"), vm.Filter(column="time", selector=vm.Checklist()), vm.Filter(column="size")]
        ```

    === "Code - dashboard"
        ```{.python pycafe-link hl_lines="61"}
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
                    footer="""**Data Source:** Bryant, P. G. and Smith, M (1995)
                    Practical Data Analysis: Case Studies in Business Statistics.
                    Homewood, IL: Richard D. Irwin Publishing.""",
                ),
            ],
        )

        second_page = vm.Page(
            title="Summary",
            layout=vm.Layout(grid=[[0, 1, -1, -1], [2, 2, 2, 2], [2, 2, 2, 2], [2, 2, 2, 2]]),
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
            controls=[vm.Filter(column="day"), vm.Filter(column="time", selector=vm.Checklist()), vm.Filter(column="size")]
        )

        dashboard = vm.Dashboard(pages=[first_page, second_page])
        Vizro().build(dashboard).run()
        ```

    === "Result"
        [![SecondPage5]][secondpage5]

You will see that a [`Dropdown`][vizro.models.Dropdown] is selected by default for categorical data and a [`RangeSlider`][vizro.models.RangeSlider] for numerical data. Additionally, the Filters are applied to all components on the page.

If you want to apply a filter to specific components only, check out the [How to use filters](../user-guides/filters.md) guide.

**Great work! 📖 We've just completed our second dashboard page and learned how to:**

1. [Add a chart to a page using the visual vocabulary](#31-add-a-chart)
1. [Add KPI cards to display summary statistics](#32-add-kpi-cards)
1. [Add Tabs to switch views](#33-add-tabs-to-switch-views)
1. [Arrange our components by customizing the layout](#34-configure-the-layout)
1. [Add a filter to interact with the dashboard](#35-add-a-filter)

## 4. Create a third page

Now that we've learned how to create pages, add components, and configure layouts, let's create a third page for our dashboard. This will give us the opportunity to practice our skills and introduce some new concepts!

This page will feature a bar chart, a violin chart, and a heatmap. We'll once again leverage the [Vizro visual vocabulary](https://vizro-demo-visual-vocabulary.hf.space/).

### 4.1. Add multiple charts

This step should feel familiar. Let's add all three charts to the page.

1. Create a third [Page][vizro.models.Page] and store it in a variable called `third_page`. Set its title to "Analysis".
1. Add three Vizro [Graphs][vizro.models.Graph] to the `components` of the `Page`.
1. For each `Graph`, use the `figure` argument to provide one of the Plotly express functions: For `px.violin and px.density_heatmap`, you can use the Plotly figure code directly from the visual vocabulary. For `px.bar`, copy the code but update the `data`, `x`, and `y` arguments to match our dataset.
    - [px.violin from the visual-vocabulary](https://vizro-demo-visual-vocabulary.hf.space/distribution/violin)
    - [px.bar from the visual-vocabulary](https://vizro-demo-visual-vocabulary.hf.space/magnitude/column)
    - [px.density_heatmap from the visual-vocabulary](https://vizro-demo-visual-vocabulary.hf.space/time/heatmap)
1. Provide a title for each `Graph`.
1. Add the new page to the list of `pages` in the [Dashboard][vizro.models.Dashboard].

!!! example "Third page"
    === "Snippet - third page"
        ```py

        third_page = vm.Page(
            title="Analysis",
            components=[
                vm.Graph(
                    title="Where do we get more tips?",
                    figure=px.bar(tips, y="tip", x="day"),
                ),
                vm.Graph(
                    title="Is the average driven by a few outliers?",
                    figure=px.violin(tips, y="tip", x="day", color="day", box=True),
                ),
                vm.Graph(
                    title="Which group size is more profitable?",
                    figure=px.density_heatmap(tips, x="day", y="size", z="tip", histfunc="avg", text_auto="$.2f"),
                ),
            ],
        )

        dashboard = vm.Dashboard(pages=[first_page, second_page, third_page])
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
                    footer="""**Data Source:** Bryant, P. G. and Smith, M (1995)
                    Practical Data Analysis: Case Studies in Business Statistics.
                    Homewood, IL: Richard D. Irwin Publishing.""",
                ),
            ],
        )

        second_page = vm.Page(
            title="Summary",
            layout=vm.Layout(grid=[[0, 1, -1, -1], [2, 2, 2, 2], [2, 2, 2, 2], [2, 2, 2, 2]]),
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
            controls=[vm.Filter(column="day"), vm.Filter(column="time", selector=vm.Checklist()), vm.Filter(column="size")]
        )

        third_page = vm.Page(
            title="Analysis",
            components=[
                vm.Graph(
                    title="Where do we get more tips?",
                    figure=px.bar(tips, y="tip", x="day"),
                ),
                vm.Graph(
                    title="Is the average driven by a few outliers?",
                    figure=px.violin(tips, y="tip", x="day", color="day", box=True),
                ),
                vm.Graph(
                    title="Which group size is more profitable?",
                    figure=px.density_heatmap(tips, x="day", y="size", z="tip", histfunc="avg", text_auto="$.2f"),
                ),
            ],
        )

        dashboard = vm.Dashboard(pages=[first_page, second_page, third_page])
        Vizro().build(dashboard).run()
        ```

    === "Result"
        [![ThirdPage]][thirdpage]

You may notice that the third chart is not visible. This issue can occur with Plotly charts when there isn't enough space to display them properly. Let's customize the layout again to allocate more space to the heatmap.

### 4.2. Configure the layout

This step should also feel more familiar by now. Let's arrange the charts to provide more space to the heatmap.

In the following layout configuration, the layout is divided into two columns and two rows. The bar chart (index 0) and violin chart (index 1) are placed side by side in the first row, while the heatmap (index 2) spans the entire second row. Remember the index corresponds to the order in which the components are added to the `components`.

```
grid = [[0, 1],
        [2, 2]]
```

Run the code below to apply the layout to the dashboard page:

!!! example "Code - Layout"
    === "Code"
        ```py
        layout=vm.Layout(grid=[[0, 1], [2, 2]]),
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
                    footer="""**Data Source:** Bryant, P. G. and Smith, M (1995)
                    Practical Data Analysis: Case Studies in Business Statistics.
                    Homewood, IL: Richard D. Irwin Publishing.""",
                ),
            ],
        )

        second_page = vm.Page(
            title="Summary",
            layout=vm.Layout(grid=[[0, 1, -1, -1], [2, 2, 2, 2], [2, 2, 2, 2], [2, 2, 2, 2]]),
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
            controls=[vm.Filter(column="day"), vm.Filter(column="time", selector=vm.Checklist()), vm.Filter(column="size")]
        )

        third_page = vm.Page(
            title="Analysis",
            layout=vm.Layout(grid=[[0, 1], [2, 2]]),
            components=[
                vm.Graph(
                    title="Where do we get more tips?",
                    figure=px.bar(tips, y="tip", x="day"),
                ),
                vm.Graph(
                    title="Is the average driven by a few outliers?",
                    figure=px.violin(tips, y="tip", x="day", color="day", box=True),
                ),
                vm.Graph(
                    title="Which group size is more profitable?",
                    figure=px.density_heatmap(tips, x="day", y="size", z="tip", histfunc="avg", text_auto="$.2f"),
                ),
            ],
        )

        dashboard = vm.Dashboard(pages=[first_page, second_page, third_page])
        Vizro().build(dashboard).run()
        ```

    === "Result"
        [![ThirdPage2]][thirdpage2]

**Fantastic work! This looks so much better, doesn't it? 🎨**

### 4.3. Add a parameter

This section explains how to add a [Parameter][vizro.models.Parameter] to your dashboard.

A [Parameter][vizro.models.Parameter] lets you dynamically change a component’s argument, making the dashboard more interactive. Here we want to switch the `x` and `color` variable across all charts, allowing data analysis from different perspectives.

In creating a [`Parameter`][vizro.models.Parameter] object, you define the `target` it applies to. In general, `targets` for [`Parameters`][vizro.models.Parameter] are set following the structure of `component_id.argument`. More information on how to set `targets` for [`Parameters`][vizro.models.Parameter] can be found in the [how-to guide for parameters](../user-guides/parameters.md).

To add a parameter to the dashboard:

1. Add a [Parameter][vizro.models.Parameter] to the `controls` of the page.
1. Assign an `id` to each `Graph` in the `components` that the parameter should target.
1. Define the parameter's `targets` using the format `component-id.argument`.
1. Set the `selector` of the [Parameter][vizro.models.Parameter] to a [`RadioItems`][vizro.models.RadioItems].
1. Provide options for the `RadioItems` selector.

!!! example "Add a parameter"
    === "Snippet - parameter"
        ```py
        controls=[
            vm.Parameter(
                targets=["violin.x", "violin.color", "heatmap.x", "bar.x"],
                selector=vm.RadioItems(
                    options=["day", "time", "sex", "smoker", "size"], value="day", title="Change x-axis inside charts:"
                ),
            ),
        ],
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
                    footer="""**Data Source:** Bryant, P. G. and Smith, M (1995)
                    Practical Data Analysis: Case Studies in Business Statistics.
                    Homewood, IL: Richard D. Irwin Publishing.""",
                ),
            ],
        )

        second_page = vm.Page(
            title="Summary",
            layout=vm.Layout(grid=[[0, 1, -1, -1], [2, 2, 2, 2], [2, 2, 2, 2], [2, 2, 2, 2]]),
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
            controls=[vm.Filter(column="day"), vm.Filter(column="time", selector=vm.Checklist()), vm.Filter(column="size")]
        )

        third_page = vm.Page(
            title="Analysis",
            layout=vm.Layout(grid=[[0, 1], [2, 2]]),
            components=[
                vm.Graph(
                    id="bar",
                    title="Where do we get more tips?",
                    figure=px.bar(tips, y="tip", x="day"),
                ),
                vm.Graph(
                    id="violin",
                    title="Is the average driven by a few outliers?",
                    figure=px.violin(tips, y="tip", x="day", color="day", box=True),
                ),
                vm.Graph(
                    id="heatmap",
                    title="Which group size is more profitable?",
                    figure=px.density_heatmap(tips, x="day", y="size", z="tip", histfunc="avg", text_auto="$.2f"),
                ),
            ],
            controls=[
                vm.Parameter(
                    targets=["violin.x", "violin.color", "heatmap.x", "bar.x"],
                    selector=vm.RadioItems(
                        options=["day", "time", "sex", "smoker", "size"], value="day", title="Change x-axis inside charts:"
                    ),
                ),
            ],
        )

        dashboard = vm.Dashboard(pages=[first_page, second_page, third_page])
        Vizro().build(dashboard).run()
        ```

    === "Result"
        [![ThirdPage3]][thirdpage3]

### 4.4. Add a custom chart

You may notice that the `bar` chart appears cluttered with many lines. This happens because each inner bar represents a unique data point when an unaggregated dataset is provided. To avoid this, we can aggregate the data before plotting. However, the aggregation needs to be dynamic based on the parameter we added in the previous step.

To achieve this, we need to include the data aggregation inside the chart function. This requires creating a custom chart. For more information on when to create a custom chart, check out the [How to create custom charts](../user-guides/custom-charts.md) guide.

To create a custom chart, we follow these steps:

1. Create a function that takes the `data_frame` as input and returns a Plotly figure.
1. Decorate the function with the `@capture(graph)` decorator.
1. Inside the function, aggregate the data, provide a label to the chart and update the bar width.
1. Use this custom function in the `Graph` component instead of `px.bar`.

!!! example "Add custom chart"
    === "Snippet - custom chart"
        ```py
        @capture("graph")
        def bar_mean(data_frame, x, y):
            df_agg = data_frame.groupby(x).agg({y: "mean"}).reset_index()
            fig = px.bar(df_agg, x=x, y=y, labels={"tip": "Average Tip ($)"})
            fig.update_traces(width=0.6)
            return fig
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


        @capture("graph")
        def bar_mean(data_frame, x, y):
            df_agg = data_frame.groupby(x).agg({y: "mean"}).reset_index()
            fig = px.bar(df_agg, x=x, y=y, labels={"tip": "Average Tip ($)"})
            fig.update_traces(width=0.6)
            return fig


        first_page = vm.Page(
            title="Data",
            components=[
                vm.AgGrid(
                    figure=dash_ag_grid(tips),
                    footer="""**Data Source:** Bryant, P. G. and Smith, M (1995)
                    Practical Data Analysis: Case Studies in Business Statistics.
                    Homewood, IL: Richard D. Irwin Publishing.""",
                ),
            ],
        )

        second_page = vm.Page(
            title="Summary",
            layout=vm.Layout(grid=[[0, 1, -1, -1], [2, 2, 2, 2], [2, 2, 2, 2], [2, 2, 2, 2]]),
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
            controls=[vm.Filter(column="day"), vm.Filter(column="time", selector=vm.Checklist()), vm.Filter(column="size")]
        )

        third_page = vm.Page(
            title="Analysis",
            layout=vm.Layout(grid=[[0, 1], [2, 2]]),
            components=[
                vm.Graph(
                    id="bar",
                    title="Where do we get more tips?",
                    figure=bar_mean(tips, y="tip", x="day"),
                ),
                vm.Graph(
                    id="violin",
                    title="Is the average driven by a few outliers?",
                    figure=px.violin(tips, y="tip", x="day", color="day", box=True),
                ),
                vm.Graph(
                    id="heatmap",
                    title="Which group size is more profitable?",
                    figure=px.density_heatmap(tips, x="day", y="size", z="tip", histfunc="avg", text_auto="$.2f"),
                ),
            ],
            controls=[
                vm.Parameter(
                    targets=["violin.x", "violin.color", "heatmap.x", "bar.x"],
                    selector=vm.RadioItems(
                        options=["day", "time", "sex", "smoker", "size"], value="day", title="Change x-axis inside charts:"
                    ),
                ),
            ],
        )

        dashboard = vm.Dashboard(pages=[first_page, second_page, third_page])
        Vizro().build(dashboard).run()
        ```

    === "Result"
        [![ThirdPage4]][thirdpage4]

**Fantastic job reaching this point! 📖 We've just completed our final dashboard page and learned how to:**

1. [Add multiple charts](#41-add-multiple-charts)
1. [Customize our layout again](#42-configure-the-layout)
1. [Add a parameter to interact with the charts](#43-add-a-parameter)
1. [Add a custom chart to our dashboard](#44-add-a-custom-chart).

## 5. The final touches

Now that we've created all the dashboard pages, let's add a personal touch by including a title, logo, and customizing the navigation.

### 5.1 Add a title and logo

To add a title and a logo to your dashboard, follow these steps:

1. Set the `title` attribute of the [Dashboard][vizro.models.Dashboard] to "Tips Analysis Dashboard".
1. Download the `logo` from [this link](https://raw.githubusercontent.com/mckinsey/vizro/refs/heads/main/vizro-core/examples/dev/assets/logo.svg) and save it in a folder named `assets`.
1. Place the `assets` folder in the same directory as your `app.py/app.ipynb` file.

Your directory structure should look like this:

```text title="Example folder structure"
├── app.py
├── assets
│   ├── logo.svg
```

!!! example "Add a dashboard title and logo"
    === "Snippet - dashboard title"
        ```py
        dashboard = vm.Dashboard(pages=[first_page, second_page, third_page], title="Tips Analysis Dashboard")
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


        @capture("graph")
        def bar_mean(data_frame, x, y):
            df_agg = data_frame.groupby(x).agg({y: "mean"}).reset_index()
            fig = px.bar(df_agg, x=x, y=y, labels={"tip": "Average Tip ($)"})
            fig.update_traces(width=0.6)
            return fig


        first_page = vm.Page(
            title="Data",
            components=[
                vm.AgGrid(
                    figure=dash_ag_grid(tips),
                    footer="""**Data Source:** Bryant, P. G. and Smith, M (1995)
                    Practical Data Analysis: Case Studies in Business Statistics.
                    Homewood, IL: Richard D. Irwin Publishing.""",
                ),
            ],
        )

        second_page = vm.Page(
            title="Summary",
            layout=vm.Layout(grid=[[0, 1, -1, -1], [2, 2, 2, 2], [2, 2, 2, 2], [2, 2, 2, 2]]),
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
            controls=[vm.Filter(column="day"), vm.Filter(column="time", selector=vm.Checklist()), vm.Filter(column="size")]
        )

        third_page = vm.Page(
            title="Analysis",
            layout=vm.Layout(grid=[[0, 1], [2, 2]]),
            components=[
                vm.Graph(
                    id="bar",
                    title="Where do we get more tips?",
                    figure=bar_mean(tips, y="tip", x="day"),
                ),
                vm.Graph(
                    id="violin",
                    title="Is the average driven by a few outliers?",
                    figure=px.violin(tips, y="tip", x="day", color="day", box=True),
                ),
                vm.Graph(
                    id="heatmap",
                    title="Which group size is more profitable?",
                    figure=px.density_heatmap(tips, x="day", y="size", z="tip", histfunc="avg", text_auto="$.2f"),
                ),
            ],
            controls=[
                vm.Parameter(
                    targets=["violin.x", "violin.color", "heatmap.x", "bar.x"],
                    selector=vm.RadioItems(
                        options=["day", "time", "sex", "smoker", "size"], value="day", title="Change x-axis inside charts:"
                    ),
                ),
            ],
        )

        dashboard = vm.Dashboard(pages=[first_page, second_page, third_page], title="Tips Analysis Dashboard")
        Vizro().build(dashboard).run()
        ```

    === "Result"
        [![Dashboard]][dashboard]

Both the logo and the title will be positioned within the dashboard header. After following these steps, you should see the logo in the top-left corner of your dashboard header, with the title displayed next to it.

If you can't see the logo, make sure the image is called `logo` and is stored in the assets folder. For more details on supported image formats, refer to the [How to add a logo](../user-guides/assets.md#add-a-logo-image) guide.

### 5.2 Customize the navigation

By default, a navigation panel on the left side allows users to switch between the pages. In this section, we will customize this by creating a custom navigation bar.

The custom navigation bar will feature two icons: one for the "Data" page and another for the "Summary" and "Analysis" pages.

To create a custom navigation bar, follow these steps:

1. Set the `navigation` attribute of the [Dashboard][vizro.models.Dashboard] to a [Navigation][vizro.models.Navigation] object.
1. Assign a [NavBar][vizro.models.NavBar] object to the `nav_selector` attribute of the `Navigation` object.
1. Populate the `items` attribute of the [NavBar][vizro.models.NavBar] object with a list of [NavLink][vizro.models.NavLink] objects.
1. Customize each [NavLink][vizro.models.NavLink] object by setting its `label`, `pages`, and `icon` attributes.
    - The `label` attribute specifies the tooltip text displayed when hovering over the navigation icons.
    - The `pages` attribute lists the pages included in the accordion navigation for that icon.
    - The `icon` attribute sets the icon to display using the [Material Design Icons library](https://fonts.google.com/icons).

!!! example "Customize navigation"
    === "Snippet - navigation"
        ```py
        navigation=vm.Navigation(
            nav_selector=vm.NavBar(
                items=[
                    vm.NavLink(label="Data", pages=["Data"], icon="database"),
                    vm.NavLink(label="Charts", pages=["Summary", "Analysis"], icon="bar_chart"),
                ]
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


        @capture("graph")
        def bar_mean(data_frame, x, y):
            df_agg = data_frame.groupby(x).agg({y: "mean"}).reset_index()
            fig = px.bar(df_agg, x=x, y=y, labels={"tip": "Average Tip ($)"})
            fig.update_traces(width=0.6)
            return fig


        first_page = vm.Page(
            title="Data",
            components=[
                vm.AgGrid(
                    figure=dash_ag_grid(tips),
                    footer="""**Data Source:** Bryant, P. G. and Smith, M (1995)
                    Practical Data Analysis: Case Studies in Business Statistics.
                    Homewood, IL: Richard D. Irwin Publishing.""",
                ),
            ],
        )

        second_page = vm.Page(
            title="Summary",
            layout=vm.Layout(grid=[[0, 1, -1, -1], [2, 2, 2, 2], [2, 2, 2, 2], [2, 2, 2, 2]]),
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
            controls=[vm.Filter(column="day"), vm.Filter(column="time", selector=vm.Checklist()), vm.Filter(column="size")]
        )

        third_page = vm.Page(
            title="Analysis",
            layout=vm.Layout(grid=[[0, 1], [2, 2]]),
            components=[
                vm.Graph(
                    id="bar",
                    title="Where do we get more tips?",
                    figure=bar_mean(tips, y="tip", x="day"),
                ),
                vm.Graph(
                    id="violin",
                    title="Is the average driven by a few outliers?",
                    figure=px.violin(tips, y="tip", x="day", color="day", box=True),
                ),
                vm.Graph(
                    id="heatmap",
                    title="Which group size is more profitable?",
                    figure=px.density_heatmap(tips, x="day", y="size", z="tip", histfunc="avg", text_auto="$.2f"),
                ),
            ],
            controls=[
                vm.Parameter(
                    targets=["violin.x", "violin.color", "heatmap.x", "bar.x"],
                    selector=vm.RadioItems(
                        options=["day", "time", "sex", "smoker", "size"], value="day", title="Change x-axis inside charts:"
                    ),
                ),
            ],
        )

        dashboard = vm.Dashboard(
            pages=[first_page, second_page, third_page],
            title="Tips Analysis Dashboard",
            navigation=vm.Navigation(
                nav_selector=vm.NavBar(
                    items=[
                        vm.NavLink(label="Data", pages=["Data"], icon="database"),
                        vm.NavLink(label="Charts", pages=["Summary", "Analysis"], icon="bar_chart"),
                    ]
                )
            ),
        )
        Vizro().build(dashboard).run()
        ```

    === "Result"
        [![DashboardFinal]][dashboardfinal]

Take a moment to explore the navigation bar! Hover over the icons to view the tooltip text and click on them to navigate between the pages.

**Congratulations on completing this tutorial! You now have the skills to configure layouts, add components, and implement interactivity in Vizro dashboards across multiple navigable pages.**

## Find out more

After completing the tutorial you now have a solid understanding of the main elements of Vizro and how to bring them together to create dynamic and interactive data visualizations.

You can find out more about Vizro's component by reading the [components overview page](../user-guides/components.md). To gain more in-depth knowledge about the usage and configuration details of individual controls, check out the guides dedicated to [Filters](../user-guides/filters.md), [Parameters](../user-guides/parameters.md), and [Selectors](../user-guides/selectors.md).

If you'd like to understand more about different ways to configure the navigation of your dashboard, head to [Navigation](../user-guides/navigation.md).

Vizro doesn't end here, and we only covered the key features, but there is still much more to explore! You can learn:

- How to use [Actions](../user-guides/actions.md) for example, for chart interaction or custom controls.
- How to [extend and customize Vizro dashboards](../user-guides/extensions.md) by creating your own:
    - [custom components](../user-guides/custom-components.md).
    - [custom actions](../user-guides/custom-actions.md).
    - [custom tables](../user-guides/custom-tables.md).
    - [custom charts](../user-guides/custom-charts.md).
    - [custom figures](../user-guides/custom-figures.md).
- How to add custom styling using [static assets](../user-guides/assets.md) such as custom css or JavaScript files.
- How to [customize your data connection](../user-guides/data.md)
- How to create dashboards from `yaml`, `dict` or `json` following the [dashboard guide](../user-guides/dashboard.md).
- How to [deploy your dashboard](../user-guides/run-deploy.md)
- How to use [Vizro-AI](https://vizro.readthedocs.io/projects/vizro-ai/en/vizro-ai-0.3.6/) to create charts with GenAI

[dashboard]: ../../assets/tutorials/dashboard/11-dashboard-title-logo.png
[dashboardfinal]: ../../assets/tutorials/dashboard/12-dashboard-navigation.png
[firstpage]: ../../assets/tutorials/dashboard/01-first-page.png
[secondpage]: ../../assets/tutorials/dashboard/02-second-page.png
[secondpage2]: ../../assets/tutorials/dashboard/03-second-page-kpi.png
[secondpage3]: ../../assets/tutorials/dashboard/04-second-page-tabs.png
[secondpage4]: ../../assets/tutorials/dashboard/05-second-page-layout.png
[secondpage5]: ../../assets/tutorials/dashboard/06-second-page-controls.png
[thirdpage]: ../../assets/tutorials/dashboard/07-third-page.png
[thirdpage2]: ../../assets/tutorials/dashboard/08-third-page-layout.png
[thirdpage3]: ../../assets/tutorials/dashboard/09-third-page-parameter.png
[thirdpage4]: ../../assets/tutorials/dashboard/10-third-page-custom-chart.png
