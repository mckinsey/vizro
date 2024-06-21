# How to create custom components

Vizro's public API is kept small to enable quick and easy configuration of a dashboard. However,
at the same time, Vizro is extensible, so that you can tweak any component to your liking or even create entirely new ones.

If you can't find a component that you would like to have in the code basis, or if you would like to alter/enhance an existing component, then you are in the right place.
This guide shows you how to create custom components that are completely new, or enhancements of existing ones.

In general, you can create a custom component based on any dash-compatible component (for example, [dash-core-components](https://dash.plotly.com/dash-core-components),
[dash-bootstrap-components](https://dash-bootstrap-components.opensource.faculty.ai/), [dash-html-components](https://github.com/plotly/dash/tree/dev/components/dash-html-components)).


All our components are based on `Dash`, and they are shipped with a set of sensible defaults that can be modified. If you would like to overwrite one of those defaults,
or if you would like to use extra `args` or `kwargs` of those components, then this is the correct way to include those. You can use any existing attribute of any underlying [Dash component](https://dash.plotly.com/#open-source-component-libraries) with this method.

!!!note

    There are always **three general steps** to consider to create a custom component:

    1. **Sub-class to create** your component
    2. **Enhance or build** the component (for example, to add/change model fields, overwrite pre-build/build method) to your desire
    3. **Check** if your component will be part of a discriminated union[^1]. If yes, then
        - you must ensure your component has a `type` field
        - you must register the new type with its parent model's relevant field (where the new component is entered into) with [`add_type`][vizro.models.VizroBaseModel.add_type]

    We will refer back to these three steps in the two examples below.

[^1]: You can check if your new component will be part of a discriminated union by consulting our [API reference on models](../API-reference/models.md). Check whether the relevant model field (for example, `selectors` in [`Filter`][vizro.models.Filter] or [`Parameter`][vizro.models.Parameter]) is described as a discriminated union (in this case the [`SelectorType`][vizro.models.types.SelectorType] is, but for example [`OptionsType`][vizro.models.types.OptionsType] is not).


## Extend an existing component
??? info "When to choose this strategy"

    You may want to use this strategy to:

    - extend an existing component (for example, to add a button to [`Card`][vizro.models.Card])
    - change configurations we have set by default (for example, to set `allowCross=False` in [`RangeSlider`][vizro.models.RangeSlider])
    - change any fields of any models (for example, to change the title field from `Optional` to have a default)


You can extend an existing component by sub-classing the component you want to alter. Remember that when sub-classing a component
you have access to all fields of all parent models, but you can choose to overwrite any field or method, or define new ones.

The aim for this example is to enhance the [`RangeSlider`][vizro.models.RangeSlider] model so that
one slider handle cannot cross the other, and to have a permanent tooltip showing the current value. You will note that it is often easier to call `super()` when overriding a complex method
such as the `build` method in the below example instead of attempting to write it from scratch.

In this case, the general three steps translate into:

1. Sub-class existing [`RangeSlider`][vizro.models.RangeSlider]:
```py
class TooltipNonCrossRangeSlider(vm.RangeSlider):
```

2. Enhance the component by changing the underlying parent `dcc.RangeSlider`:
```py
allowCross=False,
tooltip={"placement": "bottom", "always_visible": True}
```
These lines are highlighted in the example below. They are the only material change to the original `build` method.

3. Since the new model will be inserted into the `selectors` argument of the [`Filter`][vizro.models.Filter] or [`Parameter`][vizro.models.Parameter], it will be part of the discriminated union describing the allowed types for that argument, in this case the [`SelectorType`][vizro.models.types.SelectorType]. Hence we must:
    - define a new type:
```py
type: Literal["other_range_slider"] = "other_range_slider"
```
    - register the type with the parent model(s):
```py
vm.Filter.add_type("selector", TooltipNonCrossRangeSlider)
vm.Parameter.add_type("selector", TooltipNonCrossRangeSlider)
```



??? example "Example based on existing component"

    === "app.py"
        ``` py linenums="1" hl_lines="18 19"
        from typing_extensions import Literal

        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro

        iris = px.data.iris()


        # 1. Create custom component - here based on the existing RangeSlider
        class TooltipNonCrossRangeSlider(vm.RangeSlider):
            """Custom numeric multi-selector `TooltipNonCrossRangeSlider`."""

            type: Literal["other_range_slider"] = "other_range_slider"  # (1)!

            def build(self):  # (2)!
                range_slider_build_obj = super().build()  # (3)!
                range_slider_build_obj[self.id].allowCross = False  # (4)!
                range_slider_build_obj[self.id].tooltip = {"always_visible": True, "placement": "bottom"}  # (5)!
                return range_slider_build_obj


        # 2. Add new components to expected type - here the selector of the parent components
        vm.Filter.add_type("selector", TooltipNonCrossRangeSlider)  # (6)!
        vm.Parameter.add_type("selector", TooltipNonCrossRangeSlider)  # (7)!

        page = vm.Page(
            title="Custom Component",
            components=[
                vm.Graph(
                    id="for_custom_chart",
                    figure=px.scatter(iris, title="Iris Dataset", x="sepal_length", y="petal_width", color="sepal_width"),
                ),
            ],
            controls=[
                vm.Filter(
                    column="sepal_length",
                    targets=["for_custom_chart"],
                    selector=TooltipNonCrossRangeSlider(),
                ),
                vm.Parameter(
                    targets=["for_custom_chart.range_x"],
                    selector=TooltipNonCrossRangeSlider(title="Select x-axis range", min=0, max=10),  # (8)!
                ),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])

        Vizro().build(dashboard).run()
        ```

        1.  Here we provide a new type for the new component, so it can be distinguished in the discriminated union.
        2.  Here we override the `build` method by altering the output of `super().build()`. Alternatively one could copy the source code of the build method and alter it directly.
        3.  `range_slider_build_obj[self.id]` then fetches the underlying [`dcc.RangeSlider`](https://dash.plotly.com/dash-core-components/rangeslider) object.
        4.  This change prevents the `RangeSlider` from crossing itself when moving the handle.
        5.  This change displays the tooltip below the handle.
        6.  **Remember!** If part of a discriminated union, you must add the new component to the parent model where it will be inserted. In this case the new `TooltipNonCrossRangeSlider` will be inserted into the `selector` argument of the `Filter` model, and thus must be added as an allowed type.
        7.  **Remember!** If part of a discriminated union, you must add the new component to the parent model where it will be inserted. In this case the new `TooltipNonCrossRangeSlider` will be inserted into the `selector` argument of the `Parameter` model, and thus must be added as an allowed type.
        8.  The new component can now be inserted into a regular dashboard.

    === "yaml"
        ```yaml
        # Custom components are currently only possible via python configuration
        ```
    === "Result"
        [![CustomComponent1]][CustomComponent1]

    [CustomComponent1]: ../../assets/user_guides/custom_components/customcomponent_1.png


## Create a new component

??? info "When to choose this strategy"

    You may want to use this strategy to:

    - create a new component that does not exist in our library yet
    - make extensive changes to an existing component

You can create an entirely new component by sub-classing our [VizroBaseModel][vizro.models.VizroBaseModel]. Note that
using `VizroBaseModel` is mandatory if you want the new component to work in the Vizro framework.

The aim of the example is to create a [`Jumbotron`](https://dash-bootstrap-components.opensource.faculty.ai/docs/components/jumbotron/), a component that currently does not exist in Vizro's existing component range. It is a lightweight container to call attention to featured content or information.

???note "Note on `build` and `pre_build` methods"
    Note that when creating new components, you will need to define a `build` method like in the below example if it is a visual component that is rendered on the page. Examples of components with a `build` method are:

    - `selector` type: [`Checklist`][vizro.models.Checklist], [`Dropdown`][vizro.models.Dropdown], [`RadioItems`][vizro.models.RadioItems].
    - `component` type: [`Graph`][vizro.models.Graph], [`Card`][vizro.models.Card].

    For components that only create other components, you do not need to define a `build` method, for example, for [`Filter`][vizro.models.Filter] and [`Parameter`][vizro.models.Parameter].

    If you would like to have access to other components, you may want to define a `pre_build` method. This method is automatically run for all models and makes them internally consistent. Notable existing models
    with `pre_build` methods are [`Filter`][vizro.models.Filter] and [`Parameter`][vizro.models.Parameter].

In this case, the general steps translate for this example into:

1. Create new component, by sub-classing [VizroBaseModel][vizro.models.VizroBaseModel]:
```py
class Jumbotron(vm.VizroBaseModel):
```

2. Build the component using existing `dash` components.
```py
return html.Div(
        ...
    )
    ...
)
```
3. Since the new model will be inserted into the `components` argument of the [`Page`][vizro.models.Page], it will be part of the discriminated union describing the allowed types for that argument, in this case the [`ComponentType`][vizro.models.types.ComponentType]. Hence we must:
    - define a new type:
```py
type: Literal["jumbotron"] = "jumbotron"
```
    - register the type with the parent model(s):
```py
vm.Page.add_type("components", Jumbotron)
```


??? example "Example of new component creation"

    === "app.py"
        ``` py
        from typing import Literal

        from dash import html

        import vizro.models as vm
        from vizro import Vizro


        # 1. Create new custom component
        class Jumbotron(vm.VizroBaseModel):  # (1)!
            """New custom component `Jumbotron`."""

            type: Literal["jumbotron"] = "jumbotron"  # (2)!
            title: str  # (3)!
            subtitle: str
            text: str

            def build(self):  # (4)!
                return html.Div(
                    [
                        html.H2(self.title),
                        html.H3(self.subtitle),
                        html.P(self.text),
                    ]
                )


        # 2. Add new components to expected type - here the selector of the parent components
        vm.Page.add_type("components", Jumbotron)  # (5)!

        page = vm.Page(
            title="Custom Component",
            components=[
                Jumbotron(  # (6)!
                    id="my_jumbotron",
                    title="Jumbotron",
                    subtitle="This is a subtitle to summarize some content.",
                    text="This is the main body of text of the Jumbotron.",
                )
            ],
        )

        dashboard = vm.Dashboard(pages=[page])

        Vizro().build(dashboard).run()

        ```

        1.  Here we subclass the [VizroBaseModel][vizro.models.VizroBaseModel] because we are creating a new component from scratch.
        2.  Here we provide a new type for the new component, so it can be distinguished in the discriminated union.
        3.  Here we provide other fields we think are useful for our components. These fields are the main way the new component can be configured. A lot of different functionality is possible here; see the [Pydantic documentation](https://docs.pydantic.dev/1.10/) for more details.
        4.  As we are creating a new visual component, we have to define a `build` method.
        5.  **Don't forget!** If part of a discriminated union, you must add the new component to the parent model where it will be inserted. In this case the new `Jumbotron` will be inserted into the `components` argument of the `Page` model, and thus must be added as an allowed type.
        6.  The new component can now be inserted into a regular dashboard.
    === "yaml"
        ```yaml
        # Custom components are currently only possible via python configuration
        ```
    === "Result"
        [![CustomComponent2]][CustomComponent2]

    [CustomComponent2]: ../../assets/user_guides/custom_components/customcomponent_2.png


## Using custom components with custom actions

Custom components can be used as `inputs` to, `outputs` of, or as a `trigger` of custom actions. In the examples below we will explore both options.

### Custom components as inputs/outputs of custom actions

Following the instructions above to create a custom component, results in this `OffCanvas` component:

```py
class OffCanvas(vm.VizroBaseModel):
    type: Literal["offcanvas"] = "offcanvas"
    title: str
    content: str

    def build(self):
        return html.Div(
            [
                dbc.Offcanvas(
                    children=html.P(self.content),
                    id=self.id,
                    title=self.title,
                    is_open=False,
                ),
            ]
        )
```

After you have completed the steps above, it is time to write your [custom action](../user-guides/custom-actions.md).

   ```py
    @capture("action")
    def open_offcanvas(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open
   ```

Add the custom action `open_offcanvas` as a `function` argument inside the [`Action`][vizro.models.Action] model.


??? example "Example of the use of custom component with actions"

    === "app.py"
        ``` py
        from typing import List, Literal

        import dash_bootstrap_components as dbc
        import vizro.models as vm
        import vizro.plotly.express as px
        from dash import html
        from vizro import Vizro

        from vizro.models import Action
        from vizro.models.types import capture


        # 1. Create new custom component
        class OffCanvas(vm.VizroBaseModel):
            type: Literal["offcanvas"] = "offcanvas"
            title: str
            content: str

            def build(self):
                return html.Div(
                    [
                        dbc.Offcanvas(
                            children=html.P(self.content),
                            id=self.id,
                            title=self.title,
                            is_open=False,
                        ),
                    ]
                )


        # 2. Add new components to expected type - here the selector of the parent components
        vm.Page.add_type("components", OffCanvas)

        # 3. Create custom action
        @capture("action")
        def open_offcanvas(n_clicks, is_open):
            if n_clicks:
                return not is_open
            return is_open

        page = vm.Page(
            title="Custom Component",
            components=[
                vm.Button(
                    text="Open Offcanvas",
                    id="open_button",
                    actions=[
                        vm.Action(
                            function=open_offcanvas(),
                            inputs=["open_button.n_clicks", "offcanvas.is_open"],
                            outputs=["offcanvas.is_open"],
                        )
                    ],
                ),
                OffCanvas(
                    id="offcanvas",
                    content="OffCanvas content",
                    title="Offcanvas Title",
                ),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])

        Vizro().build(dashboard).run()

        ```
    === "yaml"
        ```yaml
        # Custom components are currently only possible via python configuration
        ```
    === "Result"
        [![CustomComponent3]][CustomComponent3]

    [CustomComponent3]: ../../assets/user_guides/custom_components/customcomponent_3.gif


### Trigger actions with a custom component

As mentioned above, custom components can trigger action. To enable the custom component to trigger the action, we need to add some extra code:

1. **Add the `actions` argument to your custom component**. The type of the `actions` argument is `List[Action]`.
   ```py
    actions: List[Action] = []
   ```
2. **Set the action through `_set_actions`**. In doing so, any change in the `"active_index"` property of the custom component triggers the action.
   ```py
    _set_actions = _action_validator_factory("active_index")
   ```


??? example "Example of triggering action with custom component"

    === "app.py"
        ``` py
        from typing import List, Literal

        import dash_bootstrap_components as dbc
        import vizro.models as vm
        from dash import html
        from vizro import Vizro

        try:
            from pydantic.v1 import Field, PrivateAttr
        except ImportError:
            from pydantic import PrivateAttr

        from vizro.models import Action
        from vizro.models._action._actions_chain import _action_validator_factory
        from vizro.models.types import capture


        # 1. Create new custom component
        class Carussel(vm.VizroBaseModel):
            type: Literal["carussel"] = "carussel"
            items: List
            actions: List[Action] = []

            _set_actions = _action_validator_factory("active_index")  # (1)!

            def build(self):
                return dbc.Carousel(
                    id=self.id,
                    items=self.items,
                )


        # 2. Add new components to expected type - here the selector of the parent components
        vm.Page.add_type("components", Carussel)

        # 3. Create custom action
        @capture("action")
        def carussel(active_index):
            if active_index:
                return "Second slide"

            return "First slide

        page = vm.Page(
            title="Custom Component",
            components=[
                vm.Card(text="First slide", id="carussel-card"),
                Carussel(
                    id="carrusel",
                    items=[
                        {"key": "1", "src": "path_to_your_image"},
                        {"key": "2", "src": "path_to_your_image"},
                    ],
                    actions=[
                        vm.Action(
                            function=carussel(),
                            inputs=["carrusel.active_index"],
                            outputs=["carussel-card.children"]
                        )
                    ]
                ),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])

        Vizro().build(dashboard).run()
        ```

        1.  Here we set the action so a change in the `active_index` property of the custom component triggers the action.
    === "yaml"
        ```yaml
        # Custom components are currently only possible via python configuration
        ```
    === "Result"
        [![CustomComponent4]][CustomComponent4]

    [CustomComponent4]: ../../assets/user_guides/custom_components/customcomponent_4.gif

???+ warning

    Please note that users of this package are responsible for the content of any custom-created component,
    function or integration they write - especially with regard to leaking any sensitive information or exposing to
    any security threat during implementation.

    By default, all Dash components in Vizro that persist client-side data set [`persistence_type="session"` to use `window.SessionStorage`](https://dash.plotly.com/persistence), which is cleared upon closing the browser.
    Be careful when using any custom components that persist data beyond this scope: it is your responsibility to ensure compliance with any legal requirements affecting jurisdictions in which your app operates.
