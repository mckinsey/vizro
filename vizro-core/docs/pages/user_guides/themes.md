# How to use themes

This guide shows you how to use themes. Themes are pre-designed collections of stylings that are applied to entire charts and dashboards.
The themes provided by Vizro are induced with our design best practices that make charts and dashboards look visually consistent and professional.

## Themes in dashboards
The [`Dashboard`][vizro.models.Dashboard] model accepts the `theme` argument, where you can currently choose between
a `vizro_dark` and a `vizro_light` theme. This theme will be applied on the entire dashboard and its charts/components. During run-time
you can still switch between the themes via the toggle button in the upper-right corner of the dashboard.

!!! example "Change theme"
    === "app.py"
        ```py hl_lines="18"
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro

        df = px.data.iris()

        page = vm.Page(
            title="Changing themes",
            components=[
                vm.Graph(
                    figure=px.scatter_matrix(
                        df, dimensions=["sepal_length", "sepal_width", "petal_length", "petal_width"], color="species"
                    ),
                ),
            ],
            controls=[vm.Filter(column="species")],
        )

        dashboard = vm.Dashboard(pages=[page], theme="vizro_light")

        Vizro().build(dashboard).run()
        ```
    === "app.yaml"
        ```yaml hl_lines="11"
        # Still requires a .py to register data connector in Data Manager and parse yaml configuration
        # See from_yaml example
        pages:
        - components:
          - figure:
              _target_: scatter_matrix
              color: species
              data_frame: iris
              dimensions: ["sepal_length", "sepal_width", "petal_length", "petal_width"]
            type: graph
          controls:
            - column: species
              type: filter
          title: Changing themes
        theme: vizro_light
        ```
    === "Result - vizro_light"
        [![Light]][Light]

    [Light]: ../../assets/user_guides/themes/light.png
    === "Result - vizro_dark"
        [![Dark]][Dark]

    [Dark]: ../../assets/user_guides/themes/dark.png


## Themes in plotly charts
You can also use our templates for plotly charts outside the dashboard.
Our `vizro_dark` and `vizro_light` theme are automatically registered to `plotly.io.templates` when importing Vizro.
You can find more details on how templates work in plotly.express [here](https://plotly.com/python/templates/#theming-and-templates).

### Set themes for all charts
The default plotly.io template is set to be `vizro_dark` as soon as you `import vizro`:

```py
import plotly.io as pio
import vizro
pio.templates
```


```text title="Result"
Templates configuration
-----------------------
    Default template: 'vizro_dark'
    Available templates:
        ['ggplot2', 'seaborn', 'simple_white', 'plotly',
         'plotly_white', 'plotly_dark', 'presentation', 'xgridoff',
         'ygridoff', 'gridon', 'none', 'vizro_dark', 'vizro_light']
```


All plotly charts run after the `import vizro` command will therefore have the `vizro_dark` template automatically
applied without further configuration.

To change the default plotly template globally, run:

```python
import plotly.io as pio

pio.templates.default = "vizro_light"
```

### Set themes for selected charts
To change the template for a selected chart only, use the `template` parameter and run:

```python
import vizro.plotly.express as px

df = px.data.iris()
px.scatter_matrix(df,
                  dimensions=["sepal_length", "sepal_width", "petal_length", "petal_width"],
                  color="species",
                  template="vizro_light")
```

!!! note

    Please note that using `import vizro.plotly.express as px` is equivalent to using `import plotly.express as px`,
    but with the added benefit of being able to integrate the resulting chart code into a Vizro dashboard.
    Vizro offers a minimal layer on top of Plotly's existing charting library, allowing you to seamlessly use all the
    existing charts and functionalities provided by plotly.express without any modifications.
