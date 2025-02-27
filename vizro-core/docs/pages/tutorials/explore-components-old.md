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
