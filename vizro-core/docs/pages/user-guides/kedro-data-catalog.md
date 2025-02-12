# How to integrate Vizro with Kedro Data Catalog

This page describes how to integrate Vizro with [Kedro](https://docs.kedro.org/en/stable/index.html), an open-source Python framework to create reproducible, maintainable, and modular data science code. For Pandas datasets registered in a Kedro data catalog, Vizro provides a convenient way to visualize them.

## Installation

If you already have Kedro installed then you do not need to install any extra dependencies. If you do not have Kedro installed then you should run:

```bash
pip install vizro[kedro]
```

## Use datasets from the Kedro Data Catalog

`vizro.integrations.kedro` provides functions to help generate and process a [Kedro Data Catalog](https://docs.kedro.org/en/stable/data/index.html). It supports both the original [`DataCatalog`](https://docs.kedro.org/en/stable/data/data_catalog.html) and the more recently introduced [`KedroDataCatalog`](https://docs.kedro.org/en/stable/data/index.html#kedrodatacatalog-experimental-feature). Given a Kedro Data Catalog `catalog`, the general pattern to add datasets into the Vizro data manager is:

```python
from vizro.integrations import kedro as kedro_integration
from vizro.managers import data_manager


for dataset_name, dataset in kedro_integration.datasets_from_catalog(catalog).items():
    data_manager[dataset_name] = dataset
```

This imports all datasets of type [`kedro_datasets.pandas`](https://docs.kedro.org/en/stable/kedro_datasets.html) from the Kedro `catalog` into the Vizro `data_manager`.

The `catalog` variable may have been created in a number of different ways:

1. Kedro project path. Vizro exposes a helper function `vizro.integrations.kedro.catalog_from_project` to generate a `catalog` given the path to a Kedro project.
1. [Kedro Jupyter session](https://docs.kedro.org/en/stable/notebooks_and_ipython/kedro_and_notebooks.html). This automatically exposes `catalog`.
1. Data Catalog configuration file (`catalog.yaml`). This can create a `catalog` entirely independently of a Kedro project using [`kedro.io.DataCatalog.from_config`](https://docs.kedro.org/en/stable/kedro.io.DataCatalog.html#kedro.io.DataCatalog.from_config).

The full code for these different cases is given below.

!!! example "Import a Kedro Data Catalog into the Vizro data manager"
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

    === "app.py (Data Catalog configuration file)"
        ```python
        from kedro.io import DataCatalog
        import yaml

        from vizro.integrations import kedro as kedro_integration
        from vizro.managers import data_manager


        catalog = DataCatalog.from_config(yaml.safe_load(Path("catalog.yaml").read_text(encoding="utf-8")))

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

1. Kedro project path. Vizro exposes a helper function `vizro.integrations.kedro.pipelines_from_project` to generate a `pipelines` given the path to a Kedro project.
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
