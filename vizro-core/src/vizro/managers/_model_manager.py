"""The model manager handles access to all `VizroBaseModel` instances used in a Vizro app."""

from __future__ import annotations

from collections.abc import Collection, Generator, Mapping
from typing import TYPE_CHECKING, TypeVar

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


# TODO: Re-implement the duplicate ID error and investigate further why things (atm) are working nonetheless:
# Duplicate ID on Tabs Containers caused the duplicate not to appear in the tree, BUT the page worked as intended, why?
# Very likely because we still get to the model via the parent model when we iterate over the tabs field
class DuplicateIDError(ValueError):
    """Useful for providing a more explicit error message when a model has id set automatically, e.g. Page."""


class ModelNotFoundError(KeyError):
    """Raised when a model ID is not found in the tree."""


class VizroTree(TypedTree):
    """Thin subclass of TypedTree with model iteration methods.

    Note: We do NOT override __getitem__ because the parent TypedTree uses it to access nodes
    during tree building. Use get_model() to look up models by ID instead.
    """

    def get_model(self, model_id: ModelID) -> VizroBaseModel:
        """Look up a model by its ID.

        Raises:
            ModelNotFoundError: If the model ID is not found in the tree.
        """
        node = self.find_first(data_id=model_id)
        if node is None:
            raise ModelNotFoundError(f"Model with ID '{model_id}' not found in the tree.")
        return node.data

    def iter_model_ids(self) -> Generator[ModelID, None, None]:
        """Iterate through all model IDs."""
        for node in self.iterator():
            yield node.data.id

    def _get_model_children(self, model: Model) -> Generator[Model, None, None]:
        """Iterate through children of `model` with depth-first pre-order traversal."""
        node = self.find_first(data_id=model.id)
        yield from (n.data for n in node.iterator(add_self=True))

    def get_models(
        self,
        model_type: type[Model] | tuple[type[Model], ...] | type[FIGURE_MODELS] | None = None,
        root_model: VizroBaseModel | Mapping[str, Model] | Collection[Model] | None = None,
    ) -> Generator[Model, None, None]:
        """Iterate through all models of type `model_type` (including subclasses).

        If `model_type` is specified, return only models matching that type. Otherwise, include all types.
        If `root_model` is specified, return only models that are descendants of the given `root_model`.

        Note: For figure models, pass `FIGURE_MODELS` sentinel which will be resolved to the actual types.
        """
        # Imported inside method to avoid circular imports at module level.
        import vizro.models as vm
        from vizro.models import VizroBaseModel

        if model_type is FIGURE_MODELS:
            model_type = (vm.Graph, vm.AgGrid, vm.Table, vm.Figure)  # type: ignore[assignment]

        # Get models from tree based on root_model
        if root_model is None:
            # Iterate entire tree
            models = (n.data for n in self.iterator() if isinstance(n.data, VizroBaseModel))
        elif isinstance(root_model, VizroBaseModel):
            # Single model - get its descendants
            models = self._get_model_children(root_model)
        elif isinstance(root_model, Mapping):
            # Mapping - extract VizroBaseModel instances and get descendants for each
            models_list: list[VizroBaseModel] = []
            for child in root_model.values():
                if isinstance(child, VizroBaseModel):
                    models_list.extend(list(self._get_model_children(child)))
            models = iter(models_list)
        elif isinstance(root_model, Collection) and not isinstance(root_model, str):
            # Collection - extract VizroBaseModel instances and get descendants for each
            models_list = []
            for child in root_model:
                if isinstance(child, VizroBaseModel):
                    models_list.extend(list(self._get_model_children(child)))
            models = iter(models_list)
        else:
            return  # return empty generator

        for model in models:
            if model_type is None or isinstance(model, model_type):
                yield model  # type: ignore[misc]

    def get_model_page(self, model: Model) -> Page | None:
        """Get the page containing `model`."""
        # Imported inside method to avoid circular imports at module level.
        from vizro.models import Page

        if isinstance(model, Page):
            return model

        for page in self.get_models(Page):
            # Check if model is in page's descendants by comparing IDs (not object identity)
            page_descendant_ids = {n.data.id for n in self.find_first(data_id=page.id).iterator(add_self=True)}
            if model.id in page_descendant_ids:
                return page

        return None

    def has_model(self, model_id: ModelID) -> bool:
        """Check if a model with the given ID exists in the tree."""
        return self.find_first(data_id=model_id) is not None

    def remove_model(self, model_id: ModelID) -> None:
        """Remove a model from the tree by its ID.

        Args:
            model_id: The ID of the model to remove.

        Note:
            If the model is not found, this is a no-op.
        """
        node = self.find_first(data_id=model_id)
        if node is not None:
            node.remove()


def get_tree() -> VizroTree:
    """Get the VizroTree for the current Dash app.

    This function is used at runtime (inside Dash callbacks) to access models.
    The tree is stored on the Dash app instance during `Vizro.build()`.
    """
    from dash import get_app

    try:
        app = get_app()
    except RuntimeError as e:
        raise RuntimeError(
            "get_tree() must be called within a Dash callback context. "
            "If you're in build-time code, use model._tree instead."
        ) from e

    if not hasattr(app, "vizro_tree"):
        raise RuntimeError("VizroTree not found on Dash app. Make sure Vizro.build() has been called.")

    return app.vizro_tree
