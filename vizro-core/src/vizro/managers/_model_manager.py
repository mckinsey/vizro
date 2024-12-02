"""The model manager handles access to all `VizroBaseModel` instances used in a Vizro app."""

from __future__ import annotations

import random
import uuid
from collections.abc import Generator, Iterable
from typing import TYPE_CHECKING, NewType, Optional, TypeVar, Union, cast

from vizro.managers._managers_utils import _state_modifier

if TYPE_CHECKING:
    from vizro.models import Page, VizroBaseModel


# As done for Dash components in dash.development.base_component, fixing the random seed is required to make sure that
# the randomly generated model ID for the same model matches up across workers when running gunicorn without --preload.
rd = random.Random(0)

ModelID = NewType("ModelID", str)
Model = TypeVar("Model", bound="VizroBaseModel")


# Sentinel object for models that are reactive to controls. This can't be done directly by defining
# FIGURE_MODELS = (Graph, ...) due to circular imports. Done as class for mypy.
# https://stackoverflow.com/questions/69239403/type-hinting-parameters-with-a-sentinel-value-as-the-default
class FIGURE_MODELS:
    pass


class DuplicateIDError(ValueError):
    """Useful for providing a more explicit error message when a model has id set automatically, e.g. Page."""


class ModelManager:
    def __init__(self):
        self.__models: dict[ModelID, VizroBaseModel] = {}
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
        # TODO: should this yield models rather than model IDs? Should model_manager be more like set with a special
        #  lookup by model ID or more like dictionary?
        yield from self.__models

    def _get_models(
        self,
        model_type: Optional[Union[type[Model], tuple[type[Model], ...], type[FIGURE_MODELS]]] = None,
        page: Optional[Page] = None,
    ) -> Generator[Model, None, None]:
        """Iterates through all models of type `model_type` (including subclasses).

        If `model_type` not given then look at all models. If `page` specified then only give models from that page.
        """
        import vizro.models as vm

        if model_type is FIGURE_MODELS:
            model_type = (vm.Graph, vm.AgGrid, vm.Table, vm.Figure)
        models = self.__get_model_children(page) if page is not None else self.__models.values()

        # Convert to list to avoid changing size when looping through at runtime.
        for model in list(models):
            if model_type is None or isinstance(model, model_type):
                yield model

    def __get_model_children(self, model: Model) -> Generator[Model, None, None]:
        """Iterates through children of `model`.

        Currently looks only through certain fields so might miss some children models.
        """
        from vizro.models import VizroBaseModel

        if isinstance(model, VizroBaseModel):
            yield model

        # TODO: in future this list should not be maintained manually. Instead we should look through all model children
        # by looking at model.model_fields.
        model_fields = ["components", "tabs", "controls", "actions", "selector"]

        for model_field in model_fields:
            if (model_field_value := getattr(model, model_field, None)) is not None:
                if isinstance(model_field_value, list):
                    # For fields like components that are list of models.
                    for single_model_field_value in model_field_value:
                        yield from self.__get_model_children(single_model_field_value)
                else:
                    # For fields that have single model like selector.
                    yield from self.__get_model_children(model_field_value)
                # We don't handle dicts of models at the moment. See below TODO for how this will all be improved in
                #  future.

        # TODO: Add navigation, accordions and other page objects. Won't be needed once have made whole model
        #  manager work better recursively and have better ways to navigate the hierarchy. In pydantic v2 this would use
        #  model_fields. Maybe we'd also use Page (or sometimes Dashboard) as the central model for navigating the
        #  hierarchy rather than it being so generic.

    def _get_model_page(self, model: Model) -> Page:  # type: ignore[return]
        """Gets the page containing `model`."""
        from vizro.models import Page

        if isinstance(model, Page):
            return model

        for page in cast(Iterable[Page], self._get_models(Page)):
            if model in self.__get_model_children(page):
                return page

    @staticmethod
    def _generate_id() -> ModelID:
        return ModelID(str(uuid.UUID(int=rd.getrandbits(128))))

    def _clear(self):
        self.__init__()  # type: ignore[misc]


model_manager = ModelManager()
