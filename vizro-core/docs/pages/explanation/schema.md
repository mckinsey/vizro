# Vizro schema and grammar of dashboards

This page explains the [Vizro JSON schema](#what-is-the-vizro-json-schema), which is our attempt to create a ["grammar of dashboards"](#the-grammar-of-dashboards), and the [role of Pydantic](#the-role-of-pydantic).

## What is a JSON schema?

This is a short introduction since there are many good articles to answer the question, ["What is a JSON schema?"](https://blog.postman.com/what-is-json-schema).

A [JSON schema](https://json-schema.org/) defines the rules, structure, and constraints that JSON data (a popular data format, used widely on the web) should follow. Use of a schema leaves minimal room for assumptions and makes it easier to predict the nature and behavior of JSON data.

An example of a JSON schema would be:

```json
{
  "properties": {
    "A": {
      "title": "A",
      "type": "integer"
    },
    "B": {
      "items": {
        "type": "string"
      },
      "title": "B",
      "type": "array"
    }
  },
  "required": [
    "A",
    "B"
  ],
  "title": "Example",
  "type": "object"
}
```

This schema tells us that whenever we receive JSON data, and want to check whether it is valid, the data needs to contain two fields - a field `A`, which must be a single integer, and a field `B`, which must be an array of strings. Both fields must be provided, as they are both required.

In practice this means that data can be identified as valid or invalid:

=== "valid"

    ```json
    {
      "A": 1,
      "B": [
        "a",
        "b"
      ]
    }
    ```

=== "invalid  (`B` is not an array of strings)"

    ```json
    {
      "A": 1,
      "B": [
        "a",
        3
      ]
    }
    ```

=== "also invalid (required field `B` is missing)"

    ```json
    {
      "A": 1,
    }
    ```

## What is the Vizro JSON schema?

Similar to the above example, the Vizro framework also has a JSON schema. It can be [found in our GitHub repository](https://github.com/mckinsey/vizro/tree/main/vizro-core/schemas). It is more complicated than the simple schema above, but it generally follows the same principle.

To get a feeling of what it generally looks like, we have provided a simplified schema below. Reading through it shows us for example that every dashboards needs to have a set of pages, which in turn must have components, but optionally can have controls.

??? example "Simplified Vizro JSON schema"

    ```json
    {
      "$defs": {
        "Page": {
          "properties": {
            "title": {
              "title": "Title",
              "type": "string"
            },
            "components": {
              "items": {
                "enum": [
                  "Card",
                  "Button",
                  "Container",
                  "Graph",
                  "Table",
                  "AgGrid"
                ],
                "type": "string"
              },
              "title": "Components",
              "type": "array"
            },
            "controls": {
              "anyOf": [
                {
                  "items": {
                    "enum": [
                      "Filter",
                      "Parameter"
                    ],
                    "type": "string"
                  },
                  "type": "array"
                },
                {
                  "type": "null"
                }
              ],
              "default": null,
              "title": "Controls"
            }
          },
          "required": [
            "title",
            "components"
          ],
          "title": "Page",
          "type": "object"
        }
      },
      "properties": {
        "title": {
          "title": "Title",
          "type": "string"
        },
        "pages": {
          "items": {
            "$ref": "#/$defs/Page"
          },
          "title": "Pages",
          "type": "array"
        },
        "theme": {
          "enum": [
            "vizro_dark",
            "vizro_light"
          ],
          "title": "Theme",
          "type": "string"
        }
      },
      "required": [
        "title",
        "pages",
        "theme"
      ],
      "title": "Dashboard",
      "type": "object"
    }
    ```

You can thus configure a Vizro dashboard according to a set of constraints that are defined in the schema. The configuration language that you choose is secondary: it can be via Python, but also via JSON or YAML. This is shown in [our showcase of configuration options](../user-guides/dashboard.md#use-dashboard-configuration-options).

=== "This JSON..."

    ```json
    {
      "pages": [
        {
          "components": [
            {
              "figure": {
                "_target_": "scatter",
                "color": "species",
                "data_frame": "iris",
                "x": "sepal_length",
                "y": "petal_width"
              },
              "type": "graph"
            },
            {
              "figure": {
                "_target_": "histogram",
                "color": "species",
                "data_frame": "iris",
                "x": "sepal_width"
              },
              "type": "graph"
            }
          ],
          "controls": [
            {
              "column": "species",
              "type": "filter"
            }
          ],
          "title": "My first dashboard"
        }
      ]
    }
    ```

=== "maps to this Dashboard"

    [![Dashboard]][dashboard]

=== "... but would fail here (Dashboard title missing)"

    ```json
    {
      "pages": [
        {
          "components": [
            {
              "figure": {
                "_target_": "scatter",
                "color": "species",
                "data_frame": "iris",
                "x": "sepal_length",
                "y": "petal_width"
              },
              "type": "graph"
            },
            {
              "figure": {
                "_target_": "histogram",
                "color": "species",
                "data_frame": "iris",
                "x": "sepal_width"
              },
              "type": "graph"
            }
          ],
          "controls": [
            {
              "column": "species",
              "type": "filter"
            }
          ],
        }
      ]
    }
    ```

!!! note

    The Vizro schema is still incomplete. This means that it does not yet define everything that we consider to be core and supported functionality of Vizro. The most prominent example of an omission is the [`CapturedCallable`][vizro.models.types.CapturedCallable], which are the objects you insert into many models such as `vm.Graph`, `vm.Table` or `vm.Action`, often into the `figure` argument.

    This does not mean that it cannot be configured in JSON. In fact, in the configuration above, we have used the following JSON:

    ```json
    {
      "figure": {
        "_target_": "histogram",
        "color": "species",
        "data_frame": "iris",
        "x": "sepal_width"
      },
      "type": "graph"
    }
    ```

    It means that `figure` does not appear in the schema so, as such, it is not clearly defined as part of the Vizro framework, although it should be considered as such. We are working to complete the Vizro schema in the future.

## The role of Pydantic

The Vizro framework is powered by [Pydantic](https://docs.pydantic.dev/latest/), which is the most widely used data validation library for Python. Pydantic acts as the glue that connects Vizro's JSON schema to its actual implementation - a React frontend served by a Flask backend, facilitated by Dash.

One core advantage of Pydantic is that it [can automatically produce a JSON schema](https://docs.pydantic.dev/latest/concepts/json_schema/) from our models (such as `vm.Page` or `vm.Filter`). Pydantic also supports custom validation beyond the functionality of JSON schema.

For our [toy example above](#what-is-a-json-schema), instead of defining the JSON schema directly, we could produce it via Pydantic, using the following Python code:

```python
import json
import pydantic


class Example(pydantic.BaseModel):
    A: int
    B: list[str]


print(json.dumps(Example.model_json_schema(), indent=2))
```

The above example shows that Pydantic makes it very easy to produce JSON schemas by using just Python classes and type annotations. The rest is taken care of by Pydantic.

But Pydantic allows us to go beyond the usual constraints that a JSON schema allows. In our [toy example above](#what-is-a-json-schema), with the help of Pydantic, we could define that all string elements in `B` need to start with either `a` or `b`.

```python
import json
import pydantic


class Example(pydantic.BaseModel):
    A: int
    B: list[str]

    @pydantic.field_validator("B")
    @classmethod
    def validate_b_strings(cls, v: list[str]) -> list[str]:
        for string in v:
            if not string.startswith(("a", "b")):
                raise ValueError("All strings in B must start with either 'a' or 'b'")
        return v
```

This is a fairly random example, but it illustrates the power of custom validation for anyone using the Vizro framework. Most of the time when the user "misconfigures", the error message is clear and concise.

In the toy example, this would have the following consequences:

=== "Providing this JSON config..."

    ```json
    {
      "A": 1,
      "B": [
        "a",
        "b",
        "c"
      ]
    }
    ```

=== "... would get rejected (`c` doesn't start with `a` or `b`)"

    ```shell
    pydantic_core._pydantic_core.ValidationError: 1 validation error for Example
    B
      Value error, All strings in B must start with either 'a' or 'b' [type=value_error, input_value=['a', 'b', 'c'], input_type=list]
        For further information visit https://errors.pydantic.dev/2.10/v/value_error
    ```

With the help of Pydantic, we were able to define a custom validation beyond the limits of JSON schema.

## The grammar of dashboards

How does this all come together? One of the long-term goals of Vizro is to define a so-called **grammar of dashboards**. This means that we complete the Vizro schema and define a unified, implementation independent language to configure dashboards. Other notable "grammars" in the area of visualization are for example [the Plotly Chart schema](https://plotly.com/chart-studio-help/json-chart-schema/) or the [Vega-Lite grammar of interactive graphics](https://vega.github.io/vega-lite/).

At the moment, the Vizro framework serves [Dash](https://github.com/plotly/dash) apps — but this is not a necessary condition. In principle, the mapping of JSON to app could be realized using other technologies.

## The role of `extra`

Some of our models, e.g. the [`Container`][vizro.models.Container], have an argument called `extra`. This argument enables the user to pass extra arguments directly to the underlying component of the model. In the case of the `Container`, this would be the [`dbc.Container`](https://dash-bootstrap-components.opensource.faculty.ai/docs/components/layout/).

This is clearly implementation specific and, as such, the `extra` argument is (on purpose) excluded from the Vizro schema. The argument helps users to get the maximum flexibility quickly without having to go beyond the Vizro framework, but it should not be assumed to be a core part of Vizro. Using this argument may break your code in future releases of Vizro, although this is very unlikely in the foreseeable future.

[dashboard]: ../../assets/user_guides/dashboard/dashboard.png
