# How to create custom components

If you can't find a component that you would like to have in the code basis, you can easily create your own custom component.
This guide shows you how to create custom components or enhance existing ones.

In general, you can create a custom component based on any dash-compatible component (e.g. [dash-core-components](https://dash.plotly.com/dash-core-components),
[dash-bootstrap-components](https://dash-bootstrap-components.opensource.faculty.ai/), [dash-html-components](https://github.com/plotly/dash/tree/dev/components/dash-html-components), etc.).


Vizro's public API is deliberately kept small in order to facilitate quick and easy configuration of a dashboard. However,
at the same time, Vizro is easily extensible, so that you can tweak any component to your liking or even create entirely new ones.

!!!note

    There are always **three general steps** to consider in order to create a custom component:

    1. **Sub-class to create** your component
    2. **Enhance or build** the component (e.g. add/change model fields, overwrite pre-build/build method, etc.) to your desire
    3. **Check** if your component will be part of a discriminated union[^1]. If yes, then
        - you must ensure your component has a `type` field
        - you must register the new type with its parent model's relevant field (where the new component is entered into) with [`add_type`][vizro.models.VizroBaseModel.add_type]

    We will refer back to these three steps in the two examples below.

[^1]: You can easily check if your new component will be part of a discriminated union by consulting our [API reference on models](../API_reference/models.md). Check whether the relevant model field (e.g. `selectors` in [`Filter`][vizro.models.Filter] or [`Parameter`][vizro.models.Parameter]) is described as a discriminated union (in this case the [`SelectorType`][vizro.models.types.SelectorType] is, but for example [`OptionsType`][vizro.models.types.OptionsType] is not).


## Extend an existing component
??? info "When to choose this strategy"

    You may want to use this strategy to:

    - extend an existing component (e.g. adding a button to [`Card`][vizro.models.Card])
    - change configurations we have set by default (e.g. setting `allowCross=False` in [`RangeSlider`][vizro.models.RangeSlider])
    - change any fields of any models (e.g. changing the title field from `Optional` to have a default)


You can extend an existing component by sub-classing the component you want to alter.
The below example is a bit lengthy, but the annotations should guide you through the most important lines of that code. Remember that when sub-classing a component
you have access to all fields of all parent models, but you can choose to overwrite any field or method, or define new ones.

The aim for this example is to enhance the [`RangeSlider`][vizro.models.RangeSlider] model so that
one slider handle cannot cross the other, and to have a permanent tooltip showing the current value. You will note that it is often easier to copy parts of the source-code when needing to change complex methods
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
        ``` py linenums="1" hl_lines="66 67"
        from dash import Input, Output, State, callback, callback_context, dcc, html
        from typing_extensions import Literal

        import vizro.models as vm
        import vizro.plotly.express as px
        from vizro import Vizro

        iris = px.data.iris()


        # 1. Create custom component - here based on the existing RangeSlider
        class TooltipNonCrossRangeSlider(vm.RangeSlider):
            """Custom numeric multi-selector `TooltipNonCrossRangeSlider`."""

            type: Literal["other_range_slider"] = "other_range_slider" # (1)!

            def build(self):  # (2)!
                value = self.value or [self.min, self.max]  # type: ignore[list-item]

                output = [
                    Output(f"{self.id}_start_value", "value"),
                    Output(f"{self.id}_end_value", "value"),
                    Output(self.id, "value"),
                    Output(f"temp-store-range_slider-{self.id}", "data"),
                ]
                input = [
                    Input(f"{self.id}_start_value", "value"),
                    Input(f"{self.id}_end_value", "value"),
                    Input(self.id, "value"),
                    State(f"temp-store-range_slider-{self.id}", "data"),
                ]

                @callback(output=output, inputs=input)
                def update_slider_values(start, end, slider, input_store):
                    trigger_id = callback_context.triggered_id
                    if trigger_id == f"{self.id}_start_value" or trigger_id == f"{self.id}_end_value":
                        start_text_value, end_text_value = start, end
                    elif trigger_id == self.id:
                        start_text_value, end_text_value = slider
                    else:
                        start_text_value, end_text_value = input_store if input_store is not None else value

                    start_value = min(start_text_value, end_text_value)
                    end_value = max(start_text_value, end_text_value)
                    start_value = max(self.min, start_value)
                    end_value = min(self.max, end_value)
                    slider_value = [start_value, end_value]
                    return start_value, end_value, slider_value, (start_value, end_value)

                return html.Div(
                    [
                        html.P(self.title, id="range_slider_title") if self.title else html.Div(hidden=True),
                        html.Div(
                            [
                                dcc.RangeSlider(
                                    id=self.id,
                                    min=self.min,
                                    max=self.max,
                                    step=self.step,
                                    marks=self.marks,
                                    className="range_slider_control" if self.step else "range_slider_control_no_space",
                                    value=value,
                                    persistence=True,
                                    allowCross=False, # (3)!
                                    tooltip={"placement": "bottom", "always_visible": True}, # (4)!
                                ),
                                html.Div(
                                    [
                                        dcc.Input(
                                            id=f"{self.id}_start_value",
                                            type="number",
                                            placeholder="start",
                                            min=self.min,
                                            max=self.max,
                                            className="slider_input_field_left"
                                            if self.step
                                            else "slider_input_field_no_space_left",
                                            value=value[0],
                                            size="24px",
                                            persistence=True,
                                        ),
                                        dcc.Input(
                                            id=f"{self.id}_end_value",
                                            type="number",
                                            placeholder="end",
                                            min=self.min,
                                            max=self.max,
                                            className="slider_input_field_right"
                                            if self.step
                                            else "slider_input_field_no_space_right",
                                            value=value[1],
                                            persistence=True,
                                        ),
                                        dcc.Store(id=f"temp-store-range_slider-{self.id}", storage_type="local"),
                                    ],
                                    className="slider_input_container",
                                ),
                            ],
                            className="range_slider_inner_container",
                        ),
                    ],
                    className="selector_container",
                )


        # 2. Add new components to expected type - here the selector of the parent components
        vm.Filter.add_type("selector", TooltipNonCrossRangeSlider) # (5)!
        vm.Parameter.add_type("selector", TooltipNonCrossRangeSlider) # (6)!

        page = vm.Page(
            title="Custom Component",
            path="custom-component",
            components=[
                vm.Graph(
                    id="for_custom_chart",
                    figure=px.scatter(iris, title="Foo", x="sepal_length", y="petal_width", color="sepal_width"),
                ),
            ],
            controls=[
                vm.Filter(
                    column="sepal_length",
                    targets=["for_custom_chart"],
                    selector=TooltipNonCrossRangeSlider(), # (7)!
                ),
                vm.Parameter(
                    targets=["for_custom_chart.range_x"],
                    selector=TooltipNonCrossRangeSlider(title="Select x-axis range", min=0, max=10),
                ),
            ],
        )

        dashboard = vm.Dashboard(pages=[page])

        Vizro().build(dashboard).run()
        ```

        1.  Here we provide a new type for the new component, so it can be distinguished in the discriminated union.
        2.  Here we chose to mostly copy the source code of the build method and alter it directly. Alternatively we could overload the `build` method and alter the output of `super().build()`, but then we recommend pinning the version of `Vizro` in case of future breaking changes.
        3.  This is the change that makes the `RangeSlider` not cross itself when moving the handle.
        4.  This is the change that displays the tooltip below the handle.
        5.  **Don't forget!** If part of a discriminated union, you must add the new component to the parent model where it will be inserted. In this case the new `TooltipNonCrossRangeSlider` will be inserted into the `selector` argument of the `Filter` model, and thus must be added as an allowed type.
        6.  **Don't forget!** If part of a discriminated union, you must add the new component to the parent model where it will be inserted. In this case the new `TooltipNonCrossRangeSlider` will be inserted into the `selector` argument of the `Parameter` model, and thus must be added as an allowed type.
        7.  The new component can now be inserted into a regular dashboard.

    === "yaml"
        ```yaml
        # TBD
        ```
    === "Result"
        [![CustomComponent1]][CustomComponent1]

    [CustomComponent1]: ../../assets/user_guides/custom_components/customcomponent_1.png


## Entirely new component

??? info "When to choose this strategy"

    You may want to use this strategy to:

    - create a new component that does not exist in our library yet
    - make extensive changes to an existing component

You can create an entirely new component by sub-classing our [VizroBaseModel][vizro.models.VizroBaseModel]. Note that
using `VizroBaseModel` is mandatory if you want the new component to work in the Vizro framework.

The aim of the example is to create a [`Jumbotron`](https://dash-bootstrap-components.opensource.faculty.ai/docs/components/jumbotron/), a component that currently does not exist in Vizro's existing component range. It is a lightweight container to call attention to featured content or information.

???note "Note on `build` and `pre_build` methods"
    Note that when creating new components, you will need to define a `build` method like in the below example if it is a visual component that is rendered on the page. Examples of components with a `build` method are:

    - `selector` type: [`Checklist`][vizro.models.Checklist], [`Dropdown`][vizro.models.Dropdown], [`RadioItems`][vizro.models.RadioItems], etc.
    - `component` type: [`Graph`][vizro.models.Graph], [`Card`][vizro.models.Card], etc.

    For components that only create other components, you do not need to define a `build` method, e.g. for [`Filter`][vizro.models.Filter] and [`Parameter`][vizro.models.Parameter].

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
    dbc.Container(
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


??? example "Example of entirely new component"

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
            path="custom-component",
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
        # TBD
        ```
    === "Result"
        [![CustomComponent2]][CustomComponent2]

    [CustomComponent2]: ../../assets/user_guides/custom_components/customcomponent_2.png



???+ warning

    Please note that users of this package are responsible for the content of any custom-created component,
    function or integration they write - especially with regard to leaking any sensitive information or exposing to
    any security threat during implementation.
