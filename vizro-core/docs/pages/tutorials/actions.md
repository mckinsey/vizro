# Write your own custom actions

In this tutorial, you will learn...

!!! note

    This tutorial assumes a basic knowledge of Vizro. If you haven't already done so, you should get started with Vizro in the [first dashboard tutorial](first-dashboard.md) or work through a [more in-depth tutorial](explore-components.md).

## What is an action?

Vizro models such as `vm.Dashboard`, `vm.Page`, `vm.Graph` and `vm.Filter` configure two separate parts of your app:

* Layout. This controls _what your app looks like_, for example which components you would like to see on your pages and where to place them. Under the hood, this uses [Dash layout](https://dash.plotly.com/layout).
* Interactivity. This controls _how your app behaves in response to user input_, for example what happens when someone clicks a button in your app. This uses _actions_, which under the hood use [Dash callbacks](https://dash.plotly.com/basic-callbacks).

For example, the [`vm.Filter`](../user-guides/filters.md) model configures both the layout and the interactivity of a filter. The `selector` argument configures which selector component (such as a dropdown or checklist) to render on screen. There's also an `actions` argument that configures what happens when a user changes the value of the selector. You generally don't set this `actions `argument because by default it is set to a filtering action that updates components on the page that depend on the column being filtered. 

Many Vizro models have an `actions` argument that can contain one or more actions. Each action is a Python function that is _triggered_ when a user interacts with a component. This function can depend on _inputs_ from the user's screen and update _outputs_ on the user's screen.

In Vizro, there are two types of action:

* [Built-in actions](../user-guides/actions.md). These cover many common dashboard operations such as downloading data and cross-filtering. These actions can be imported from `vizro.actions`.
* [Custom actions](../user-guides/custom-actions.md). These are written by a user to achieve behaviour outside of Vizro's built-in actions.

!!! note

    Do you have an idea for a built-in action that you think would be useful for many Vizro users? Let us know by submitting a [feature request](https://github.com/mckinsey/vizro/issues/new?template=feature-request.yml)!

This tutorial mainly concerns how to write your own custom actions, although you will also gain a better understanding of how Vizro's built-in actions work. You do not need to know anything about Dash callbacks to complete the tutorial other than the section on [combining Dash callbacks and Vizro actions](...). If you are already familiar with Dash callbacks then you might like to read our [explanation of how Vizro actions compare to Dash callbacks](...).

## A simple action

Let's start with a very simple single-page app that contains a [button](../user-guides/button.md) and some [text](../user-guides/text.md).

!!! example "App layout"

    === "app.py"

        ```{.python pycafe-link}
        import vizro.models as vm
        from vizro import Vizro
        
        page = vm.Page(
            title="My first custom action",
            layout=vm.Flex(),
            components=[
                vm.Button(),
                vm.Text(text="Click the button"),
            ],
        )
        
        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

    === "Result"

        TODO screenshot

??? details

    We haven't yet defined any actions, but behind the scenes Vizro has already defined some Dash callbacks for you:
    * A callback to change the dashboard theme when the theme selector is toggled. 
    * A callback associated with [Dash pages](https://dash.plotly.com/urls) that will make the app work when more pages are added.

    While developing, you can see all the Dash callbacks in Dash dev tool's [callback graph](https://dash.plotly.com/devtools#callback-graph). This is shown when running in debug mode with [`run(debug=True)`](../user-guides/run-deploy.md#/#automatic-reloading-and-debugging).

    TODO screenshot

    For a large or complex app, the callback graph quickly grows and becomes difficult to navigate. To make debugging easier you can temporarily comment out all but one page in your app to show only the relevant callbacks in the graph. 


TODO tip somewhere When debugging, it can also be very useful to insert a breakpoint inside the code of an action.  [VS Code](https://code.visualstudio.com/docs/debugtest/debugging#_breakpoints) 

So far we have specified that a button should be included in the page layout but haven't configured what should happen when the button is clicked. Let's define an action for that.

!!! example "A simple action"

    === "app.py"

        ```{.python pycafe-link hl_lines="3-13 21-24 26"}
        import vizro.models as vm
        from vizro import Vizro
        from vizro.models.types import capture
        
        from datetime import datetime
        
        
        @capture("action")  # (1)!
        def update_text():  # (2)!
            time_format = "%H:%M:%S"
            now = datetime.now()
            time = now.strftime(time_format)
            return f"The time is {time}"  # (3)!
        
        
        page = vm.Page(
            title="My first custom action",
            layout=vm.Flex(),
            components=[
                vm.Button(
                    actions=vm.Action(  # (4)!
                        function=update_text(),
                        outputs="time_text",
                    )
                ),
                vm.Text(id="time_text", text="Click the button"),  # (5)!
            ],
        )
        
        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

        1. You can write a simple action using the `capture("action")` decorator. This prepares a function to be used as a Vizro action.
        2. For now, the `update_text` function has no arguments.
        3. An action doesn't need to have outputs, but this one returns a string. An action can return values of any Python type that can be converted to JSON.
        4. We attach the action to the `vm.Button` model using the `actions` argument. We call the action function with `function=update_text()` (remember the `()`) and set the output to `"time_text"`.
        5. To use the `vm.Text` as an output, we supply `id="time_text"` that matches onto the action's `outputs`. It does not matter that this component is defined after the `vm.Action` that uses it.

    === "Result"

        TODO screenshot

Congratulations on writing your first action! Before clicking the button, the text shows "Click the button". When you click the button, the `update_text` action is triggered. This Python function executes on the server to find the current time and return a string "The time is ...". The resulting value is sent back to the user's screen and updates the text of the component with `id="time_text"`. As explained in the [Dash documentation](https://dash.plotly.com/basic-callbacks), this is called _reactive programming_.

## Runtime input

Now we will see how you can add a _runtime input_ to your actions. A runtime input is the value or _state_ of a component on the user's screen while the dashboard is running. What this means will soon become clear by extending our example! As before, let's start by adding something to the layout and then consider how to extend our action. Here we create a small form by adding a [`Switch`][vizro.models.Switch] to the layout that lets the user specify whether they would like to use a 12- or 24-hour clock.

!!! example "Add `Switch` to layout"

    === "app.py"

        ```{.python pycafe-link hl_lines="16 22-26"}
        import vizro.models as vm
        from vizro import Vizro
        from vizro.models.types import capture
        
        from datetime import datetime
        
        
        @capture("action")
        def update_text():
            time_format = "%H:%M:%S"
            now = datetime.now()
            time = now.strftime(time_format)
            return f"The time is {time}"
        
        
        vm.Container.add_type("components", vm.Switch)  # (1)!
        
        page = vm.Page(
            title="My first custom action",
            layout=vm.Flex(),
            components=[
                vm.Container(  # (2)!
                    layout=vm.Flex(direction="row"),
                    variant="outlined",
                    components=[
                        vm.Switch(id="clock_switch", title="24-hour clock", value=True),  # (3)!
                        vm.Button(
                            actions=vm.Action(
                                function=update_text(),
                                outputs="time_text",
                            ),
                        ),
                    ],
                ),
                vm.Text(id="time_text", text="Click the button"),
            ],
        )
        
        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

        1. Currently [`Switch`][vizro.models.Switch] is designed to be used as a [control selectors](../user-guides/selectors.md). In future, Vizro will have a dedicated `Form` model for the creation of forms. For now, we add them directly as `components` inside a [`Container`][vizro.models.Container]. For this to be a valid configuration we must first do `add_type` as for a [custom component](../user-guides/custom-components.md).
        2. We group the form inputs into a [styled container](../user-guides/container.md#styled-containers) to achieve some visual separation of the form inputs and outputs. This is purely stylistic and does not affect the operation of actions.
        3. We have already set `id` for the `Switch` in anticipation of it being used in `update_text`. 
        
    === "Result"

           TODO screenshot

Now we need to connect `vm.Switch(id="clock_switch")` to our `update_text` action. We add an argument `use_24_hour_clock` to the `update_text` function and configure the function call in `vm.Action` to link this argument to the `clock_switch` component.

!!! example "Connect `Switch` to `update_text`"

    === "app.py"

        ```{.python pycafe-link hl_lines="9-10 29"}
        import vizro.models as vm
        from vizro import Vizro
        from vizro.models.types import capture
          
        from datetime import datetime
        
        
        @capture("action")
        def update_text(use_24_hour_clock):   # (1)!
             time_format = "%H:%M:%S" if use_24_hour_clock else "%I:%M:%S %p"   # (2)!
             now = datetime.now()
             time = now.strftime(time_format)
             return f"The time is {time}"
        
        
        vm.Container.add_type("components", vm.Switch)
        
        page = vm.Page(
             title="My first custom action",
             layout=vm.Flex(),
             components=[
                 vm.Container(
                     layout=vm.Flex(direction="row"),
                     variant="outlined",
                     components=[
                         vm.Switch(id="clock_switch", title="24-hour clock", value=True),
                         vm.Button(
                             actions=vm.Action(
                                 function=update_text(use_24_hour_clock="clock_switch"),  # (3)!
                                 outputs="time_text",
                             ),
                         ),
                     ],
                 ),
                 vm.Text(id="time_text", text="Click the button"),
             ],
        )
        
        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

        1. We add an argument `use_24_hour_clock` to `update_text`. This will receive a boolean value `True` or `False`.
        2. `time_format` now changes depending on the the value of `use_24_hour_clock`.
        3. The argument `use_24_hour_clock` is _bound_ at runtime to the value of the `clock_switch` component. This will be `True` or `False` depending on whether the switch is toggled on or off. Here we used keyword argument as `update_text(use_24_hour_clock="clock_switch")` but, just like a normal Python function call, we could also use a positional argument as `update_text("clock_switch")`.
          
    === "Result"

        TODO screenshot

Note that toggling the `clock_switch` does not by itself trigger `update_text`. The switch is used as a runtime input but the action is triggered only by clicking the button. In fact, this is a key principle governing Vizro actions: **an action can have any number of inputs and outputs but only one trigger**.  

TODO
In Vizro there are two types of runtime input.
Refer later to see what other non-runtime inputs might be
Put all that stuff later?

## Multiple inputs and outputs

We have just said that an action can have any number of inputs and outputs, so let's extend our example to show how this works. Now we will have two inputs that the user can configure before clicking the button and two outputs that are updated simultaneously.

!!! example "Multiple inputs and outputs"

    === "app.py"

        ```{.python pycafe-link hl_lines="9 11 14-15 19 30 33 34 40"}
        import vizro.models as vm
        from vizro import Vizro
        from vizro.models.types import capture
        
        from datetime import datetime
        
        
        @capture("action")
        def update_text(use_24_hour_clock, date_format):  # (1)!
             time_format = "%H:%M:%S" if use_24_hour_clock else "%I:%M:%S %p"
             date_format = "%d/%m/%y" if date_format == "DD/MM/YY" else "%m/%d/%y"
             now = datetime.now()
             time = now.strftime(time_format)
             date = now.strftime(date_format)
             return f"The time is {time}", f"The date is {date}"  # (2)!
        
        
        vm.Container.add_type("components", vm.Switch)
        vm.Container.add_type("components", vm.RadioItems)
        
        page = vm.Page(
             title="My first custom action",
             layout=vm.Flex(),
             components=[
                 vm.Container(
                     layout=vm.Flex(direction="row"),
                     variant="outlined",
                     components=[
                         vm.Switch(id="clock_switch", title="24-hour clock", value=True),
                         vm.RadioItems(id="date_selector", options=["DD/MM/YY", "MM/DD/YY"]),
                         vm.Button(
                             actions=vm.Action(
                                 function=update_text(use_24_hour_clock="clock_switch", date_format="date_selector"),   # (3)!
                                 outputs=["time_text", "date_text"],   # (4)!
                             ),
                         ),
                     ],
                 ),
                 vm.Text(id="time_text", text="Click the button"),
                 vm.Text(id="date_text", text="Click the button"),
             ],
        )
        
        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

        1. We add an argument `date_format` to `update_text`. This will receive a string value `"DD/MM/YY"` or `"MM/DD/YY"`.
        2. We now return _two_ strings. It would work exactly the same if we returned a list `[f"The time is {time}", f"The date is {date}"]`. 
        3. The new argument `date_format` is bound to the `vm.RadioItems(date_selector)`.
        4. There are now two outputs: `time_text` and `date_text`.

    === "Result"

        TODO screenshot

The returned values are matched to the `outputs` in order. If your action has many outputs then it can be a good idea to instead return a dictionary where returned values are labelled by string keys. In this case, `outputs` should also be a dictionary with matching keys, and the order of entries does not matter. For example:

```py
@capture("action")
def update_text(use_24_hour_clock, date_format):
    ...
    return {"time_output": f"The time is {time}", "date_output": f"The date is {date}"}

...

vm.Action(
   function=update_text(use_24_hour_clock="clock_switch", date_format="date_selector"),
   outputs={"time_output": "time_text", "date_output": "date_text"},  # (1)!
)
```

1. `outputs={"date_output": "date_text", "time_output": "time_text"}` would work exactly the same; the order of entries does not matter.

## Actions chains

Sometimes you need a single trigger to execute multiple actions. Vizro uses _chains_ of actions to achieve this. There are two different types chains:
* Explicit action chains. When uou specify multiple actions as `actions=[action_1, action_2, ...]` then Vizro chains them together. These actions executed in sequence, so that `action_2` executes only when `action_1` has completed.
* Implicit action chains. Say that `actions=action_1` is triggered by clicking a button `vm.Button(id="submit")`. If CONTINUE HERE
* 
* 
* Even though an action can only have one    

mermaid diagram

```
import vizro.models as vm
from vizro import Vizro
from vizro.models.types import capture

from datetime import datetime


@capture("action")
def update_time_text(use_24_hour_clock):  # (1)!
    time_format = "%H:%M:%S" if use_24_hour_clock else "%I:%M:%S %p"
    now = datetime.now()
    time = now.strftime(time_format)
    return f"The time is {time}"


@capture("action")
def update_date_text(date_format):  # (1)!
    date_format = "%d/%m/%y" if date_format == "DD/MM/YY" else "%m/%d/%y"
    now = datetime.now()
    date = now.strftime(date_format)
    return f"The date is {date}"  # (2)!


vm.Container.add_type("components", vm.Switch)
vm.Container.add_type("components", vm.RadioItems)

page = vm.Page(
    title="My first custom action",
    layout=vm.Flex(),
    components=[
        vm.Container(
            layout=vm.Flex(direction="row"),
            variant="outlined",
            components=[
                vm.Switch(
                    id="clock_switch",
                    title="24-hour clock",
                    value=True,
                    actions=vm.Action(function=update_time_text(use_24_hour_clock="clock_switch"), outputs="time_text"),
                ),
                vm.RadioItems(
                    id="date_selector",
                    options=["DD/MM/YY", "MM/DD/YY"],
                    actions=vm.Action(function=update_date_text(date_format="date_selector"), outputs="date_text"),
                ),
            ],
        ),
        vm.Text(id="time_text", text="Click the switch"),
        vm.Text(id="date_text", text="Click the radio item"),
    ],
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()



```

PUT EXAMPLE OF ACTION IN SWITCH AS SOMETHING THAT SHOULDN'T NEED TO SPECIFY ID, LIKE CHAT 

The execution of one action 


`raise PreventUpdate` etc. what if first action crashes
execution of other actions in chain isolated, can only trigger first
Independent of Dash

warning about many chained callbacks and how it's many HTTP requests

reuse same upate_text action on both input components


implicit chaining, repeat update_text action on switch, explicit multiple actions in a chain as actions = [...] - make all this clearer
mention actions = [...] but don't worry about it much since might be removed. Could do by breaking update_text into two separate actions

## Trigger, input and output properties

Don't put this section here - too much Dash. Yes - just keep it simple and not talking about multiple properties and components here until gets more advanced.

A single Vizro model produces one or more Dash components, each of which has several properties. For example, the Dash component corresponding to `vm.Text` is [`dcc.Markdown`](https://dash.plotly.com/dash-core-components/markdown). The above examples' `vm.Text(id="time_text", text="Click the button")` produces something like the following Dash component:
```py
dcc.Markdown(id="time_text", children="Click the button")
```

To update the text shown in this component as an output in a Dash callback, you would refer to `Output("time_text", "children")`. In Vizro, you could instead refer to `outputs="time_text.children"`. However, to simplify the notation, Vizro offers several shorthands:
* `outputs="time_text.text"` where the format is `<model_id>.<argument_name>`. Here we update the `text` argument of the `vm.Text` model that has `id="time_text"`. 
* `outputs="time_text"` where the format is `<model_id>`. This automatically connects to the default Dash component property that is part of the Vizro model. The default depends on the Vizro model but corresponds to the most commonly used property. In this example it would target the `text` argument of the `vm.Text` model because that is the most common part to update. 

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

A Vizro action always uses a specific Dash component and property for the action trigger, runtime inputs and outputs. However, as explained in the [how to](...) you should prefer to use the Vizro shorthands where possible rather than referring to the underlying Dash components (for example, use `clock_switch.title` in preference to `clock_switch_title.children`). This is more intuitive and more stable. While using a pure Dash component `id` and property will remain possible in Vizro actions, we consider the exact underlying Dash components to be implementation details, and so the Dash components available and their `id`s may change between non-breaking Vizro releases.

!!! note

    Are you targetting an underlying Dash component that you think should be addressed by Vizro more easily? Let us know by submitting a [feature request](https://github.com/mckinsey/vizro/issues/new?template=feature-request.yml)!



serverside inefficient. here could be done frontend
stateless, users don't interfere so long as don't alter global variables - need to point to Dash explanation for this



to recap:
action contains inputs/outpust etc.
explain key principles of actions like single trigger

Example states input that uses filter - would need to implement something here first on vm.Filter

TODO THROUGHOUT refer to explanation for what Dash equivalent would look like

Some output field and property which isn't just model name
collapse - built in action will be much clearer
change tab
update tooltip
add alert
change page - not for now

---
Good example ideas:
CRUD
table as input
filter/parameter that updates text too
API call/run model example - simple calculation but not full model. Scenario from table example
database? save to file?
click on table to drilldown to product page like labs telemetry - even before proper interact

update tooltip
popup when selected rows clicked to do alert
remove selected rows and save to disk
download png button? Or download selected data?
clear selection button
want input/output aggrid?
output text
update graph description
select aggrid rows
editable table
remove rows, write to disk
could be parameter interaction even though built in
something where action doesn't work and we need Dash callback
trigger not there explicitly
filters populate options but only fetches data on submit
"sample button"
update and download
refresh page - yes, even if have it built into actions


Tutorial on drillthrough etc. Do want this even before it's properly built in and will remain useful because it shows how things work. Do this with controls in containers 
But do how to guide first since easier?
---

same date example that changes page and uses store 

state to store that's then used e.g. on a different page

toast alert for successful validation, clear form
change collapse of navigation accordion by default - something to do with opl

collapse/uncollapse all containers
text saying what controls are selected e.g. in graph header
live updates - refresh page
back button like in browser

check #vizro-users Petar answers - most recent one that Li asked about
check deepresearch summarising our issues
narrow down the options while user is typing: https://vizro-cnx-demo.alpha.mckinsey.digital/customer-view---germany

---
Teach as if to new vizro user not familiar with Dash first
Then compare to Dash in separate explanation

---
Where to put explanation?

---
I think "built in" and "custom" is the best terminology to use but we can also say "user-defined" since it makes sense. Let's avoid using "predefined" though. SEARCH FOR USAGE OF THIS



https://github.com/mckinsey/vizro/pull/1054
vizro_download, vizro_url  https://github.com/McK-Internal/vizro-internal/issues/1611
Y direct reference to component, field name https://github.com/McK-Internal/vizro-internal/issues/1610 https://github.com/McK-Internal/vizro-internal/issues/1609
Y dict output format https://github.com/McK-Internal/vizro-internal/issues/1608
Y single [action] allowed
Y single [output] allowed
built in special arguments (though structure of `_controls` not finalised)
two sorts of action (Abstract and normal)
actions chain 
callbacks + actions combined
page lifecyle - on page load, filter callback, etc.
YAML configuration of captured callable

drill through - probably don't document yet. Maybe write more about URL query params?

deprecations - do after

security - injection. CHeck Dash security guide

AgGrid inner ID - should be no examples like that to remove but check

tutorial more than how-to. Tutorial refers to more detail in explanation. Tutorial is learning-oriented
How to use built in actions and How to write a custom action. How to is task-oriented
explanation for Dash vs. vizro and actions loop
prevent_initial_call=True always

Reference for built in arguments, objects, properties/fields

NEED TO UPDATE ALL DOCS function=export_data() etc. Search throughout
Update all actions examples in docs that have unecssary [actions] or [outputs]

Vizro vs Dash notes
runtime input vs. state
trigger vs. input
vizro has built in actions
attach to trigger not define globally
need to provide id in Dash for trigger component
trigger not passed in
one vs multiple triggers



"""
