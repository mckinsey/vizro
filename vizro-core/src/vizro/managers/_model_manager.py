"""The model manager handles access to all `VizroBaseModel` instances used in a Vizro app."""
from __future__ import annotations

import random
import uuid
from typing import TYPE_CHECKING, Dict, Generator, NewType, Tuple, Type, TypeVar, cast

from vizro.managers._managers_utils import _state_modifier

if TYPE_CHECKING:
    from vizro.models import VizroBaseModel, Page

rd = random.Random(0)

ModelID = NewType("ModelID", str)
Model = TypeVar("Model", bound="VizroBaseModel")


class DuplicateIDError(ValueError):
    """Useful for providing a more explicit error message when a model has id set automatically, e.g. Page."""

    pass


class ModelManager:
    def __init__(self):
        self.__models: Dict[ModelID, VizroBaseModel] = {}
        self._frozen_state = False

    # TODO: Consider do we need to save "page_id=None, parent_model_id=None" eagerly to the model itself
    #       and make all searching helper methods much easier?
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

    # TODO: Consider do we need to add additional argument "model_page_id=None"
    def _items_with_type(self, model_type: Type[Model]) -> Generator[Tuple[ModelID, Model], None, None]:
        """Iterates through all models of type `model_type` (including subclasses)."""
        for model_id in self:
            if isinstance(self[model_id], model_type):
                yield model_id, cast(Model, self[model_id])

    # TODO: Consider moving this one to the _callback_mapping_utils.py since it's only used there
    def _get_action_trigger(self, action_id: ModelID) -> VizroBaseModel:
        from vizro.models._action._actions_chain import ActionsChain

        for _, actions_chain in model_manager._items_with_type(ActionsChain):
            if action_id in [action.id for action in actions_chain.actions]:
                return self[actions_chain.trigger.component_id]

    # TODO: consider returning with yield
    def _get_model_children(self, model_id: ModelID) -> Set[ModelID]:
        """Gets all components and subpages recursively of the model with the `model_id`."""
        model_children = set()

        def __get_model_children_helper(model: VizroBaseModel) -> None:
            model_children.add(model.id)
            if hasattr(model, "components"):
                for sub_model in model.components:
                    __get_model_children_helper(model=sub_model)
            if hasattr(model, "subpages"):
                for sub_model in model.subpages:
                    __get_model_children_helper(model=sub_model)

        __get_model_children_helper(model=self.__models[model_id])
        return model_children

    # TODO: Consider moving this one into Dashboard or some util file
    def _get_model_page(self, model_id: ModelID) -> Page:
        """Gets the page id of the page that contains the model with the `model_id`."""
        from vizro.models import Page

        for page_id, _ in model_manager._items_with_type(Page):
            page_model_ids = [page_id, self._get_model_children(model_id=page_id)]
            page = self.__models[page_id]

            if hasattr(page, "actions"):
                for actions_chain in page._get_page_actions_chains():
                    page_model_ids.append(actions_chain.id)
                    for action in actions_chain.actions:
                        page_model_ids.append(action.id)

            for control in page.controls:
                page_model_ids.append(control.id)
                if hasattr(control, "selector") and control.selector:
                    page_model_ids.append(control.selector.id)

            # TODO: Add navigation, accordions and other page objects

            if model_id in page_model_ids:
                return page

    @staticmethod
    def _generate_id() -> ModelID:
        return ModelID(str(uuid.UUID(int=rd.getrandbits(128))))

    def _clear(self):
        self.__init__()  # type: ignore[misc]


model_manager = ModelManager()
