# Actions

Actions control how your app responds to user input such as clicking a button or a point on a graph. Vizro provides [built-in actions](../user-guides/actions.md) and also enables you to write your own [custom actions](../user-guides/custom-actions.md).

Vizro's actions are built on top of [Dash callbacks](https://dash.plotly.com/basic-callbacks), but you do not need to know anything about Dash to use them. This page [explains more about how Vizro actions work](../explanation/actions-explanation.md) and their similarities and differences compared to Dash callbacks.

## What is an action?

There are two aspects to every Vizro app:

- Layout. This controls _what your app looks like_, for example which components you would like to see on your pages and where to place them. Under the hood, this uses [Dash layout](https://dash.plotly.com/layout).
- Interactivity. This controls _how your app behaves in response to user input_, for example what happens when someone clicks a button in your app. This uses _actions_, which under the hood use [Dash callbacks](https://dash.plotly.com/basic-callbacks).

Vizro models such as `vm.Graph`, `vm.Filter`, `vm.Button` and `vm.Page` configure both the layout and interactivity. For example, the [`vm.Filter`](../user-guides/filters.md) model configures both the layout and the interactivity of a filter. The `selector` argument configures which selector component (such as a dropdown or checklist) to render on screen. There's also an `actions` argument that configures what happens when a user changes the value of the selector. You generally don't set this `actions` argument because by default it is set to a filtering action that updates components on the page that depend on the column being filtered.

Many [Vizro models][vizro.models] have an `actions` argument that can contain one or more actions. Each action is a Python function that is _triggered_ when a user interacts with a component. This function can depend on _inputs_ from the user's screen and update _outputs_ on the user's screen.

In Vizro, there are two types of action:

- [Built-in actions](../user-guides/actions.md). These cover many common dashboard operations such as downloading data and cross-filtering. These actions can be imported from `vizro.actions`.
- [Custom actions](../user-guides/custom-actions.md). These are written by a dashboard developer to achieve behavior outside of Vizro's built-in actions and use the [`Action` model][vizro.models.Action].

!!! note

    Do you have an idea for a built-in action? Submit a [feature request](https://github.com/mckinsey/vizro/issues/new?template=feature-request.yml)!
