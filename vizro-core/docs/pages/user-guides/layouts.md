# How to change the layout of your page

The [`Page`][vizro.models.Page] model accepts a `layout` argument that enables custom arrangement of charts and components on the screen. This guide shows how to customize the layout using either the default [`Grid`][vizro.models.Layout] model or the optional [`Flex`][vizro.models.Flex] model inside the `layout` argument of the [`Page`][vizro.models.Page] or the [`Container`][vizro.models.Container].

## Layout options: Grid and Flex

The `layout` argument allows you to choose between two layout models: [`Grid`][vizro.models.Layout] (default) and [`Flex`][vizro.models.Flex]. Both models provide different ways to organize components on the page.

- **Grid layout**: The [`Grid`][vizro.models.Layout] layout arranges components in a structured grid where rows and columns are explicitly defined. This layout is ideal for precise control over the placement of components.
- **Flex layout**: The [`Flex`][vizro.models.Flex] layout arranges components using a flexible box model, where items can grow, shrink, and wrap dynamically based on available space. This layout is ideal for responsive designs where components need to adapt to different screen sizes.

The `layout` argument of the [`Page`][vizro.models.Page] model is optional. If no layout is specified, it will default to a grid layout - all charts/components are then automatically [**stacked vertically**](layouts.md#vertical-and-horizontal-stacking) on the page in one column.

!!! example "Default Layout"
    === "app.py"
        ```{.python pycafe-link}
        from vizro import Vizro
        import vizro.models as vm

        page = vm.Page(
            title="two_left",
            components=[vm.Card(text="""# Component 0"""),
                        vm.Card(text="""# Component 1""")]

        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

    === "app.yaml"
        ```yaml
        # Still requires a .py to add data to the data manager and parse YAML configuration
        # See yaml_version example
        pages:
          - components:
              - text: |
                  # Component 0
                type: card
              - text: |
                  # Component 1
                type: card
            title: two_left
        ```

    === "Result"
        [![Layout]][layout]

## Grid Layout

### Configure the grid

To customize the grid arrangement, configure the `grid` parameter of the [`Grid`][vizro.models.Layout] model.

The example below shows an example of a valid `grid`:

```python title="Basic example"
grid = [[0, 1], [0, 2]]
```

- The `grid` must be provided as `list[list[int]]` (for example, `grid = [[0, 1], [0, 2]]`).
- The integers in the `grid` must be consecutive integers starting with 0 (for example, `0`, `1`, `2`).
    - The integers correspond to the index of the chart/component inside the list of `components` provided to [`Page`][vizro.models.Page].
    - The number of integers in the `grid` needs to match the number of chart/components provided.
- Each sub-list corresponds to a grid row (in the example above, row 1 = `[0, 1]` and row 2 = `[0, 2]`)
- Each element inside the sub-list corresponds to a grid column (for example, column 1 = `[0, 0]` and column 2 = `[1, 2]`)
- Each chart/component will take the entire space of its grid area but you can use [empty sections](#add-empty-sections-to-the-grid) for extra separation.
- The area spanned by a chart/component in the grid must be rectangular.
- The grid can be arbitrarily large, allowing arbitrarily granular control of the grid.

### Understand stacking direction

As described above, when no `Layout` is specified, components are presented **vertically** as a single-column stack. If you have three components, the default `Layout.grid` will be as follows, with three equally sized rows, each containing a component spanning the entire width:

```python title="Vertical stacking"
grid = [[0], [1], [2]]
```

To present components **horizontally** in one row:

```python title="Horizontal stacking"
grid = [[0, 1, 2]]
```

This defines a single row that occupies the entire width and height, divided into three equal columns.

<figure markdown>
  ![Stacking components](../../assets/user_guides/layout/stacking.png){ width="680" }
</figure>

### Grid - basic example

!!! example "Grid Arrangement - Basic Example"
    === "app.py"
        ```{.python pycafe-link}
        import vizro.models as vm
        from vizro import Vizro

        page = vm.Page(
            title="one_left_two_right",
            layout=vm.Layout(grid=[[0, 1],
                                   [0, 2]]),
            components=[vm.Card(text="""# Component 0"""),
                        vm.Card(text="""# Component 1"""),
                        vm.Card(text="""# Component 2"""),
                        ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

    === "app.yaml"
        ```yaml
        # Still requires a .py to add data to the data manager and parse YAML configuration
        # See yaml_version example
        pages:
          - components:
              - text: |
                  # Component 0
                type: card
              - text: |
                  # Component 1
                type: card
              - text: |
                  # Component 2
                type: card
            layout:
              grid: [[0, 1], [0, 2]]
            title: one_left_two_right
        ```

    === "Result"
        [![Grid]][grid]

### Grid - advanced example

If you need to divide the grid into subgrids for finer control or want to visually distinguish your subgrids, you can use [`Containers`](container.md). See our section on [when to use `Containers` vs. `Page.layout`](container.md#when-to-use-containers) for more information.

The `Layout` provides full control over the arrangement of top-level components within a page, allowing arbitrarily granular control of the grid by creating larger grids.

!!! example "Grid Arrangement - Advanced Example"
    === "app.py"
        ```{.python pycafe-link}
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro

        gapminder = px.data.gapminder()

        page = vm.Page(
            title="Custom Layout - Advanced Example",
            layout=vm.Layout(grid=[[0, 1, 3, 4],
                                    [2, 2, 3, 4]]),
            components=[
                vm.Graph(
                    figure=px.line(
                        gapminder,
                        title="Graph 1",
                        x="year",
                        y="lifeExp",
                        color="continent",
                    ),
                ),
                vm.Graph(
                    figure=px.scatter(
                        gapminder,
                        title="Graph 2",
                        x="gdpPercap",
                        y="lifeExp",
                        size="pop",
                        color="continent",
                    ),
                ),
                vm.Graph(
                    figure=px.box(
                        gapminder,
                        title="Graph 3",
                        x="continent",
                        y="lifeExp",
                        color="continent",
                    ),
                ),
                vm.Graph(
                    figure=px.line(
                        gapminder,
                        title="Graph 4",
                        x="year",
                        y="lifeExp",
                        color="continent",
                    ),
                ),
                vm.Graph(
                    figure=px.scatter(
                        gapminder,
                        title="Graph 5",
                        x="gdpPercap",
                        y="lifeExp",
                        size="pop",
                        color="continent",
                    ),
                ),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

    === "app.yaml"
        ```yaml
        # Still requires a .py to add data to the data manager and parse YAML configuration
        # See yaml_version example
        pages:
          - components:
              - figure:
                  _target_: line
                  data_frame: gapminder
                  x: year
                  y: lifeExp
                  color: continent
                  title: Graph 1
                type: graph
              - figure:
                  _target_: scatter
                  data_frame: gapminder
                  x: gdpPercap
                  y: lifeExp
                  size: pop
                  color: continent
                  title: Graph 2
                type: graph
              - figure:
                  _target_: box
                  data_frame: gapminder
                  x: continent
                  y: lifeExp
                  color: continent
                  title: Graph 3
                type: graph
              - figure:
                  _target_: line
                  data_frame: gapminder
                  x: year
                  y: lifeExp
                  color: continent
                  title: Graph 4
                type: graph
              - figure:
                  _target_: scatter
                  data_frame: gapminder
                  x: gdpPercap
                  y: lifeExp
                  size: pop
                  color: continent
                  title: Graph 5
                type: graph
            layout:
              grid: [[0, 1, 3, 4], [2, 2, 3, 4]]
            title: Custom Layout - Advanced Example
        ```

    === "Result"
        [![GridAdv]][gridadv]

### Cheatsheet - grid examples

Here is a reference table of example layouts:

<!-- vale off -->

one row with one component, second row with two components stacked horizontally

| Layout needed                                                                                                                                                                                                           | Grid                                                                                                                        | Code                                                          |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| <img src="../../../assets/user_guides/layout/one_left_color.png" alt="one component" width="400"/>                                                                                                                      | <img src="../../../assets/user_guides/layout/1l_grid.png" alt="layout=vm.Layout(grid=[[0]])" width="100"/>                  | `layout=vm.Layout(grid=[[0]])`                                |
| <img src="../../../assets/user_guides/layout/two_left_color.png" alt="two horizontally stacked rows, each with one component" width="400"/>                                                                             | <img src="../../../assets/user_guides/layout/2l_grid.png" width="100"/>                                                     | `layout=vm.Layout(grid=[[0],[1]])`                            |
| <img src="../../../assets/user_guides/layout/two_top_color.png" alt="one row with two components set horizontally" width="400"/>                                                                                        | <img src="../../../assets/user_guides/layout/2t_grid.png" alt="layout=vm.Layout(grid=[[0],[1]])" width="100"/>              | `layout=vm.Layout(grid=[[0,1]])`                              |
| <img src="../../../assets/user_guides/layout/three_left_color.png" alt="three horizontally stacked rows, each with one component" width="400"/>                                                                         | <img src="../../../assets/user_guides/layout/3l_grid.png" alt="layout=vm.Layout(grid=[[0],[1],[2]]" width="100"/>           | `layout=vm.Layout(grid=[[0],[1],[2]])` or <br/> `layout=None` |
| <img src="../../../assets/user_guides/layout/one_left_two_right_color.png" alt="one row divided into two separate columns where the left column is one component and the right is two stacked components" width="400"/> | <img src="../../../assets/user_guides/layout/1l_2r_grid.png" alt="layout=vm.Layout(grid=[[0,1],[0,2]])"  width="100"/>      | `layout=vm.Layout(grid=[[0,1],[0,2]])`                        |
| <img src="../../../assets/user_guides/layout/one_top_two_bottom_color.png" alt="two rows with the top as a single component and the bottom divided into two components" width="400"/>                                   | <img src="../../../assets/user_guides/layout/1t_2b_grid.png" alt="layout=vm.Layout(grid=[[0,0],[1,2]])" width="100"/>       | `layout=vm.Layout(grid=[[0,0],[1,2]])`                        |
| <img src="../../../assets/user_guides/layout/two_top_one_bottom_color.png" alt="two rows with the top divided into two columns where each holds one component, and the bottom as a single component" width="400"/>      | <img src="../../../assets/user_guides/layout/2t_1b_grid.png" alt="layout=vm.Layout(grid=[[0,1],[2,2]])" width="100"/>       | `layout=vm.Layout(grid=[[0,1],[2,2]])`                        |
| <img src="../../../assets/user_guides/layout/one_left_three_right_color.png" alt="two columns where the left is a single component and the right is a set of three horizontally stacked components" width="400"/>       | <img src="../../../assets/user_guides/layout/1l_3r_grid.png" alt="layout=vm.Layout(grid=[[0,1],[0,2],[0,3]])" width="100"/> | `layout=vm.Layout(grid=[[0,1],[0,2],[0,3]])`                  |
| <img src="../../../assets/user_guides/layout/two_left_two_right_color.png" alt="two rows where each row is two components" width="400"/>                                                                                | <img src="../../../assets/user_guides/layout/2t_2b_grid.png" alt="layout=vm.Layout(grid=[[0,1],[2,3]])" width="100"/>       | `layout=vm.Layout(grid=[[0,1],[2,3]])`                        |
| <img src="../../../assets/user_guides/layout/three_left_one_right_color.png" alt="two columns where the left is a set of three horizontally stacked components and the right is a single component" width="400"/>       | <img src="../../../assets/user_guides/layout/3l_1r_grid.png" alt="layout=vm.Layout(grid=[[0,3],[1,3],[2,3]])" width="100"/> | `layout=vm.Layout(grid=[[0,3],[1,3],[2,3]])`                  |
| <img src="../../../assets/user_guides/layout/one_top_three_bottom_color.png" alt="two rows where the top is a single component and the bottom is three separate components" width="400"/>                               | <img src="../../../assets/user_guides/layout/1t_3b_grid.png" alt="layout=vm.Layout(grid=[[0,0,0],[1,2,3]])" width="100"/>   | `layout=vm.Layout(grid=[[0,0,0],[1,2,3]])`                    |
| <img src="../../../assets/user_guides/layout/three_top_one_bottom_color.png" alt="two rows where the top is three separate components and the bottom is a single component" width="400"/>                               | <img src="../../../assets/user_guides/layout/3t_1b_grid.png" alt="layout=vm.Layout(grid=[[0,1,2],[3,3,3]])" width="100"/>   | `layout=vm.Layout(grid=[[0,1,2],[3,3,3]])`                    |

<!--vale on -->

### Add empty sections

One approach to organize the dashboard's layout involves integrating empty sections by specifying `-1` within the grid layout.

```python title="Example"
grid = [[0, 1, -1], [0, 2, -1]]
```

!!! example "Adding Empty Spaces"
    === "app.py"
        ```{.python pycafe-link}
        import vizro.models as vm
        from vizro import Vizro

        page = vm.Page(
            title="Adding empty spaces",
            layout=vm.Layout(grid=[[0, 1, -1],
                                   [0, 2, -1]]),
            components=[vm.Card(text="""# Component 0"""),
                        vm.Card(text="""# Component 1"""),
                        vm.Card(text="""# Component 2"""),
                        ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

    === "app.yaml"
        ```yaml
        # Still requires a .py to add data to the data manager and parse YAML configuration
        # See yaml_version example
        pages:
          - components:
              - text: |
                  # Component 0
                type: card
              - text: |
                  # Component 1
                type: card
              - text: |
                  # Component 2
                type: card
            layout:
              grid: [[0, 1, -1], [0, 2, -1]]
            title: Adding empty spaces
        ```

    === "Result"
        [![GridEmpty]][gridempty]

### Control the scroll behavior

By default, the grid fits all charts/components on the screen. This can lead to distortions such that the chart/component looks squashed. To control the scroll behavior, you can specify the following:

- `row_min_height`: Sets a chart/component's minimum height. Defaults to 0px.
- `col_min_width`: Sets a chart/component's minimum width. Defaults to 0px.

!!! example "Activate Scrolling"
    === "app.py"
        ```{.python pycafe-link}
        import vizro.models as vm
        from vizro import Vizro

        page = vm.Page(
            title="Activate scrolling",
            layout=vm.Layout(grid=[[i] for i in range(8)],
                             row_min_height="240px"),
            components=[vm.Card(text="""# Component 0"""),
                        vm.Card(text="""# Component 1"""),
                        vm.Card(text="""# Component 2"""),
                        vm.Card(text="""# Component 3"""),
                        vm.Card(text="""# Component 4"""),
                        vm.Card(text="""# Component 5"""),
                        vm.Card(text="""# Component 6"""),
                        vm.Card(text="""# Component 7"""),
                        ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

    === "app.yaml"
        ```yaml
        # Still requires a .py to add data to the data manager and parse YAML configuration
        # See yaml_version example
        pages:
          - components:
              - text: |
                  # Component 0
                type: card
              - text: |
                  # Component 1
                type: card
              - text: |
                  # Component 2
                type: card
              - text: |
                  # Component 2
                type: card
              - text: |
                  # Component 4
                type: card
              - text: |
                  # Component 5
                type: card
              - text: |
                  # Component 6
                type: card
              - text: |
                  # Component 7
                type: card
            layout:
              grid: [[0], [1], [2], [3], [4], [5], [6], [7]]
              row_min_height: 240px
            title: Activate scrolling
        ```

    === "Result"
        [![GridScroll]][gridscroll]

### Further customization

For further customization, such as changing the gap between row and column, refer to the documentation of the [`Layout`][vizro.models.Layout] model.

## Flex Layout

The [Flex][vizro.models.Flex] layout offers a dynamic and flexible way to organize components within a page. Built on the CSS Flexbox model, it is specifically designed to create responsive layouts that seamlessly adjust to varying screen sizes and available space.

Unlike the [Grid][vizro.models.Layout] layout, which uses a predefined row-and-column structure, the `Flex` layout provides greater flexibility by allowing components to resize, align, and position themselves dynamically based on the layout configuration.

If you're new to Flexbox, we strongly recommend exploring [An Interactive Guide to Flexbox](https://www.joshwcomeau.com/css/interactive-guide-to-flexbox/). This tutorial provides a visual introduction to the core concepts of Flexbox, making it easier to understand how to leverage the `Flex` layout effectively.

### Flex - basic example

To switch to a `Flex` layout, simply pass `vm.Flex()` to the `layout` argument of the [Page][vizro.models.Page]. This replaces the default `Grid` layout with a `Flex` layout, where components (flex items) are arranged vertically (`direction="column"`), remain on a single line (`wrap=False`), and have a default spacing (`gap=24px`) between them.

!!! example "Flex - basic example"
    === "app.py"
        ```{.python pycafe-link}
        import vizro.models as vm
        from vizro import Vizro
        import vizro.plotly.express as px

        tips = px.data.tips()

        page = vm.Page(
            title="Flex - basic example",
            layout=vm.Flex(),
            components=[vm.Graph(figure=px.violin(tips, y="tip", x="day", color="day")) for i in range(3)],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

    === "app.yaml"
        ```yaml
        # Still requires a .py to add data to the data manager and parse YAML configuration
        # See yaml_version example
        pages:
          - components:
              - figure:
                  _target_: violin
                  x: day
                  y: tip
                  color: day
                  data_frame: tips
                type: graph
              - figure:
                  _target_: violin
                  x: day
                  y: tip
                  color: day
                  data_frame: tips
                type: graph
              - figure:
                  _target_: violin
                  x: day
                  y: tip
                  color: day
                  data_frame: tips
                type: graph
            layout:
              type: flex
            title: Flex - basic example
        ```

    === "Result"
        [![FlexBasic]][flexbasic]

### Flex - advanced example

If you want to customize the default behavior, the [Flex][vizro.models.Flex] model allows you to configure three optional arguments:

- `direction`: Defines the layout direction of the components within the flex container, determining whether they are arranged in rows or columns.
- `gap`: Controls the spacing between components in the flex container, enabling you to set consistent horizontal and vertical spacing between items.
- `wrap`: Determines whether components should wrap onto multiple lines or remain on a single line when there isn't enough space in the container.

!!! example "Flex - advanced example"
    === "app.py"
        ```{.python pycafe-link}
        import vizro.models as vm
        from vizro import Vizro
        import vizro.plotly.express as px

        tips = px.data.tips()

        page = vm.Page(
            title="Flex - advanced example",
            layout=vm.Flex(direction="row", gap="40px", wrap=True),
            components=[vm.Graph(figure=px.violin(tips, y="tip", x="day", color="day")) for i in range(3)],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

    === "app.yaml"
        ```yaml
        # Still requires a .py to add data to the data manager and parse YAML configuration
        # See yaml_version example
        pages:
          - components:
              - figure:
                  _target_: violin
                  x: day
                  y: tip
                  color: day
                  data_frame: tips
                type: graph
              - figure:
                  _target_: violin
                  x: day
                  y: tip
                  color: day
                  data_frame: tips
                type: graph
              - figure:
                  _target_: violin
                  x: day
                  y: tip
                  color: day
                  data_frame: tips
                type: graph
            layout:
              type: flex
              direction: row
              gap: 40px
              wrap: true
            title: Flex - advanced example
        ```

    === "Result"
        [![FlexAdvanced]][flexadvanced]

### Change the size of flex-items

There may be times when resizing your flex items is necessary, such as when designing for different screen sizes or combining elements with diverse content types (e.g., charts, text, or images).

You can achieve this by either specifying the `width` and `height` directly on the components or, if you're comfortable, applying custom CSS.

#### Change size via component's arguments

The syntax for setting `width` and `height` varies between components. Refer to the component's documentation for the correct syntax and usage, such as:

- `Graph`: See the documentation on [Plotly - Adjust Graph Size in Python](https://plotly.com/python/setting-graph-size/).
- `AgGrid`: See the documentation on [Dash - Change Grid Size](https://dash.plotly.com/dash-ag-grid/grid-size)
- `DataTable`: See the documentation on [Dash - Setting Table Height](https://dash.plotly.com/datatable/height#setting-table-height-with-vertical-scroll)
- `Card`: See our documentation on [Card - The extra argument](https://vizro.readthedocs.io/en/stable/pages/user-guides/card/#the-extra-argument)

!!! example "Change the width for Graph"
    === "app.py"
        ```{.python pycafe-link}
        import vizro.models as vm
        from vizro import Vizro
        import vizro.plotly.express as px

        tips = px.data.tips()

        page = vm.Page(
            title="Change the width for Graph",
            layout=vm.Flex(direction="row", gap="40px", wrap=True),
            components=[vm.Graph(figure=px.violin(tips, y="tip", x="day", color="day", width=400)) for i in range(5)],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

    === "app.yaml"
        ```yaml
        # Still requires a .py to add data to the data manager and parse YAML configuration
        # See yaml_version example
        pages:
          - components:
              - figure:
                  _target_: violin
                  x: day
                  y: tip
                  color: day
                  data_frame: tips
                  width: 400
                type: graph
              - figure:
                  _target_: violin
                  x: day
                  y: tip
                  color: day
                  data_frame: tips
                  width: 400
                type: graph
              - figure:
                  _target_: violin
                  x: day
                  y: tip
                  color: day
                  data_frame: tips
                  width: 400
                type: graph
              - figure:
                  _target_: violin
                  x: day
                  y: tip
                  color: day
                  data_frame: tips
                  width: 400
                type: graph
              - figure:
                  _target_: violin
                  x: day
                  y: tip
                  color: day
                  data_frame: tips
                  width: 400
                type: graph
            layout:
              type: flex
              direction: row
              gap: 40px
              wrap: true
            title: Change the width for Graph
        ```

    === "Result"
        [![FlexItemSizeArg]][flexitemsizearg]

#### Change size via custom CSS

Custom CSS is often a better choice than setting sizes through component arguments when you need to apply a consistent `height` and/or `width` across multiple elements without repeating code. This is especially helpful for ensuring uniform sizing of all flex items.

Each item within the `Flex` layout is wrapped in a `Div` with the `classname="flex-item"`, which can be targeted with CSS. For more information on identifying the correct selectors, refer to our [user guide on custom CSS](custom-css.md).

!!! example "Customizing CSS properties in selective components"
    === "my_css_file.css"
        ```css
        /* Apply styling to all flex items */
        #page-with-uniform-flex-items .flex-item {
            width: 260px;
        }
        ```

    === "app.py"
        ```py
        import vizro.models as vm
        from vizro import Vizro

        page = vm.Page(
            id="page-with-uniform-flex-items",
            title="Change the width via CSS",
            layout=vm.Flex(direction="row", wrap=True),
            components=[
                vm.Card(
                    text="""
                       # Lorem Ipsum

                       Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam sed elementum ligula.
                       In ultricies est ac mauris vehicula fermentum. Curabitur faucibus elementum lectus.
                       Name ut ipsum tortor. Praesent ut nulla risus. Praesent in dignissim nulla.
                   """
                )
                for i in range(12)
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        ```

        <img src=https://py.cafe/logo.png alt="PyCafe logo" width="30"><b><a target="_blank" href="https://py.cafe/vizro-official/vizro-custom-card-styling">Run and edit this code in PyCafe</a></b>

    === "Result"
        [![FlexItemSizeCSS]][flexitemsizecss]

## Alternative layout approaches

In general, any arbitrarily granular layout can already be achieved using [`Page.layout`](layouts.md) alone and is our recommended approach if you want to arrange components on a page with consistent row and/or column spacing.

!!! note "Alternative layout approaches: `Tabs` and `Containers`"
    [`Tabs`][vizro.models.Tabs] and [`Containers`][vizro.models.Container] provide alternative methods for customizing your page layout. For instance, if you need more granular control, want to break the overall page grid into subgrids, or wish to visually distinguish your subgrid, refer to our [user guide on Containers](container.md).

![tabs](../../assets/user_guides/components/tabs-info.png){ width="500" }

[flexadvanced]: ../../assets/user_guides/layout/flex_advanced.png
[flexbasic]: ../../assets/user_guides/layout/flex_basic.png
[flexitemsizearg]: ../../assets/user_guides/layout/flex_item_size_args.png
[flexitemsizecss]: ../../assets/user_guides/layout/flex_item_size_css.png
[grid]: ../../assets/user_guides/layout/one_left_two_right.png
[gridadv]: ../../assets/user_guides/layout/grid_advanced.png
[gridempty]: ../../assets/user_guides/layout/layout_empty_spaces.png
[gridscroll]: ../../assets/user_guides/layout/grid_scroll.png
[layout]: ../../assets/user_guides/layout/two_left.png
