"""Unit tests for vizro.managers.data_manager."""
import pandas as pd
import pytest

from vizro.managers._data_manager import DataManager


class TestDataManager:
    def setup_method(self):
        self.data_manager = DataManager()
        self.data = pd.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6]})

    def test_add_dataframe(self):
        dataset_name = "test_dataset"
        component_id = "component_id_a"
        self.data_manager[dataset_name] = self.data
        self.data_manager._add_component(component_id, dataset_name)
        assert self.data_manager._get_component_data(component_id).equals(self.data)

    def test_add_lazy_dataframe(self):
        dataset_name = "test_lazy_dataset"
        component_id = "component_id_b"

        def lazy_data():
            return self.data

        self.data_manager[dataset_name] = lazy_data
        self.data_manager._add_component(component_id, dataset_name)
        assert self.data_manager._get_component_data(component_id).equals(lazy_data())

    def test_add_existing_dataset(self):
        dataset_name = "existing_dataset"
        self.data_manager[dataset_name] = self.data
        with pytest.raises(ValueError):
            self.data_manager[dataset_name] = self.data

    def test_add_invalid_dataset(self):
        dataset_name = "invalid_dataset"
        invalid_data = "not_a_dataframe"
        with pytest.raises(TypeError):
            self.data_manager[dataset_name] = invalid_data

    def test_add_component_to_nonexistent_dataset(self):
        component_id = "test_component"
        dataset_name = "nonexistent_dataset"
        with pytest.raises(KeyError):
            self.data_manager._add_component(component_id, dataset_name)

    def test_add_existing_component(self):
        component_id = "existing_component"
        dataset_name = "test_dataset"
        self.data_manager[dataset_name] = self.data
        self.data_manager._add_component(component_id, dataset_name)
        with pytest.raises(ValueError):
            self.data_manager._add_component(component_id, dataset_name)

    def test_get_component_data_nonexistent(self):
        dataset_name = "test_dataset"
        nonexistent_component = "nonexistent_component"
        self.data_manager[dataset_name] = self.data
        with pytest.raises(KeyError):
            self.data_manager._get_component_data(nonexistent_component)
