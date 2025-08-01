"""The model manager handles access to all `VizroBaseModel` instances used in a Vizro app."""

from __future__ import annotations

import random
import uuid
from collections.abc import Collection, Generator, Mapping
from typing import TYPE_CHECKING, Optional, TypeVar, Union

from nutree.typed_tree import TypedNode, TypedTree

if TYPE_CHECKING:
    from vizro.models import Dashboard, Page, VizroBaseModel
    from vizro.models.types import ModelID


# As done for Dash components in dash.development.base_component, fixing the random seed is required to make sure that
# the randomly generated model ID for the same model matches up across workers when running gunicorn without --preload.
rd = random.Random(0)

Model = TypeVar("Model", bound="VizroBaseModel")


# Sentinel object for models that are reactive to controls. This can't be done directly by defining
# FIGURE_MODELS = (Graph, ...) due to circular imports. Done as class for mypy.
# https://stackoverflow.com/questions/69239403/type-hinting-parameters-with-a-sentinel-value-as-the-default
class FIGURE_MODELS:
    pass


class DuplicateIDError(ValueError):
    """Useful for providing a more explicit error message when a model has id set automatically, e.g. Page."""


# TODO: Parameters don't work yet!!
class ModelManager:
    def __init__(self):
        # TODO: need to handle CapturedCallable in future too, which doesn't have .id
        self.__dashboard_tree = TypedTree(calc_data_id=lambda tree, data: data.id, forward_attrs=True)
        self._frozen_state = False

    # TODO[AM]: probably better to just instantiate model manager in Vizro and pass dashboard in init rather
    # than doing it as separate method here --> work out whether to put this __init__.
    def _set_dashboard(self, dashboard: Dashboard):
        self.__populate_tree(dashboard)

    def print_dashboard_tree(self):
        """Pretty print the dashboard tree."""
        return self.__dashboard_tree.print(
            title=False,
            repr=lambda node: f"{node.kind}: {node.__class__.__name__}(id={node.id})",
        )

    # TODO[AM]: Check if removal of __del__ was ok due to legacy actions.

    def __getitem__(self, model_id: ModelID) -> VizroBaseModel:
        return self.__dashboard_tree.find(data_id=model_id).data

    def _get_node(self, model_id: ModelID) -> TypedNode[VizroBaseModel]:
        """Get the tree node for a given model ID."""
        return self.__dashboard_tree[model_id]

    def _get_tree(self) -> TypedTree[VizroBaseModel]:
        """Get the dashboard tree."""
        return self.__dashboard_tree

    def __iter__(self) -> Generator[TypedNode[VizroBaseModel], None, None]:
        """Iterates through all models in depth-first pre-order traversal."""
        # TODO: should this yield models rather than nodes? Should model_manager be more like set with a special
        #  lookup by model ID or more like dictionary?
        yield from iter(self.__dashboard_tree)

    def _get_models(
        self,
        model_type: Optional[Union[type[Model], tuple[type[Model], ...], type[FIGURE_MODELS]]] = None,
        root_model: Optional[VizroBaseModel] = None,
    ) -> Generator[Model, None, None]:
        """Iterates through all models of type `model_type` (including subclasses).

        Args:
            model_type: If specified, return only models matching that type. Otherwise, include all types.
            root_model: If specified, return only models that are descendants of the given `root_model`.

        Yields:
            Models matching the specified criteria in pre-order traversal.
        """
        import vizro.models as vm

        if model_type is FIGURE_MODELS:
            model_type = (vm.Graph, vm.AgGrid, vm.Table, vm.Figure)  # type: ignore[assignment]

        # Determine which nodes to iterate through based on root_model
        nodes = iter(self.__dashboard_tree[root_model.id]) if root_model is not None else iter(self.__dashboard_tree)

        for node in nodes:
            model = node.data
            if model_type is None or isinstance(model, model_type):
                yield model

    def __populate_tree(
        self,
        model: Union[Model, Mapping[str, Model], Collection[Model]],
        parent: Optional[Model] = None,
        field_name: Optional[str] = None,
    ):
        """Iterates through children of `model` with depth-first pre-order traversal."""
        # TODO: decide if we want to refine this method.
        from vizro.models import VizroBaseModel

        if isinstance(model, VizroBaseModel):
            if parent is None:
                # TODO: Maybe dashboard should be actual tree root instead (so Tree("dashboard")) but note there's no
                # way to attach data to it then.
                self.__dashboard_tree.add(model, kind="dashboard")
            else:
                self.__dashboard_tree[parent].add(model, kind=field_name)

            for model_field in model.__class__.model_fields:
                self.__populate_tree(getattr(model, model_field), model, model_field)
        elif isinstance(model, Mapping):
            # We don't look through keys because Vizro models aren't hashable.
            for child_model in model.values():
                self.__populate_tree(child_model, parent, field_name)
        elif isinstance(model, Collection):
            for child_model in model:
                if not isinstance(child_model, str):
                    self.__populate_tree(child_model, parent, field_name)

    def _get_model_page(self, model: Model) -> Page:
        """Gets the page containing `model`."""
        from vizro.models import Page

        if isinstance(model, Page):
            return model

        # Find the model's node in the tree and walk up to find the Page
        current_node = self.__dashboard_tree[model.id]
        if not current_node:
            raise ValueError(f"Model with id='{model.id}' not found in dashboard tree")

        while current_node.parent:
            current_node = current_node.parent
            if isinstance(current_node.data, Page):
                return current_node.data

        raise ValueError(f"Model with id='{model.id}' is not contained within any Page")

    @staticmethod
    def _generate_id() -> ModelID:
        return str(uuid.UUID(int=rd.getrandbits(128)))

    def _clear(self):
        self.__init__()  # type: ignore[misc]


model_manager = ModelManager()
