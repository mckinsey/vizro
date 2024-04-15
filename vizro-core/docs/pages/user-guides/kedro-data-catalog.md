# How to integrate Vizro with Kedro Data Catalog

This page describes how to integrate Vizro with [Kedro](https://docs.kedro.org/en/stable/index.html), an open-source Python framework to create reproducible, maintainable, and modular data science code. For Pandas datasets registered in a Kedro data catalog, Vizro provides a convenient way to visualize them.

## Installation
If you already have Kedro installed then you do not need to install any extra dependencies. If you do not have Kedro installed then you should run:

```bash
pip install vizro[kedro]
```

## Use datasets from the Kedro Data Catalog
`vizro.integrations.kedro` provides functions to help generate and process a [Kedro Data Catalog](https://docs.kedro.org/en/stable/data/index.html). Given a Kedro Data Catalog `catalog`, the general pattern to add datasets into the Vizro data manager is:
```python
from vizro.integrations import kedro as kedro_integration
from vizro.managers import data_manager


for dataset_name, dataset in kedro_integration.datasets_from_catalog(catalog).items():
    data_manager[dataset_name] = dataset
```

This imports all datasets of type [`kedro_datasets.pandas`](https://docs.kedro.org/en/stable/kedro_datasets.html) from the Kedro `catalog` into the Vizro `data_manager`.

The `catalog` variable may have been created in a number of different ways:

1. Kedro project path. Vizro exposes a helper function `vizro.integrations.kedro.catalog_from_project` to generate a `catalog` given the path to a Kedro project.
2. [Kedro Jupyter session](https://docs.kedro.org/en/stable/notebooks_and_ipython/kedro_and_notebooks.html). This automatically exposes `catalog`.
3. Data Catalog configuration file (`catalog.yaml`). This can create a `catalog` entirely independently of a Kedro project using [`kedro.io.DataCatalog.from_config`](https://docs.kedro.org/en/stable/kedro.io.DataCatalog.html#kedro.io.DataCatalog.from_config).

The full code for these different cases is given below.

!!! example "Import a Kedro Data Catalog into the Vizro data manager"

    === "app.py (Kedro project path)"
        ```py
        from vizro.integrations import kedro as kedro_integration
        from vizro.managers import data_manager


        catalog = kedro_integration.catalog_from_project("/path/to/kedro/project")

        for dataset_name, dataset in kedro_integration.datasets_from_catalog(catalog).items():
            data_manager[dataset_name] = dataset
        ```
    === "app.ipynb (Kedro Jupyter session)"
        ```py
        from vizro.managers import data_manager


        for dataset_name, dataset in kedro_integration.datasets_from_catalog(catalog).items():
            data_manager[dataset_name] = dataset
        ```
    === "app.py (Data Catalog configuration file)"
        ```py
        from kedro.io import DataCatalog
        import yaml

        from vizro.integrations import kedro as kedro_integration
        from vizro.managers import data_manager


        catalog = DataCatalog.from_config(yaml.safe_load(Path("catalog.yaml").read_text(encoding="utf-8")))

        for dataset_name, dataset in kedro_integration.datasets_from_catalog(catalog).items():
            data_manager[dataset_name] = dataset
        ```
