# Vizro schema and grammar of dashboards

This page explains the [Vizro JSON schema](#what-is-the-vizro-json-schema), which is our attempt to create a ["grammar of dashboards"](#the-grammar-of-dashboards), and the [role of Pydantic](#the-role-of-pydantic).

## What is a JSON schema?

This is a short introduction since there are many good articles to answer the question, ["What is a JSON schema?"](https://blog.postman.com/what-is-json-schema).

A JSON schema defines the rules, structure, and constraints that JSON data (a popular data format, used widely on the web) should follow. Use of a schema leaves minimal room for assumptions and makes it easier to predict the nature and behavior of JSON data.

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

=== "invalid"
    ```json
    {
      "A": 1,
      "B": [
        "a",
        3
      ]
    }
    ```

=== "also invalid"
    ```json
    {
    "A": 1,
    }
    ```

## What is the Vizro JSON schema?

Similar to the above example, the Vizro framework also has a JSON schema. It can be [found in our GitHub repository](https://github.com/mckinsey/vizro/tree/main/vizro-core/schemas). It is more complicated than the simple schema above, but it generally follows the same principle.

You can configure a Vizro dashboard according to a set of constraints that are defined in the schema. The configuration language that you choose is secondary: it can be via Python, but also via JSON or YAML. This is shown in [our showcase of configuration options](../user-guides/dashboard.md#use-dashboard-configuration-options).

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

The Vizro framework is powered by [Pydantic](https://docs.pydantic.dev/latest/), which is the most widely used data validation library for Python. Pydantic acts as the glue that connects Vizro's JSON schema to its actual implementation - a React front end served by a Flask backend, facilitated by Dash.

One core advantage of Pydantic is that it emits a [JSON schema](https://blog.postman.com/what-is-json-schema) so that our models, such as `vm.Page` or `vm.Filter`, can easily be translated into a well-defined JSON schema. Beyond this capability, it also has support for custom validation beyond the functionality of the JSON schema.

In our toy example from above we could define that, in the array of strings, consecutive elements have to have more letters than their predecessor. This is a fairly random example, but it illustrates the power of custom validation for anyone using the Vizro framework. Most of the time when the user "misconfigures", the error message is clear and concise.

## The grammar of dashboards

How does this all come together? One of the long-term goals of Vizro is to define a so-called **grammar of dashboards**. This means that we complete the Vizro schema and define a unified, implementation independent language to configure dashboards.

At the moment, the Vizro framework serves [Dash](https://github.com/plotly/dash) apps - but this is not a necessary condition. In principle, the mapping of JSON to application/dashboard could be realized in any technology.

## The role of `extra`

Some of our models, e.g. the [`Container`][vizro.models.Container], have an argument called `extra`. This argument enables the user to pass extra arguments directly to the underlying component of the model. In the case of the `Container`, this would be the [`dbc.Container`](https://dash-bootstrap-components.opensource.faculty.ai/docs/components/layout/).

This is clearly implementation specific and, as such, the `extra` argument is (on purpose) excluded from the Vizro schema. The argument helps users to get the maximum flexibility quickly without having to go beyond the Vizro framework, but it should not be assumed to be a core part of Vizro. Using this argument may break your code in future releases of Vizro, although this is very unlikely in the foreseeable future.

[dashboard]: ../../assets/user_guides/dashboard/dashboard.png
