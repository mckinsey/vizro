# How to integrate Vizro with the Kedro Data Catalog

This page describes how to integrate Vizro with [Kedro](https://docs.kedro.org/en/stable/index.html), an open-source Python framework to create reproducible, maintainable, and modular data science code. Vizro provides a convenient way to visualize Pandas datasets registered in a [Kedro Data Catalog](https://docs.kedro.org/en/stable/data/index.html).

Even if you do not have a Kedro project, you can still [use a Kedro Data Catalog](#create-a-kedro-data-catalog) to manage your dashboard's data sources.

## Installation

If you already have Kedro installed then you do not need to install any extra dependencies. If you do not have Kedro installed then you should run:

```bash
pip install vizro[kedro]
```

Vizro is currently compatible with `kedro>=0.19.0` and works with dataset factories for `kedro>=0.19.9`.

## Create a Kedro Data Catalog

You can create a [Kedro Data Catalog](https://docs.kedro.org/en/stable/data/index.html) to be a YAML registry of your dashboard's data sources. If you have a Kedro project then you will already have this file; if you would like to use the Kedro Data Catalog outside a Kedro project then you need to create it. In this case, you should save your `catalog.yaml` file to the same directory as your `app.py`.

The Kedro Data Catalog separates configuration of your data sources from your app's code. Here is an example `catalog.yaml` file that illustrates some of the features of the Kedro Data Catalog.

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

For more details, refer to Kedro's [introduction to the Data Catalog](https://docs.kedro.org/en/stable/data/data_catalog.html) and their [collection of YAML examples](https://docs.kedro.org/en/stable/data/data_catalog_yaml_examples.html).

## Use datasets from the Kedro Data Catalog

Vizro provides functions to help generate and process a [Kedro Data Catalog](https://docs.kedro.org/en/stable/data/index.html) in the module `vizro.integrations.kedro`. These functions support both the original [`DataCatalog`](https://docs.kedro.org/en/stable/data/data_catalog.html) and the more recently introduced [`KedroDataCatalog`](https://docs.kedro.org/en/stable/data/index.html#kedrodatacatalog-experimental-feature). Given a Kedro `catalog`, the general pattern to add datasets to the Vizro data manager is:

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
1. Kedro project path. Vizro exposes a helper function `catalog_from_project` to generate a `catalog` given the path to a Kedro project.
1. [Kedro Jupyter session](https://docs.kedro.org/en/stable/notebooks_and_ipython/kedro_and_notebooks.html). This automatically exposes `catalog`.

The full code for these different cases is given below.

!!! example "Import a Kedro Data Catalog into the Vizro data manager"
    === "app.py (Data Catalog configuration file)"
        ```python
        from kedro.io import DataCatalog  # (1)!
        import yaml

        from vizro.integrations import kedro as kedro_integration
        from vizro.managers import data_manager


        catalog = DataCatalog.from_config(yaml.safe_load(Path("catalog.yaml").read_text(encoding="utf-8")))  # (2)!

        for dataset_name, dataset_loader in kedro_integration.datasets_from_catalog(catalog).items():
            data_manager[dataset_name] = dataset_loader
        ```

        1. Kedro's [experimental `KedroDataCatalog`](https://docs.kedro.org/en/stable/data/index.html#kedrodatacatalog-experimental-feature) would also work.
        1. The contents of `catalog.yaml` is [described above](#create-a-kedro-data-catalog).

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

1. Kedro project path. Vizro exposes a helper function `pipelines_from_project` to generate a `pipelines` given the path to a Kedro project.
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
