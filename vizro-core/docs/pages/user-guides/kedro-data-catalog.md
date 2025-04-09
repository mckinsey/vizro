# How to integrate Vizro with the Kedro Data Catalog

This page describes how to integrate Vizro with [Kedro](https://docs.kedro.org/en/stable/index.html), an open-source Python framework to create reproducible, maintainable, and modular data science code. Vizro provides a convenient way to visualize Pandas datasets registered in a [Kedro Data Catalog](https://docs.kedro.org/en/stable/data/index.html).

Even if you do not have a Kedro project, you can still [use a Kedro Data Catalog](#create-a-kedro-data-catalog) to manage your dashboard's data sources. This separates configuration of your data from your app's code and is particularly useful for dashboards with many data sources or more complex data loading configuration.

## Installation

If you already have Kedro installed then you do not need to install any extra dependencies. If you do not have Kedro installed then you should run:

```bash
pip install vizro[kedro]
```

Vizro is currently compatible with `kedro>=0.19.0` and works with dataset factories for `kedro>=0.19.9`.

## Create a Kedro Data Catalog

You can create a [Kedro Data Catalog](https://docs.kedro.org/en/stable/data/index.html) to be a YAML registry of your dashboard's data sources. To do so, create a new file called `catalog.yaml` file in the same directory as your `app.py`. Below is an example `catalog.yaml` file that illustrates some of the key features of the Kedro Data Catalog.

```yaml
cars:  # (1)!
  type: pandas.CSVDataset  # (2)!
  filepath: cars.csv

motorbikes:
  type: pandas.CSVDataset
  filepath: s3://your_bucket/data/motorbikes.csv   # (3)!
  load_args:   # (4)!
    sep: ','
    na_values: [NA]
  credentials: s3_credentials  # (5)!

trains:
  type: pandas.ExcelDataset
  filepath: trains.xlsx
  load_args:
    sheet_name: [Sheet1, Sheet2, Sheet3]

trucks:
  type: pandas.ParquetDataset
  filepath: trucks.parquet
  load_args:
    columns: [name, gear, disp, wt]
    categories: list
    index: name
```

1. The [minimum details needed](https://docs.kedro.org/en/stable/data/data_catalog.html#the-basics-of-catalog-yml) for a Kedro Data Catalog entry are the data source name (`cars`), the type of data (`type`), and the file's location (`filepath`).
1. Vizro supports all [`kedro_datasets.pandas`](https://docs.kedro.org/en/stable/kedro_datasets.html) datasets. This includes, for example, CSV, Excel and Parquet files.
1. Kedro supports a [variety of data stores](https://docs.kedro.org/en/stable/data/data_catalog.html#dataset-filepath) including local file systems, network file systems and cloud object stores.
1. You can [pass data loading arguments](https://docs.kedro.org/en/stable/data/data_catalog.html#load-save-and-filesystem-arguments) to specify how to load the data source.
1. You can [securely inject credentials](https://docs.kedro.org/en/stable/configuration/credentials.html) into data loading functions using a [`credentials.yaml` file](https://docs.kedro.org/en/stable/data/data_catalog.html#dataset-access-credentials) or [environment variables](https://docs.kedro.org/en/stable/configuration/advanced_configuration.html#how-to-load-credentials-through-environment-variables).

As [shown below](#use-datasets-from-the-kedro-data-catalog), the best way to use the `catalog.yaml` is with the [Kedro configuration loader](https://docs.kedro.org/en/stable/configuration/configuration_basics.html) `OmegaConfigLoader`. For simple cases, this functions much like `yaml.safe_load`. However, the Kedro configuration loader also enables more advanced functionality.

??? "Kedro configuration loader features"

    Here are a few features of the Kedro configuration loader which are not possible with a `yaml.safe_load` alone. For more details, refer to Kedro's [documentation on advanced configuration](https://docs.kedro.org/en/stable/configuration/advanced_configuration.html).

    - [Configuration environments](https://docs.kedro.org/en/stable/configuration/configuration_basics.html#configuration-environments) to organize settings that might be different between your different [development and production environments](run-deploy.md). For example, you might have different s3 buckets for development and production data.
    - [Recursive scanning for configuration files](https://docs.kedro.org/en/stable/configuration/configuration_basics.html#configuration-loading) to merge complex configuration that is split across multiple files and folders.
    - [Templating (variable interpolation)](https://docs.kedro.org/en/stable/configuration/advanced_configuration.html#catalog) and [dynamically computed values (resolvers)](https://docs.kedro.org/en/stable/configuration/advanced_configuration.html#how-to-use-resolvers-in-the-omegaconfigloader).

## Use datasets from the Kedro Data Catalog

Vizro provides functions to help generate and process a [Kedro Data Catalog](https://docs.kedro.org/en/stable/data/index.html) in the module [`vizro.integrations.kedro`](../API-reference/kedro-integration.md). These functions support both the original [`DataCatalog`](https://docs.kedro.org/en/stable/data/data_catalog.html) and the more recently introduced [`KedroDataCatalog`](https://docs.kedro.org/en/stable/data/index.html#kedrodatacatalog-experimental-feature). Given a Kedro `catalog`, the general pattern to add datasets to the Vizro data manager is:

```python
from vizro.integrations import kedro as kedro_integration
from vizro.managers import data_manager


for dataset_name, dataset_loader in kedro_integration.datasets_from_catalog(catalog).items():
    data_manager[dataset_name] = dataset_loader
```

The code above registers all data sources of type [`kedro_datasets.pandas`](https://docs.kedro.org/en/stable/kedro_datasets.html) in the Kedro `catalog` with Vizro's `data_manager` . You can now [reference the data source](data.md#reference-by-name) by name. For example, given the [above `catalog.yaml` file](#create-a-kedro-data-catalog), you could use the data source names `"cars"`, `"motorbikes"`, `"trains"`, and `"trucks"` with `px.scatter("cars", ...)`.

!!! note

    Data sources imported from Kedro in this way are [dynamic data](data.md#dynamic-data). This means that the data can be refreshed while your dashboard is running. For example, if you run a Kedro pipeline, the latest data is shown in the Vizro dashboard without restarting it.

The `catalog` variable may have been created in a number of different ways:

1. Data Catalog configuration file (`catalog.yaml`), [created as described above](#create-a-kedro-data-catalog). This generates a `catalog` variable independently of a Kedro project using [`DataCatalog.from_config`](https://docs.kedro.org/en/stable/kedro.io.DataCatalog.html#kedro.io.DataCatalog.from_config).
1. Kedro project path. Vizro exposes a helper function [`catalog_from_project`](../API-reference/kedro-integration.md#vizro.integrations.kedro.catalog_from_project) to generate a `catalog` given the path to a Kedro project.
1. [Kedro Jupyter session](https://docs.kedro.org/en/stable/notebooks_and_ipython/kedro_and_notebooks.html). This automatically exposes `catalog`.

The full code for these different cases is given below.

!!! example "Import a Kedro Data Catalog into the Vizro data manager"

    === "app.py (Data Catalog configuration file)"

        ```python
        from kedro.config import OmegaConfigLoader
        from kedro.io import DataCatalog  # (1)!

        from vizro.integrations import kedro as kedro_integration
        from vizro.managers import data_manager

        conf_loader = OmegaConfigLoader(conf_source=".")  # (2)!
        catalog = DataCatalog.from_config(conf_loader["catalog"])  # (3)!

        for dataset_name, dataset_loader in kedro_integration.datasets_from_catalog(catalog).items():
            data_manager[dataset_name] = dataset_loader
        ```

        1. Kedro's [experimental `KedroDataCatalog`](https://docs.kedro.org/en/stable/data/index.html#kedrodatacatalog-experimental-feature) would also work.
        1. This [loads and parses configuration in `catalog.yaml`](https://docs.kedro.org/en/stable/configuration/advanced_configuration.html#advanced-configuration-without-a-full-kedro-project). The argument `conf_source="."` specifies that `catalog.yaml` is found in the same directory as `app.py` or a subdirectory beneath this level. In a more complex setup, this could include [configuration environments](https://docs.kedro.org/en/stable/configuration/configuration_basics.html#configuration-environments), for example to organize configuration for development and production data sources.
        1. If you have [credentials](https://docs.kedro.org/en/stable/configuration/credentials.html) then these can be injected with `DataCatalog.from_config(conf_loader["catalog"], conf_loader["credentials"])`.

    === "app.py (Kedro project path)"

        ```python
        from vizro.integrations import kedro as kedro_integration
        from vizro.managers import data_manager

        project_path = "/path/to/kedro/project"
        catalog = kedro_integration.catalog_from_project(project_path)


        for dataset_name, dataset_loader in kedro_integration.datasets_from_catalog(catalog).items():
            data_manager[dataset_name] = dataset_loader
        ```

    === "app.ipynb (Kedro Jupyter session)"

        ```python
        from vizro.managers import data_manager


        for dataset_name, dataset_loader in kedro_integration.datasets_from_catalog(catalog).items():
            data_manager[dataset_name] = dataset_loader
        ```

### Use dataset factories

To add datasets that are defined using a [Kedro dataset factory](https://docs.kedro.org/en/stable/data/kedro_dataset_factories.html), `datasets_from_catalog` needs to resolve dataset patterns against explicit datasets. Given a Kedro `pipelines` dictionary, you should specify a `pipeline` argument as follows:

```python
kedro_integration.datasets_from_catalog(catalog, pipeline=pipelines["__default__"])  # (1)!
```

1. You can specify the name of your pipeline, for example `pipelines["my_pipeline"]`, or even combine multiple pipelines with `pipelines["a"] + pipelines["b"]`. The Kedro `__default__` pipeline is what runs by default with the `kedro run` command.

The `pipelines` variable may have been created the following ways:

1. Kedro project path. Vizro exposes a helper function [`pipelines_from_project`](../API-reference/kedro-integration.md#vizro.integrations.kedro.pipelines_from_project) to generate a `pipelines` given the path to a Kedro project.
1. [Kedro Jupyter session](https://docs.kedro.org/en/stable/notebooks_and_ipython/kedro_and_notebooks.html). This automatically exposes `pipelines`.

The full code for these different cases is given below.

!!! example "Import a Kedro Data Catalog with dataset factories into the Vizro data manager"

    === "app.py (Kedro project path)"

        ```python
        from vizro.integrations import kedro as kedro_integration
        from vizro.managers import data_manager


        project_path = "/path/to/kedro/project"
        catalog = kedro_integration.catalog_from_project(project_path)
        pipelines = kedro_integration.pipelines_from_project(project_path)

        for dataset_name, dataset_loader in kedro_integration.datasets_from_catalog(
            catalog, pipeline=pipelines["__default__"]
        ).items():
            data_manager[dataset_name] = dataset_loader
        ```

    === "app.ipynb (Kedro Jupyter session)"

        ```python
        from vizro.managers import data_manager


        for dataset_name, dataset_loader in kedro_integration.datasets_from_catalog(
            catalog, pipeline=pipelines["__default__"]
        ).items():
            data_manager[dataset_name] = dataset_loader
        ```
