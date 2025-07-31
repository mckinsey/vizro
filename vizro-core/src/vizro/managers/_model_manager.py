"""The model manager handles access to all `VizroBaseModel` instances used in a Vizro app."""

from __future__ import annotations

import random
import uuid
from collections.abc import Collection, Generator, Mapping
from typing import TYPE_CHECKING, Optional, TypeVar, Union

from nutree import IterMethod, TypedTree

if TYPE_CHECKING:
    from vizro.models import Page, VizroBaseModel
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


class ModelManager:
    def __init__(self):
        # AM rough notes: need to handle CapturedCallable in future too? Which doesn't have .id
        # AM rough notes: forward_attrs=True looks nice for simplifying syntax.
        self.__dashboard_tree = TypedTree(calc_data_id=lambda tree, data: data.id)
        self._frozen_state = False

    # AM rough notes: probably better to just instantiate model manager in Vizro and pass dashboard in init rather
    # than doing it as separate method here.
    # Ideal next checkpoint future state: work out whether to put this __init__.
    def _set_dashboard(self, dashboard):
        self.__dashboard_tree.clear()
        self.__populate_tree(dashboard)

    def print_dashboard_tree(self):
        return self.__dashboard_tree.print(
            title=False,
            repr=lambda node: f"{node.kind}: {node.data.__class__.__name__}(id={node.data.id})",
        )

    # TODO: Consider storing "page_id" or "parent_model_id" and make searching helper methods easier?
    # Ideal next checkpoint future state: this is removed.

    # Ideal next checkpoint future state: this is removed. Maybe still be needed for temporary hack for actionschain
    # needed during 0.1.x -> 0.2.0 transition.
    # @_state_modifier
    # def __delitem__(self, model_id: ModelID):
    #     # Only required to handle legacy actions and could be removed when those are no longer needed.
    #     del self.__models[model_id]

    # Ideal next checkpoint future state: this still exists but uses self.__dashboard_tree. DONE
    def __getitem__(self, model_id: ModelID) -> VizroBaseModel:
        # Do we need to return deepcopy(self.__models[model_id]) to avoid adjusting element by accident?
        return self.__dashboard_tree.find(data_id=model_id).data

    # Ideal next checkpoint future state: this still exists but uses self.__dashboard_tree. DONE
    def __iter__(self) -> Generator[ModelID, None, None]:
        """Iterates through all models.

        Note this yields model IDs rather key/value pairs to match the interface for a dictionary.
        """
        # TODO: should this yield models rather than model IDs? Should model_manager be more like set with a special
        #  lookup by model ID or more like dictionary?
        # yield from self.__models
        yield from self.__dashboard_tree.iterator(method=IterMethod.PRE_ORDER)

    # Ideal next checkpoint future state: this still exists but uses self.__dashboard_tree. DONE
    def _get_models(
        self,
        model_type: Optional[Union[type[Model], tuple[type[Model], ...], type[FIGURE_MODELS]]] = None,
        root_model: Optional[VizroBaseModel] = None,
    ) -> Generator[Model, None, None]:
        """Iterates through all models of type `model_type` (including subclasses).

        If `model_type` is specified, return only models matching that type. Otherwise, include all types.
        If `root_model` is specified, return only models that are descendants of the given `root_model`.
        """
        import vizro.models as vm

        if model_type is FIGURE_MODELS:
            model_type = (vm.Graph, vm.AgGrid, vm.Table, vm.Figure)  # type: ignore[assignment]

        if root_model is not None:
            root_node = self.__dashboard_tree.find(data_id=root_model.id)
            nodes = root_node.iterator(method=IterMethod.PRE_ORDER) if root_node else []
        else:
            nodes = self.__dashboard_tree.iterator(method=IterMethod.PRE_ORDER)

        for node in nodes:
            model = node.data
            if model_type is None or isinstance(model, model_type):
                yield model

    def __populate_tree(
        self, model: Union[Model, Mapping[str, Model], Collection[Model]], parent=None, field_name=None
    ):
        """Iterates through children of `model` with depth-first pre-order traversal."""
        # AM rough notes: this is basically copied and pasted from __get_model_children and then modified to populate
        # dashboard tree instead of yielding.
        # MS: This misses items created in pre-build (like selectors) and "behind the scene" items like ActionsChain
        # (and possibly more)
        # TODO: decide if alternative scheme with init in
        # VizroBaseModel is satisfactory, luckily action chains are gone
        from vizro.models import VizroBaseModel

        if isinstance(model, VizroBaseModel):
            if parent is None:
                # AM rough notes:
                # Populate root node of dashboard. Maybe dashboard should be actual tree root instead
                # (so Tree("dashboard")) but note there's no way to attach data to it then.
                self.__dashboard_tree.add(model, kind="dashboard")
            else:
                self.__dashboard_tree[parent].add(model, kind=field_name)

            for model_field in model.__class__.model_fields:
                self.__populate_tree(getattr(model, model_field), model, model_field)
        elif isinstance(model, Mapping):
            # We don't look through keys because Vizro models aren't hashable.
            for child_model in model.values():
                self.__populate_tree(child_model, parent, field_name)
        elif isinstance(model, Collection) and not isinstance(model, str):
            for child_model in model:
                self.__populate_tree(child_model, parent, field_name)
        # TODO[MS]: does there not need to be a case for not being a model? I guess that should
        # just be caught by mypy

    def _get_model_page(self, model: Model) -> Page:
        """Gets the page containing `model`."""
        from vizro.models import Page

        if isinstance(model, Page):
            return model

        # Find the model's node in the tree and walk up to find the Page
        current_node = self.__dashboard_tree.find(data_id=model.id)
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
