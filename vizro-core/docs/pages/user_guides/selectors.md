# How to use selectors

This guide highlights different selectors that can be used in a dashboard. Selectors do not serve a purpose on their own, but they allow to change how the input is given to other models, e.g. the [`Filter`][vizro.models.Filter] or the [`Parameter`][vizro.models.Parameter] model.

The [`Filter`][vizro.models.Filter] or the [`Parameter`][vizro.models.Parameter] model accept the `selector` argument, where a selector model can be entered to choose how the user should input their choices for the respective models.

## Categorical Selectors

Within the categorical selectors, a clear distinction exists between multi-option and single-option selectors.
For instance, the [`Checklist`][vizro.models.Checklist] functions as a multi-option selector by default while
the [`RadioItem`][vizro.models.RadioItems] serves as a single-option selector by default. However, the
[`Dropdown`][vizro.models.Dropdown] can function as both a multi-option or single-option selector.

For more details, kindly refer to the documentation of the underlying dash components:

- [dcc.Dropdown](https://dash.plotly.com/dash-core-components/dropdown)
- [dcc.Checklist](https://dash.plotly.com/dash-core-components/checklist)
- [dcc.RadioItems](https://dash.plotly.com/dash-core-components/radioitems)

???+ note

    When configuring the `options` of the categorical selectors, you can either provide:

    - a list of values e.g. `options = ['Value A', 'Value B', 'Value C']`
    - or a dictionary of label-value mappings e.g. `options=[{'label': 'True', 'value': True}, {'label': 'False', 'value': False}]`

    The later is required if you want to provide different display labels to your option values or in case you want to
    provide boolean values as options. In this case, you need to provide a string label for your boolean values as
    boolean values cannot be displayed properly as labels in the underlying dash components.

## Numerical Selectors

For more details, kindly refer to the documentation of the underlying dash components:

- [dcc.Slider](https://dash.plotly.com/dash-core-components/slider])
- [dcc.RangeSlider](https://dash.plotly.com/dash-core-components/rangeslider])

???+ note

    When configuring the [`Slider`][vizro.models.Slider] and the [`RangeSlider`][vizro.models.RangeSlider] with float values, and using `step` with an integer value, you may notice
    unexpected behavior, such as the drag value being outside its indicated marks.
    To our knowledge, this is a current bug in the underlying [`dcc.Slider`](https://dash.plotly.com/dash-core-components/slider) and
    [`dcc.RangeSlider`](https://dash.plotly.com/dash-core-components/rangeslider) component, which you can circumvent by adapting the `step` size accordingly.

To enhance existing selectors, please see our How-to-guide on creating [custom components](custom_components.md)
