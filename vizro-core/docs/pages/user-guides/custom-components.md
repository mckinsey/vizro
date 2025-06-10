# How to create custom components

Vizro's public API is kept small to enable quick and easy configuration of a dashboard. However,
at the same time, Vizro is extensible, so that you can tweak any component to your liking or even create entirely new ones.

If you can't find a component that you would like to have in the code basis, or if you would like to alter/enhance an existing component, then you are in the right place.
This guide shows you how to create custom components that are completely new, or enhancements of existing ones.

!!! note "Can you use `extra` instead of creating a custom component?"
    If you want to alter/enhance an existing component, you may not even need to create a custom component. Many of our models have an `extra` argument, that let's you pass arguments to the underlying Dash component directly. You can check the [API reference](../API-reference/models.md) of the model in question. An example of this would be to make the [`RadioItem`][vizro.models.RadioItems] [inline instead of stacked](./selectors.md#the-extra-argument).

In general, you can create a custom component based on any dash-compatible component (for example, [dash-core-components](https://dash.plotly.com/dash-core-components),
[dash-bootstrap-components](https://dash-bootstrap-components.opensource.faculty.ai/), [dash-html-components](https://github.com/plotly/dash/tree/dev/components/dash-html-components)).


All our components are based on `Dash`, and they are shipped with a set of sensible defaults that can be modified. If you would like to overwrite one of those defaults,
or if you would like to use extra `args` or `kwargs` of those components, then this is the correct way to include those. You can use any existing attribute of any underlying [Dash component](https://dash.plotly.com/#open-source-component-libraries) with this method.

!!!note

    There are always **four general steps** to consider to create a custom component:

    0. **Check** if you can achieve your goal with a potential `extra` argument
    1. **Sub-class to create** your component
    2. **Enhance or build** the component (for example, to add/change model fields, overwrite pre-build/build method) to your desire
    3. **Check** if your component will be part of a discriminated union[^1]. If yes, then
        - you must ensure your component has a `type` field
        - you must register the new type with its parent model's relevant field (where the new component is entered into) with [`add_type`][vizro.models.VizroBaseModel.add_type]

    We will refer back to these three steps in the two examples below.

[^1]: You can check if your new component will be part of a discriminated union by consulting our [API reference on models](../API-reference/models.md). Check whether the relevant model field (for example, `selectors` in [`Filter`][vizro.models.Filter] or [`Parameter`][vizro.models.Parameter]) is described as a discriminated union (in this case the [`SelectorType`][vizro.models.types.SelectorType] is, but for example [`OptionsType`][vizro.models.types.OptionsType] is not).


## Extend an existing component


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
        ```{.python pycafe-link linenums="1" hl_lines="17 18"}
        from typing_extensions import Literal

        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro

        iris = px.data.iris()


        class TooltipNonCrossRangeSlider(vm.RangeSlider):
            """Custom numeric multi-selector `TooltipNonCrossRangeSlider`."""

            type: Literal["other_range_slider"] = "other_range_slider"  # (1)!

            def build(self):  # (2)!
                range_slider_build_obj = super().build()  # (3)!
                range_slider_build_obj[self.id].allowCross = False  # (4)!
                range_slider_build_obj[self.id].tooltip = {"always_visible": True, "placement": "bottom"}  # (5)!
                return range_slider_build_obj


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
        # Custom components are currently only possible via Python configuration
        ```
    === "Result"
        [![CustomComponent1]][CustomComponent1]

    [CustomComponent1]: ../../assets/user_guides/custom_components/customcomponent_1.png


## Create a new component

You may want to use this strategy to:

- create a new component that does not exist in our library yet
- make extensive changes to an existing component

You can create an entirely new component by sub-classing our [VizroBaseModel][vizro.models.VizroBaseModel]. Note that
using `VizroBaseModel` is mandatory if you want the new component to work in the Vizro framework.

The aim of the example is to create a [`Jumbotron`](https://dash-bootstrap-components.opensource.faculty.ai/docs/components/jumbotron/), a component that currently does not exist in Vizro's existing component range. It is a lightweight container to call attention to featured content or information.

### The `build` and `pre_build` methods

When creating new components, you will need to define a `build` method like in the below example if it is a visual component that is rendered on the page. Examples of components with a `build` method are:

- `selector` type: [`Checklist`][vizro.models.Checklist], [`Dropdown`][vizro.models.Dropdown], [`RadioItems`][vizro.models.RadioItems].
- `component` type: [`Graph`][vizro.models.Graph], [`Card`][vizro.models.Card].

For components that only create other components, you do not need to define a `build` method, for example, for [`Filter`][vizro.models.Filter] and [`Parameter`][vizro.models.Parameter].

If you would like to have access to other components, you may want to define a `pre_build` method. This method is automatically run for all models and makes them internally consistent. Notable existing models with `pre_build` methods are [`Filter`][vizro.models.Filter] and [`Parameter`][vizro.models.Parameter].

### General steps

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
        ```{.python pycafe-link}
        from typing import Literal

        from dash import html

        import vizro.models as vm
        from vizro import Vizro


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


        vm.Page.add_type("components", Jumbotron)  # (5)!

        page = vm.Page(
            title="Custom Component",
            components=[
                Jumbotron(  # (6)!
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
        # Custom components are currently only possible via Python configuration
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
        ```{.python pycafe-link}
        from typing import Literal

        import dash_bootstrap_components as dbc
        import vizro.models as vm
        import vizro.plotly.express as px
        from dash import html
        from vizro import Vizro

        from vizro.models.types import capture


        class OffCanvas(vm.VizroBaseModel):  # (1)!
            type: Literal["offcanvas"] = "offcanvas"  # (2)!
            title: str
            content: str

            def build(self):  # (3)!
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


        vm.Page.add_type("components", OffCanvas)  # (4)!

        @capture("action")  # (5)!
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
                        vm.Action(  # (6)!
                            function=open_offcanvas(),
                            inputs=["open_button.n_clicks", "offcanvas.is_open"],
                            outputs=["offcanvas.is_open"],
                        )
                    ],
                ),
                OffCanvas(  # (7)!
                    id="offcanvas",
                    content="OffCanvas content",
                    title="Offcanvas Title",
                ),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()

        ```

        1. Here we sub-class `VizroBaseModel` to create a new `OffCanvas` component.
        1. We define a new type for the component, so it can be distinguished in the discriminated union.
        1. We define the `build` method, which will be called to render the component on the page. This uses `dbc.Offcanvas` from `dash-bootstrap-components`.
        1. **Remember!** If part of a discriminated union, you must add the new component to the parent model where it will be inserted. In this case the new `OffCanvas` component will be inserted into the `components` argument of the `Page` model, and thus must be added as an allowed type.
        1. We define a custom action `open_offcanvas` using the `@capture("action")` decorator. This action will toggle the `is_open` state of the `OffCanvas` component.
        1. We add the `open_offcanvas` action to a `Button`. The action takes `n_clicks` from the button and the current `is_open` state of the `OffCanvas` as inputs, and outputs the new `is_open` state to the `OffCanvas`.
        1. We add the `OffCanvas` component to the page.
    === "yaml"
        ```yaml
        # Custom components are currently only possible via Python configuration
        ```
    === "Result"
        [![CustomComponent3]][CustomComponent3]

    [CustomComponent3]: ../../assets/user_guides/custom_components/customcomponent_3.gif


### Trigger actions with a custom component

As mentioned above, custom components can trigger actions. To enable the custom component to trigger the action, add the `actions` field and specify which property triggers the actions:

1. **Add the `actions` argument to your custom component**. The type of the `actions` argument is `list[ActionType]`.
2. **Set the action through `_action_validator_factory`**. In doing so, any change in the `"active_index"` property of the custom component triggers the action.

    ```py
    actions: Annotated[
        list[ActionType],
        AfterValidator(_action_validator_factory("active_index")),
        PlainSerializer(lambda x: x[0].actions),
        Field(default=[]),
        ]
    ```


??? example "Example of triggering action with custom component"

    === "app.py"
        ```py
        from typing import Annotated, Literal

        import dash_bootstrap_components as dbc
        import vizro.models as vm
        from pydantic import AfterValidator, Field, PlainSerializer
        from vizro import Vizro
        from vizro.models.types import ActionType
        from vizro.models._action._actions_chain import _action_validator_factory
        from vizro.models.types import capture


        class Carousel(vm.VizroBaseModel):  # (1)!
            type: Literal["carousel"] = "carousel"
            items: list
            actions: Annotated[
                list[ActionType],
                AfterValidator(_action_validator_factory("active_index")),  # (2)!
                PlainSerializer(lambda x: x[0].actions),  # (3)!
                Field(default=[]),
            ]

            def build(self):
                return dbc.Carousel(
                    id=self.id,
                    items=self.items,
                )

        vm.Page.add_type("components", Carousel)  # (4)!

        @capture("action")  # (5)!
        def slide_next_card(active_index):
            if active_index:
                return "Second slide"

            return "First slide"


        page = vm.Page(
            title="Custom Component",
            components=[
                vm.Card(text="First slide", id="carousel-card"),
                Carousel(  # (6)!
                    id="carousel",
                    items=[
                        {"key": "1", "src": "assets/slide_1.jpg"},
                        {"key": "2", "src": "assets/slide_2.jpg"},
                    ],
                    actions=[
                        vm.Action(  # (7)!
                            function=slide_next_card(),
                            inputs=["carousel.active_index"],
                            outputs=["carousel-card.children"],
                        )
                    ],
                ),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```

        1. Here we subclass `VizroBaseModel` to create a new `Carousel` component.
        1. We set the action so a change in the `active_index` property of the custom component triggers the action. `_action_validator_factory("active_index")` ensures that an `Action` model is correctly created and validated.
        1. We tell the serializer to only serialize the `actions` field. This is important for when the dashboard configuration is exported (e.g., to YAML or JSON).
        1. **Remember!** If part of a discriminated union, you must add the new component to the parent model where it will be inserted. In this case the new `Carousel` will be inserted into the `components` argument of the `Page` model, and thus must be added as an allowed type.
        1. We define a custom action `slide_next_card` using the `@capture("action")` decorator. This action will change the text of a `Card` component based on the active slide in the `Carousel`.
        1. We add the `Carousel` component to the page, providing items for the carousel.
        1. We link the `slide_next_card` action to the `Carousel`. The action is triggered by changes in `carousel.active_index` and updates the `children` property of `carousel-card`.

        <img src=https://py.cafe/logo.png alt="PyCafe logo" width="30"><b><a target="_blank" href="https://py.cafe/vizro-official/vizro-custom-carousel-component">Run and edit this code in PyCafe</a></b>

    === "yaml"
        ```yaml
        # Custom components are currently only possible via Python configuration
        ```
    === "Result"
        [![CustomComponent4]][CustomComponent4]

    [CustomComponent4]: ../../assets/user_guides/custom_components/customcomponent_4.gif

### Security warning

Note that users of this package are responsible for the content of any custom-created component, function or integration they write. You should be cautious about leaking any sensitive information and potential security threats.

By default, all Dash components in Vizro that persist client-side data set [`persistence_type="session"` to use `window.SessionStorage`](https://dash.plotly.com/persistence), which is cleared upon closing the browser.

Be careful when using any custom components that persist data beyond this scope: it is your responsibility to ensure compliance with any legal requirements affecting jurisdictions in which your app operates.
