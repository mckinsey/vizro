# How to connect your dashboard to data

Vizro supports two different types of data:

* [Static data](static-data.md): pandas DataFrame. This is the simplest method and best to use if you do not need the more advanced functionality of dynamic data.
* [Dynamic data](dynamic-data.md): function that returns a pandas DataFrame. This is a bit more complex to understand but has more advanced functionality such as the ability to refresh data while the dashboard is running.

The following flowchart shows what you need to consider when choosing how to set up your data.
``` mermaid
graph TD
  refresh["`Do you need your data to refresh while the dashboard is running?`"]
  specification["`Do you need to specify your dashboard through a configuration language like YAML?`"]
  dynamic([Use dynamic data referenced by name])
  static-direct([Use static data supplied directly])
  static-name([Use static data referenced by name])

  refresh -- No --> specification
  refresh -- Yes --> dynamic
  specification -- No --> static-direct
  specification -- Yes --> static-name
  
  click static-direct href "../static-data#supply-directly"
  click static-name href "../static-data#reference-by-name"
  click dynamic href "../dynamic-data"
```

??? note "Static vs. dynamic data comparison"

    This table gives a full comparison between static and dynamic data. Do not worry if you do not yet understand everything in it; it will become clearer after reading more about [static data](static-data.md) and [dynamic data](dynamic-data.md)!

    |                                                               | Static           | Dynamic                                  |
    |---------------------------------------------------------------|------------------|------------------------------------------|
    | Required Python type                                          | pandas DataFrame | Function that returns a pandas DataFrame |
    | Can be supplied directly in `data_frame` argument of `figure` | Yes              | No                                       |
    | Can be referenced by name after adding to Data Manager        | Yes              | Yes                                      |
    | Can be refreshed while dashboard is running                   | No               | Yes                                      |
    | Production-ready                                              | Yes              | Yes                                      |

If you have a [Kedro](https://kedro.org/) project or would like to use the [Kedro Data Catalog](https://docs.kedro.org/en/stable/data/index.html) to manage your data independently of a Kedro project then you should use Vizro's [integration with the Kedro Data Catalog](kedro-data-catalog.md). This provides helper functions to add [`kedro_datasets.pandas`](https://docs.kedro.org/en/stable/kedro_datasets.html) datasets as dynamic data in the Vizro Data Manager.
