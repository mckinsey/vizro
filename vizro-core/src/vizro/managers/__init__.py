"""Managers to handle access to key across a Vizro app."""

from ._data_manager import data_manager
from ._model_manager import model_manager

__all__ = ["data_manager", "model_manager"]
