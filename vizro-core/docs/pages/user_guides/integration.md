# How to integrate Vizro with other tools

This page describes how to integrate Vizro with other tools.

## Kedro

[Kedro](https://docs.kedro.org/en/stable/index.html) is an open-source Python framework to create reproducible, maintainable, and
modular data science code. For Pandas datasets registered in a Kedro data catalog,
Vizro provides a convenient way to visualize them.

### Installation
To install Vizro with Kedro support, run:

```bash
pip install vizro[kedro]
```

### Using datasets from the Kedro data catalog
Given a Kedro data catalog (either from a kedro project or a `catalog.yml` style file), you can use the following code to
register the datasets with [`kedro_datasets.pandas`](https://docs.kedro.org/en/stable/kedro_datasets.html) type to Vizro's data manager.

!!! example "Kedro Data Catalog"
    === "app.py (kedro project)"
        ```py
        from vizro.integrations import kedro as kedro_integration
        from vizro.managers import data_manager


        catalog = kedro_integration.catalog_from_project("/path/to/projects/iris")

        for dataset_name, dataset in kedro_integration.datasets_from_catalog(catalog).items():
            data_manager[dataset_name] = dataset
        ```
    === "app.py (use data catalog file YAML syntax without a kedro project)"
        ```py
        from kedro.io import DataCatalog
        import yaml

        from vizro.integrations import kedro as kedro_integration
        from vizro.managers import data_manager


        catalog = DataCatalog.from_config(yaml.safe_load(Path("catalog.yaml").read_text(encoding="utf-8")))

        for dataset_name, dataset in kedro_integration.datasets_from_catalog(catalog).items():
            data_manager[dataset_name] = dataset
        ```
