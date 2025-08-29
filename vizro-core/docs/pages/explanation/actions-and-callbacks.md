# Actions and Dash callbacks

Coming soon!

<!--

## Rough notes
Vizro vs Dash notes
runtime input vs. state
trigger vs. input
vizro has built in actions
attach to trigger not define globally
need to provide id in Dash for trigger component
trigger not passed in
duplicated outputs fine
one vs multiple triggers
prevent_initial_call=True always
actions loop
pattern matching callbacks

"I think using side-by-side examples when comparing would be very beneficial, for users who already know callbacks well, and especially for LLM to understand how these 2 systems differ and relate.
I.e., to achieve the same effect, how to write an action and what's the equivalent version using callbacks. Given llm can write callbacks very well - with comparison, llm should know how to write custom action accurately"

Explain how  can combine Dash callbacks and Vizro action, e.g. Vizro actions can use Dash components/properties so easy to adapt. Can have some additional clientside callbacks - give example from simple action.

Write Dash equivalent of simple vizro app
Show some output field and property which isn't just model name to show how can use Dash component/property

## Dash callback graph
??? details

    We haven't yet defined any actions, but behind the scenes Vizro has already defined some Dash callbacks for you:

    * A callback to change the dashboard theme when the theme selector is toggled.
    * A callback associated with [Dash pages](https://dash.plotly.com/urls) that will make the app work when more pages are added.

    While developing, you can see all the Dash callbacks in Dash dev tool's [callback graph](https://dash.plotly.com/devtools#callback-graph). This is shown when running in debug mode with [`run(debug=True)`](../user-guides/run-deploy.md#/#automatic-reloading-and-debugging).

    TODO screenshot

    For a large or complex app, the callback graph quickly grows and becomes difficult to navigate. To make debugging easier you can temporarily comment out all but one page in your app to show only the relevant callbacks in the graph.


## Trigger, input and output properties

Still needed given explanation in custom actions how to? Probably just a shortened version of it.

A single Vizro model produces one or more Dash components, each of which has several properties. For example, the Dash component corresponding to `vm.Text` is [`dcc.Markdown`](https://dash.plotly.com/dash-core-components/markdown). The above examples' `vm.Text(id="time_text", text="Click the button")` produces something like the following Dash component:
```py
dcc.Markdown(id="time_text", children="Click the button")
```

To update the text shown in this component as an output in a Dash callback, you would refer to `Output("time_text", "children")`. In Vizro, you could instead refer to `outputs="time_text.children"`. However, to simplify the notation, Vizro offers several shorthands:
* `outputs="time_text.text"` where the format is `<model_id>.<argument_name>`. Here we update the `text` argument of the `vm.Text` model that has `id="time_text"`.
* `outputs="time_text"` where the format is `<model_id>`. This automatically connects to the default Dash component property that is part of the Vizro model. The default depends on the Vizro model but corresponds to the most commonly used property. In this example it would address the `text` argument of the `vm.Text` model because that is the most common part to update.

The above two shorthands work exactly the same as the full `outputs="time_text.children"`.

Let's look at another example. The Dash component corresponding to `vm.Switch` is [`dbc.Switch`](https://www.dash-bootstrap-components.com/docs/components/input/). The above examples' `vm.Switch(id="clock_switch", title="24-hour clock", value=True)` produces something like the following:
```py
dbc.Switch(
    id="clock_switch",
    value=True,
    label=html.Span(id="clock_switch_title", children="24-hour-clock"),
)
```

As well as the "core" `dbc.Switch` component, the `vm.Switch` model produces a `html.Span` component to contain the label. When using `vm.Switch` model as an action trigger or runtime input (as in the examples' `use_24_hour_clock="clock_switch"`), the `value` of the switch is the default Dash component property. Hence `use_24_hour_clock="clock_switch"` is shorthand for `use_24_hour_clock="clock_switch.value"`.

If the `vm.Switch` is used as an output then there are multiple different Dash components and properties that could be updated:
* `outputs="clock_switch"` is equivalent to `outputs="clock_switch.value"` and updates the `value` of the `dbc.Switch`.
* `outputs="clock_switch.title` is equivalent to `outputs="clock_switch_title.children"` and updates the `title` of the `dbc.Switch`.

A Vizro action always uses a specific Dash component and property for the action trigger, runtime inputs and outputs. However, as explained in the [how to](...) you should prefer to use the Vizro shorthands where possible rather than referring to the underlying Dash components (for example, use `clock_switch.title` in preference to `clock_switch_title.children`). This is more intuitive and more stable. While using a pure Dash component `id` and property will remain possible in Vizro actions, we consider the exact underlying Dash components to be implementation details, and so the Dash components available may change between non-breaking Vizro releases.

!!! note

    Are you addressing an underlying Dash component that you think should be addressed by Vizro more easily? Let us know by submitting a [feature request](https://github.com/mckinsey/vizro/issues/new?template=feature-request.yml)!

### Moved from the user guide on actions "Address specific parts of a model"

In fact, whenever we refer to just a model `id` as an action's input or output, it is just shorthand for the full `<model_id>.<argument_name>`, with some appropriate default argument name chosen for the model. This default corresponds to the most common argument that you would use for an action's input and output. In the above example, the input `use_24_hour_clock="clock_switch"` is equivalent to writing `use_24_hour_clock="clock_switch.value"`, and the output `"time_text"` is equivalent to writing `"time_text.text"`. If you prefer to be explicit then you can write these full versions and the app will work exactly the same way.

Some arguments, or even whole models, are available for use as an action input but not output or vice versa. For example, `vm.Text` is available as an action output but not input.

...

In fact, Vizro's system of `<model_id>.<argument_name>` is just shorthand for the underlying Dash `<component_id>.<property>`. For example, `"clock_switch.title"` is equivalent to `"clock_switch_title.children"`. Wherever possible, you should prefer to use the Vizro shorthands rather than referring to the underlying Dash components (for example, use `"clock_switch.title"` in preference to `"clock_switch_title.children"`). This is more intuitive and more stable. While using a pure Dash component `id` and property will indefinitely remain possible in Vizro actions, we consider the exact underlying Dash components to be implementation details, and so the Dash components available may change between non-breaking Vizro releases.

...

Most Vizro models produce multiple Dash components, each of which has several properties. The above examples' `vm.Switch(id="clock_switch", title="24-hour clock", value=True)` produces something like the following:

```py
import dash_bootstrap_components as dbc
from dash import html

dbc.Switch(
    id="clock_switch",
    value=True,
    label=html.Span(id="clock_switch_title", children="24-hour-clock"),
)
```

As well as the "core" [`dbc.Switch` component](https://www.dash-bootstrap-components.com/docs/components/input/), the `vm.Switch` model produces a [`html.Span` component](https://dash.plotly.com/dash-html-components/span) to contain the value of the `title` argument. Sometimes there may be Dash components or properties that you wish to use as an action input or output that are not easily mapped onto Vizro model arguments. In this case, you should [consult the model's source code](https://github.com/mckinsey/vizro/tree/main/vizro-core/src/vizro/models) to find the relevant Dash component and property. Here, for example, we could use `outputs="clock_switch_title.style"` to change the `style`

The `id` of Dash components are always prefixed by the model `id`. For example, `vm.Graph(id="my_graph")` would produce Dash components with `id="my_graph_title"`, `id="my_graph_header"`, `id="my_graph_footer"`, and so on.

### Recap

To summarise the above sections on addressing specific parts of a model, we have seen the following equivalences:

- `"clock_switch"` is shorthand for `"clock_switch.value"`. In this case, the Vizro `<model_id>.<argument_name>` is the same as the underlying Dash `<component_name>.<property>`.
- `"time_text"` is shorthand for `"time_text.text"`, which itself refers to the underlying Dash property`"time_text.children"`.
- `"clock_switch.title"` is shorthand for (and should be used in preference to) the underlying Dash property `"clock_switch_title.children"`.

If you are already familiar with Dash then here are some other common equivalences that are useful to know:

- `"my_button"` is shorthand for the underlying Dash property `"my_button.n_clicks"`.
- `"my_graph` is shorthand for the underlying Dash property `"my_graph.figure"`.
- For all [selectors](selectors.md), `"my_selector"` is shorthand for the underlying Dash property `"my_selector.value"`.


"""Li comment: maybe put it inside a Table with Vizto shorthand / Dash equivalent"""



## Performance

Every Vizro action corresponds to an HTTP request, so that it takes some time for the client to communicate with the server. When you run your app locally, this delay not be noticeable, since the client and the server are running on the same computer, but when you [deploy your app](https://vizro.readthedocs.io/en/stable/pages/user-guides/run-deploy/#production) there is network latency introduced. This may or may not become a performance bottleneck for your app.

There is no upper limit to the length of actions chains (explicit or implicit). However, if you intend to deploy your app, it is best to keep them of a reasonable length. There is no hard and fast rule for what constitutes "reasonable", since it depends on many factors such as what your actions do, the amount of data transferred, the number of users of your app and your server setup. However, as a rough guide, it is usually best to avoid actions chains with more than five actions that run serially.

If you hit performance limits then you might like to consider using [Dash clientside callbacks](https://dash.plotly.com/clientside-callbacks). These execute purely on the clientside and do not perform an HTTP request, so there is no network latency. The code is written in JavaScript rather than Python. These callbacks live outside the Vizro actions system but are fully compatible with Vizro actions: you can write an app containing both Actions and Dash clientside callbacks.

## Statelessness

stateless, users don't interfere so long as don't alter global variables - need to point to Dash explanation for this
https://dash.plotly.com/sharing-data-between-callbacks#why-global-variables-will-break-your-app
includes `data_manager`



-->
