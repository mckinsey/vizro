"""Unit tests for vizro.integrations.kedro."""

from importlib.metadata import version
from pathlib import Path

import kedro.pipeline as kp
import pytest
from kedro.config import OmegaConfigLoader
from packaging.version import parse

from vizro.integrations.kedro import catalog_from_project, datasets_from_catalog, pipelines_from_project

# KedroDataCatalog was experimental in kedro<1 and became the new DataCatalog in Kedro 1.0.0.
# Before 1.0.0, we need to support both the old DataCatalog and then new KedroDataCatalog
# Kedro projects are created with the following command. Note you can't just do `kedro new --example` or it will not
# use the starter of the right version.
# kedro new --name=kedro_<version>_project --starter=spaceflights-pandas --telemetry=no --checkout <version>h
# Then remove:
#  * dummy_confusion_matrix entry in catalog.yml because it has different dependencies for different
#    Kedro versions.
#  * Kedro project tests directory so pytest doesn't get confused.

LEGACY_KEDRO = parse(version("kedro")) < parse("1.0.0")

if not LEGACY_KEDRO:
    from kedro.io import DataCatalog

    kedro_project_path = Path(__file__).parent / "kedro-1-0-0-project"
    data_catalog_classes = [DataCatalog]
else:
    from kedro.io import DataCatalog as LegacyDataCatalog
    from kedro.io import KedroDataCatalog as DataCatalog

    kedro_project_path = Path(__file__).parent / "kedro-0-19-9-project"
    data_catalog_classes = [DataCatalog, LegacyDataCatalog]


# Fetch catalog from catalog.yml that does not live in a real project. This gives us a way to
# test dataset factories. We test both new and legacy DataCatalog classes for kedro < 1.0.0.
@pytest.fixture(params=data_catalog_classes)
def catalog_no_project(request):
    data_catalog_class = request.param
    source = Path(__file__).parent / "not-kedro-project"
    conf_loader = OmegaConfigLoader(source)
    return data_catalog_class.from_config(conf_loader["catalog"])


class TestCatalogFromProject:
    def test_save_on_close(self):
        with pytest.raises(ValueError, match="`catalog_from_project` always runs with `save_on_close=False`"):
            catalog_from_project(save_on_close=True)

    def test_invalid_project_path(self, monkeypatch):
        # Error raised by Kedro when invalid project_path supplied.
        with pytest.raises(RuntimeError, match=r"Could not find the project configuration file 'pyproject.toml'"):
            catalog_from_project(project_path=kedro_project_path.parent)

    # When no project_path is supplied explicitly, catalog_from_projects infers it automatically.
    @pytest.mark.parametrize(
        "cwd, project_path",
        [
            (None, kedro_project_path),  # cwd doesn't matter if project_path given explicitly.
            (kedro_project_path, None),  # project_path inferred automatically if at root of project.
            (kedro_project_path / "conf", None),  # project_path inferred automatically if inside project.
        ],
    )
    def test_catalog_from_project(self, monkeypatch, cwd, project_path):
        if cwd is not None:
            monkeypatch.chdir(cwd)
        # Filter out parameters that are added by Kedro context and we don't care about.
        catalog = catalog_from_project(project_path)
        if not LEGACY_KEDRO:
            dataset_names = {
                dataset_name
                for dataset_name in catalog
                if not (dataset_name.startswith("params:") or dataset_name == "parameters")
            }
        else:
            # catalog itself is not iterable: need to use catalog.list.
            dataset_names = {
                dataset_name
                for dataset_name in catalog.list()
                if not (dataset_name.startswith("params:") or dataset_name == "parameters")
            }

        expected = {
            "companies",
            "model_input_table",
            "preprocessed_companies",
            "preprocessed_shuttles",
            "regressor",
            "reviews",
            "shuttle_passenger_capacity_plot_exp",
            "shuttle_passenger_capacity_plot_go",
            "shuttles",
        }

        if LEGACY_KEDRO:
            # Legacy kedro project doesn't have reporting pipeline.
            expected -= {"shuttle_passenger_capacity_plot_exp", "shuttle_passenger_capacity_plot_go"}

        assert dataset_names == expected


class TestPipelinesFromProject:
    @pytest.mark.parametrize(
        "cwd, project_path",
        [
            (None, kedro_project_path),  # cwd doesn't matter if project_path given explicitly.
            (kedro_project_path, None),  # project_path inferred automatically if at root of project.
            (kedro_project_path / "conf", None),  # project_path inferred automatically if inside project.
        ],
    )
    def test_pipelines_from_project(self, monkeypatch, cwd, project_path):
        if cwd is not None:
            monkeypatch.chdir(cwd)

        expected = {
            "__default__",
            "data_science",
            "data_processing",
            "reporting",
        }
        if LEGACY_KEDRO:
            # Legacy kedro project doesn't have reporting pipeline.
            expected -= {"reporting"}

        assert set(pipelines_from_project(project_path)) == expected


class TestDatasetsFromCatalog:
    def test_catalog_no_pipeline(self, catalog_no_project, mocker):
        datasets = datasets_from_catalog(catalog_no_project)
        assert set(datasets) == {"pandas_excel", "pandas_parquet"}

        # Make sure that dataset_name is bound early to the data loading function.
        mocker.patch.object(catalog_no_project, "release")
        mocker.patch.object(catalog_no_project, "load")
        for dataset_name, dataset_loader in datasets.items():
            dataset_loader()
            catalog_no_project.release.assert_called_with(dataset_name)
            catalog_no_project.load.assert_called_with(dataset_name)

    # A bit of an integration test on a real project.
    def test_catalog_project_no_pipeline(self, mocker):
        catalog = catalog_from_project(kedro_project_path)
        datasets = datasets_from_catalog(catalog)
        assert set(datasets) == {
            "companies",
            "model_input_table",
            "preprocessed_companies",
            "preprocessed_shuttles",
            "reviews",
            "shuttles",
        }

        # Make sure that dataset_name is bound early to the data loading function.
        mocker.patch.object(catalog, "release")
        mocker.patch.object(catalog, "load")
        for dataset_name, dataset_loader in datasets.items():
            dataset_loader()
            catalog.release.assert_called_with(dataset_name)
            catalog.load.assert_called_with(dataset_name)

    def test_catalog_with_pipeline(self, catalog_no_project, mocker):
        pipeline = kp.pipeline(
            [
                kp.node(
                    func=lambda *args: None,
                    inputs=[
                        "pandas_excel",
                        "something#csv",
                        "something_else#csv",
                        "not_dataframe",
                        "not_in_catalog",
                        "parameters",
                        "params:z",
                    ],
                    outputs=None,
                ),
            ]
        )

        datasets = datasets_from_catalog(catalog_no_project, pipeline=pipeline)
        assert set(datasets) == {"pandas_excel", "pandas_parquet", "something#csv", "something_else#csv"}

        # Make sure that dataset_name is bound early to the data loading function.
        mocker.patch.object(catalog_no_project, "release")
        mocker.patch.object(catalog_no_project, "load")
        for dataset_name, dataset_loader in datasets.items():
            dataset_loader()
            catalog_no_project.release.assert_called_with(dataset_name)
            catalog_no_project.load.assert_called_with(dataset_name)
