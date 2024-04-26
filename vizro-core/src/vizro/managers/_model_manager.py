"""The model manager handles access to all `VizroBaseModel` instances used in a Vizro app."""

from __future__ import annotations

import random
import uuid
from typing import TYPE_CHECKING, Dict, Generator, List, NewType, Optional, Tuple, Type, TypeVar, cast

from vizro.managers._managers_utils import _state_modifier

if TYPE_CHECKING:
    from vizro.models import VizroBaseModel
    from vizro.models._action._actions_chain import ActionsChain

# As done for Dash components in dash.development.base_component, fixing the random seed is required to make sure that
# the randomly generated model ID for the same model matches up across workers when running gunicorn without --preload.
rd = random.Random(0)

ModelID = NewType("ModelID", str)
Model = TypeVar("Model", bound="VizroBaseModel")


class DuplicateIDError(ValueError):
    """Useful for providing a more explicit error message when a model has id set automatically, e.g. Page."""


class ModelManager:
    def __init__(self):
        self.__models: Dict[ModelID, VizroBaseModel] = {}
        self._frozen_state = False

    # TODO: Consider storing "page_id" or "parent_model_id" and make searching helper methods easier?
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

    # TODO: Consider adding an option to iterate only through specific page - "in_page_with_id=None"
    def _items_with_type(self, model_type: Type[Model]) -> Generator[Tuple[ModelID, Model], None, None]:
        """Iterates through all models of type `model_type` (including subclasses)."""
        for model_id in self:
            if isinstance(self[model_id], model_type):
                yield model_id, cast(Model, self[model_id])

    # TODO: Consider returning with yield
    # TODO: Make collection of model ids (throughout this file) to be Set[ModelID].
    def _get_model_children(self, model_id: ModelID, all_model_ids: Optional[List[ModelID]] = None) -> List[ModelID]:
        if all_model_ids is None:
            all_model_ids = []

        all_model_ids.append(model_id)
        model = self[model_id]
        if hasattr(model, "components"):
            for child_model in model.components:
                self._get_model_children(child_model.id, all_model_ids)
        if hasattr(model, "tabs"):
            for child_model in model.tabs:
                self._get_model_children(child_model.id, all_model_ids)
        return all_model_ids

    # TODO: Consider moving this method in the Dashboard model or some other util file
    def _get_model_page_id(self, model_id: ModelID) -> ModelID:  # type: ignore[return]
        """Gets the id of the page containing the model with "model_id"."""
        from vizro.models import Page

        for page_id, page in model_manager._items_with_type(Page):
            page_model_ids = [page_id, self._get_model_children(model_id=page_id)]

            for actions_chain in self._get_page_actions_chains(page_id=page_id):
                page_model_ids.append(actions_chain.id)
                for action in actions_chain.actions:
                    page_model_ids.append(action.id)

            for control in page.controls:
                page_model_ids.append(control.id)
                if hasattr(control, "selector") and control.selector:
                    page_model_ids.append(control.selector.id)

            # TODO: Add navigation, accordions and other page objects

            if model_id in page_model_ids:
                return cast(ModelID, page.id)

    # TODO: Increase the genericity of this method
    def _get_page_actions_chains(self, page_id: ModelID) -> List[ActionsChain]:
        """Gets all ActionsChains present on the page."""
        page = self[page_id]
        page_actions_chains = []

        for model_id in self._get_model_children(model_id=page_id):
            model = self[model_id]
            if hasattr(model, "actions"):
                page_actions_chains.extend(model.actions)

        for control in page.controls:
            if hasattr(control, "selector") and control.selector:
                page_actions_chains.extend(control.selector.actions)

        return page_actions_chains

    # TODO: Consider moving this one to the _callback_mapping_utils.py since it's only used there
    def _get_action_trigger(self, action_id: ModelID) -> VizroBaseModel:  # type: ignore[return]
        """Gets the model that triggers the action with "action_id"."""
        from vizro.models._action._actions_chain import ActionsChain

        for _, actions_chain in model_manager._items_with_type(ActionsChain):
            if action_id in [action.id for action in actions_chain.actions]:
                return self[ModelID(str(actions_chain.trigger.component_id))]

    def _get_page_model_ids_with_figure(self, page_id: ModelID) -> List[ModelID]:
        """Gets ids of all components from the page that have a 'figure' registered."""
        return [
            model_id
            for model_id in self._get_model_children(model_id=page_id)
            # Optimally this statement should be: "if isinstance(model, Figure)"
            if hasattr(model_manager[model_id], "figure")
        ]

    @staticmethod
    def _generate_id() -> ModelID:
        return ModelID(str(uuid.UUID(int=rd.getrandbits(128))))

    def _clear(self):
        self.__init__()  # type: ignore[misc]


model_manager = ModelManager()
