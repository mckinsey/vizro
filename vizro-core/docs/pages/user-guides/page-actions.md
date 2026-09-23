---
description: "Customize what runs when a page opens with `Page.actions`: keep the default figure refresh, add a notification, or defer loading expensive data."
---

# How to run actions when a page opens

By default, every [`Page`][vizro.models.Page] runs an action when it opens or reloads that refreshes all of its charts, tables, figures and [dynamic filters](data.md#filters) against the current values of the page's [controls](controls.md). This is the same [`update_targets`](actions.md#refresh-figures-on-demand) mechanism that runs when a control changes.

You can customize this behavior with the `actions` argument of [`Page`][vizro.models.Page]. When you set `Page.actions`, your [actions chain](actions.md#multiple-actions) runs on page load **in place of** the automatic refresh. This lets you:

- run extra actions on page load, such as a welcome [notification](notification-actions.md), while still refreshing figures, and
- turn the automatic refresh off entirely, which is useful to defer loading expensive data until the user asks for it.

!!! note

    Because your actions **replace** the default, include [`va.update_targets()`](actions.md#refresh-figures-on-demand) in your chain if you still want figures to refresh when page loads. If you leave `actions` unset, the default on-page-load refresh is added for you as before.

## Run extra actions on page load

To keep the default figure refresh and also do something else, list [`va.update_targets()`](actions.md#refresh-figures-on-demand) first and then chain your other actions. The example below refreshes the page and then shows a welcome [notification](notification-actions.md).

!!! example "Actions on page load"

    === "app.py"

        ```{.python pycafe-link hl_lines="14"}
        import vizro.actions as va
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro

        df = px.data.iris()

        page = vm.Page(
            title="Welcome notification",
            components=[
                vm.Graph(figure=px.bar(df, x="species", y="sepal_length", color="species")),
            ],
            controls=[vm.Filter(column="species")],
            actions=[va.update_targets(), va.show_notification(text="Welcome! Data refreshed for this page.")],
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
              - type: graph
                figure:
                  _target_: bar
                  data_frame: iris
                  x: species
                  y: sepal_length
                  color: species
            controls:
              - type: filter
                column: species
            actions:
              - type: update_targets
              - type: show_notification
                text: "Welcome! Data refreshed for this page."
            title: Welcome notification
        ```

    === "Result"

        The dashboard shows a welcome notification each time the page opens, and the figure is refreshed as usual.

        [![PageActionsShowNotificationOnPageLoad]][pageactionsshownotificationonpageload]

## Defer loading expensive data

If a page queries a large or slow data source, you might not want it to load automatically every time the page opens. Set `actions=None` or `actions=[]` to switch off the automatic on-page-load refresh, then let the user load the data on demand, for example with a [`Button`][vizro.models.Button] that triggers [`va.update_targets()`](actions.md#refresh-figures-on-demand).

!!! example "Load on demand"

    === "app.py"

        ```{.python pycafe-link hl_lines="15"}
        import vizro.actions as va
        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro

        df = px.data.iris()

        page = vm.Page(
            title="Load on demand",
            components=[
                vm.Graph(figure=px.scatter(df, x="sepal_width", y="sepal_length", color="species")),
                vm.Button(text="Load data", actions=va.update_targets()),
            ],
            controls=[vm.Filter(column="species", selector=vm.Checklist(actions=None))],  # (1)!
            actions=None,  # (2)!
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

        1. `actions=[]` or `actions=None` set on filter's selector disables refreshing the graph when its value changes, so the figure is not populated until the user clicks the button.
        1. `actions=[]` or `actions=None` disables the automatic on-page-load refresh, so the figure is not populated until the user clicks the button.

    === "app.yaml"

        ```yaml
        # Still requires a .py to add data to the data manager and parse YAML configuration
        # See yaml_version example
        pages:
          - components:
              - type: graph
                figure:
                  _target_: scatter
                  data_frame: iris
                  x: sepal_width
                  y: sepal_length
                  color: species
              - type: button
                text: Load data
                actions:
                  - type: update_targets
            controls:
              - type: filter
                column: species
                selector:
                  type: checklist
                  actions: []
            actions: []
            title: Load on demand
        ```

    === "Result"

        The figure stays empty when the page opens and is populated only after the user clicks "Load data".

        [![PageActionsDeferOnPageLoad]][pageactionsdeferonpageload]

!!! warning

    When you disable the on-page-load refresh with `actions=None` or `actions=[]`, [dynamic filters](data.md#filters) do not recompute their options when the page opens; they refresh only once an [`update_targets`](actions.md#refresh-figures-on-demand) action runs, for example from a button or the "Reset all" button. Use static filters if you want their options available immediately.

[pageactionsshownotificationonpageload]: ../../assets/user_guides/page_actions/page_actions_show_notification_on_page_load.png
[pageactionsdeferonpageload]: ../../assets/user_guides/page_actions/page_actions_defer_on_page_load.gif
