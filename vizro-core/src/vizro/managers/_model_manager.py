"""The model manager handles access to all `VizroBaseModel` instances used in a Vizro app."""
from __future__ import annotations

import random
import uuid
from typing import TYPE_CHECKING, Dict, Generator, NewType, Tuple, Type, TypeVar, cast

from vizro.managers._managers_utils import _state_modifier

if TYPE_CHECKING:
    from vizro.models import VizroBaseModel

rd = random.Random(0)

ModelID = NewType("ModelID", str)
Model = TypeVar("Model", bound="VizroBaseModel")


class DuplicateIDError(ValueError):
    """Useful for providing a more explicit error message when a model has id set automatically, e.g. Page."""


class ModelManager:
    def __init__(self):
        self.__models: Dict[ModelID, VizroBaseModel] = {}
        self._frozen_state = False

    @_state_modifier
    def __setitem__(self, model_id: ModelID, model: Model):
        if model_id in self.__models:
            raise DuplicateIDError(
                f"Model with id={model_id} already exists. Models must have a unique id across the whole dashboard. "
                f"If you are working from a Jupyter Notebook, please either restart the kernel, or "
                f"use 'from vizro import Vizro; Vizro._reset()`."
            )
        self.__models[model_id] = model

    def __getitem__(self, model_id: ModelID) -> VizroBaseModel:
        # Do we need to return deepcopy(self.__models[model_id]) to avoid adjusting element by accident?
        return self.__models[model_id]

    def __iter__(self) -> Generator[ModelID, None, None]:
        """Iterates through all models.

        Note this yields model IDs rather key/value pairs to match the interface for a dictionary.
        """
        yield from self.__models

    def _items_with_type(self, model_type: Type[Model]) -> Generator[Tuple[ModelID, Model], None, None]:
        """Iterates through all models of type `model_type` (including subclasses)."""
        for model_id in self:
            if isinstance(self[model_id], model_type):
                yield model_id, cast(Model, self[model_id])

    @staticmethod
    def _generate_id() -> ModelID:
        return ModelID(str(uuid.UUID(int=rd.getrandbits(128))))

    def _clear(self):
        self.__init__()  # type: ignore[misc]


model_manager = ModelManager()
