"""The model manager handles access to all `VizroBaseModel` instances used in a Vizro app."""

from __future__ import annotations

from collections.abc import Collection, Generator, Iterable, Mapping
from typing import TYPE_CHECKING, TypeVar, cast

from nutree.typed_tree import TypedTree

if TYPE_CHECKING:
    from vizro.models import Page, VizroBaseModel
    from vizro.models.types import ModelID


Model = TypeVar("Model", bound="VizroBaseModel")


# Sentinel object for models that are reactive to controls. This can't be done directly by defining
# FIGURE_MODELS = (Graph, ...) due to circular imports. Done as class for mypy.
# https://stackoverflow.com/questions/69239403/type-hinting-parameters-with-a-sentinel-value-as-the-default
class FIGURE_MODELS:
    pass


# TODO: Re-implement the dupicate ID error and investigate further why things (atm) are working nonetheless:
# Duplciate ID on Tabs Containers caused the duplicate not to appear in the tree, BUT the page worked as intended, why?
# Very likely because we still get to the model via the parent model when we iterator over the tabs field
class DuplicateIDError(ValueError):
    """Useful for providing a more explicit error message when a model has id set automatically, e.g. Page."""


class ModelManager:
    def __init__(self):
        self._frozen_state = False
        self._dashboard_tree: TypedTree | None = None

    def __getitem__(self, model_id: ModelID) -> VizroBaseModel:
        return self._dashboard_tree.find_first(data_id=model_id).data

    def __iter__(self) -> Generator[ModelID, None, None]:
        """Iterates through all models.

        Note this yields model IDs rather key/value pairs to match the interface for a dictionary.
        """
        # TODO: should this yield models rather than model IDs? Should model_manager be more like set with a special
        #  lookup by model ID or more like dictionary?
        for node in self._dashboard_tree.iterator():
            yield node.data.id

    def _get_models(
        self,
        model_type: type[Model] | tuple[type[Model], ...] | type[FIGURE_MODELS] | None = None,
        root_model: VizroBaseModel | Mapping[str, Model] | Collection[Model] | None = None,
    ) -> Generator[Model, None, None]:
        """Iterates through all models of type `model_type` (including subclasses).

        If `model_type` is specified, return only models matching that type. Otherwise, include all types.
        If `root_model` is specified, return only models that are descendants of the given `root_model`.
        """
        import vizro.models as vm
        from vizro.models import VizroBaseModel

        if model_type is FIGURE_MODELS:
            model_type = (vm.Graph, vm.AgGrid, vm.Table, vm.Figure)  # type: ignore[assignment]

        # Get models from tree based on root_model
        if root_model is None:
            # Iterate entire tree
            models = (n.data for n in self._dashboard_tree.iterator() if isinstance(n.data, VizroBaseModel))
        elif isinstance(root_model, VizroBaseModel):
            # Single model - get its descendants
            models = self.__get_model_children(root_model)
        elif isinstance(root_model, Mapping):
            # Mapping - extract VizroBaseModel instances and get descendants for each
            models = []
            for child in root_model.values():
                if isinstance(child, VizroBaseModel):
                    models.extend(list(self.__get_model_children(child)))
        elif isinstance(root_model, Collection) and not isinstance(root_model, str):
            # Collection - extract VizroBaseModel instances and get descendants for each
            models = []
            for child in root_model:
                if isinstance(child, VizroBaseModel):
                    models.extend(list(self.__get_model_children(child)))
        else:
            return  # return empty generator

        # Convert to list to avoid changing size when looping through at runtime.
        for model in models:
            if model_type is None or isinstance(model, model_type):
                yield model  # type: ignore[misc]

    def __get_model_children(self, model: Model) -> Generator[Model, None, None]:
        """Iterates through children of `model` with depth-first pre-order traversal."""
        node = self._dashboard_tree.find_first(data_id=model.id)
        yield from (n.data for n in node.iterator(add_self=True))

    def _get_model_page(self, model: Model) -> Page:  # type: ignore[return]
        """Gets the page containing `model`."""
        from vizro.models import Page

        if isinstance(model, Page):
            return model

        for page in cast(Iterable[Page], self._get_models(Page)):
            if model in self.__get_model_children(page):  # type: ignore[operator]
                return page

    def _clear(self):
        self.__init__()  # type: ignore[misc]


model_manager = ModelManager()
