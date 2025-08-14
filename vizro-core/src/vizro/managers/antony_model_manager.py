"""The model manager handles access to all `VizroBaseModel` instances used in a Vizro app."""

from __future__ import annotations

import random
import uuid
from collections.abc import Collection, Generator, Iterable, Mapping
from typing import TYPE_CHECKING, Optional, TypeVar, Union, cast

from nutree import TypedTree

from vizro.managers._managers_utils import _state_modifier

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
        self.__models: dict[ModelID, VizroBaseModel] = {}
        # AM rough notes: need to handle CapturedCallable in future too? Which doesn't have .id
        # AM rough notes: forward_attrs=True looks nice for simplifying syntax.
        self.__dashboard_tree = TypedTree(calc_data_id=lambda tree, data: data.id)
        self._frozen_state = False

    # AM rough notes: probably better to just instantiate model manager in Vizro and pass dashboard in init rather
    # than doing it as separate method here.
    # Ideal next checkpoint future state: work out whether to put this __init__.
    def _set_dashboard(self, dashboard):
        self.__populate_tree(dashboard)
        d = self.__dashboard_tree
        # AM rough notes: importantly the nodes are just pointers to real objects so not duplicated in memory.
        # assert d.first_child().data.pages[0] is d["Test page"].data
        d.print(title=False, repr=lambda node: f"{node.kind}: {node.data.__class__.__name__}(id={node.id})")
        # repr = {node.data!r} is maybe the default and shows all fields too
        d.to_mermaid_flowchart(
            "graph.md",
            node_mapper='["{node.data.__class__.__name__}(id={node.id})"]',
            direction="LR",
            add_root=False,
            title=False,
        )

    # TODO: Consider storing "page_id" or "parent_model_id" and make searching helper methods easier?
    # Ideal next checkpoint future state: this is removed.
    @_state_modifier
    def __setitem__(self, model_id: ModelID, model: Model):
        if model_id in self.__models:
            raise DuplicateIDError(
                f"Model with id={model_id} already exists. Models must have a unique id across the whole dashboard. "
                f"If you are working from a Jupyter Notebook, please either restart the kernel, or "
                f"use 'from vizro import Vizro; Vizro._reset()`."
            )
        self.__models[model_id] = model

    # Ideal next checkpoint future state: this is removed. Maybe still be needed for temporary hack for actionschain
    # needed during 0.1.x -> 0.2.0 transition.
    @_state_modifier
    def __delitem__(self, model_id: ModelID):
        # Only required to handle legacy actions and could be removed when those are no longer needed.
        del self.__models[model_id]

    # Ideal next checkpoint future state: this still exists but uses self.__dashboard_tree.
    def __getitem__(self, model_id: ModelID) -> VizroBaseModel:
        # AM rough notes: smart lookup in nutree allows lookup by id and model itself and probably good to use here.
        # But there's unexpected behaviour/maybe a bug in nutree where you set Tree(calc_data_id) upfront.
        # Probably easy to fix.
        # AM rough notes: problem here probably caused by pre-build order in filters.
        print(model_id)
        return self.__dashboard_tree.find_first(data_id=model_id).data
        # Do we need to return deepcopy(self.__models[model_id]) to avoid adjusting element by accident?
        # return self.__models[model_id]

    # Ideal next checkpoint future state: this still exists but uses self.__dashboard_tree.
    def __iter__(self) -> Generator[ModelID, None, None]:
        """Iterates through all models.

        Note this yields model IDs rather key/value pairs to match the interface for a dictionary.
        """
        # TODO: should this yield models rather than model IDs? Should model_manager be more like set with a special
        #  lookup by model ID or more like dictionary?
        yield from self.__models

    # Ideal next checkpoint future state: this still exists but uses self.__dashboard_tree.
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
        models = self.__get_model_children(root_model) if root_model is not None else self.__models.values()

        # Convert to list to avoid changing size when looping through at runtime.
        for model in list(models):
            if model_type is None or isinstance(model, model_type):
                yield model  # type: ignore[misc]

    # Ideal next checkpoint future state: this method is removed.
    def __get_model_children(self, model: Model) -> Generator[Model, None, None]:
        """Iterates through children of `model`."""
        # AM: this is depth-first pre-order and matches nutree well
        from vizro.models import VizroBaseModel

        if isinstance(model, VizroBaseModel):
            yield model
            for model_field in model.__class__.model_fields:
                yield from self.__get_model_children(getattr(model, model_field))
        elif isinstance(model, Mapping):
            # We don't look through keys because Vizro models aren't hashable.
            for single_model in model.values():
                yield from self.__get_model_children(single_model)
        elif isinstance(model, Collection) and not isinstance(model, str):
            for single_model in model:
                yield from self.__get_model_children(single_model)

    def __populate_tree(self, model: Model, parent=None, field_name=None):
        """Iterates through children of `model` with depth-first pre-order traversal."""
        # AM rough notes: this is basically copied and pasted from __get_model_children and then modified to populate
        # dashboard tree instead of yielding.
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

    # Ideal next checkpoint future state: this still exists but uses self.__dashboard_tree.
    def _get_model_page(self, model: Model) -> Page:  # type: ignore[return]
        """Gets the page containing `model`."""
        from vizro.models import Page

        if isinstance(model, Page):
            return model

        for page in cast(Iterable[Page], self._get_models(Page)):
            if model in self.__get_model_children(page):  # type: ignore[operator]
                return page

    # Ideal next checkpoint future state: move this to VizroBaseModel set_id validator.
    @staticmethod
    def _generate_id() -> ModelID:
        return str(uuid.UUID(int=rd.getrandbits(128)))

    def _clear(self):
        self.__init__()  # type: ignore[misc]


model_manager = ModelManager()

"""
AM rough notes:

Options for how to translate pydantic models into tree with anytree:
1. model_dump -> dict -> import but then need to convert to children - might be able to keep isinstance since can
have non-json serialisable. Also problem with dashboard.model_dump(context={"add_name": True}, exclude_unset=False)
on our simple dashboard used in _to_python tests - haven't investigated why.
2. use as Mixin. Means doing multiple inheritance and already have clash with Page.path.

nutree seems much better overall.

Keep get_models etc. centralised into MM for now but then maybe move to Dashboard model later.

Might be useful to have property in every model to enable you to get to its Node in the tree or just a reference to the
whole dashboard tree? Basically this inserts model manager into every model so no need for global.

nutree supports custom tree traversal orders so we could write our own, but how would we define it in a better way than
priority = 1000 etc.?

CURRENT STATUS OF ABOVE CODE:
- tree seems to be populated correctly but worth checking
- tried swapping getitem to use dashboard_tree and seems to partially work but hits problem with not finding ids
probably due to order of prebuild and putting things in the tree
- next steps would be to try and remove __get_model_children and modifY other methods to use nutree navigation instead

Rough thoughts on how we might handle _is_container property. Could keep as property and/or:
key question is given model (or model.id), how to find corresponding node in the tree?

Dropdown()._nutree_node.up(2)
model_manager[dropdown_id].up(2)

Storing just parent as property in all model's seems like a worse version of storing the corresponding node:
dropdown._nutree_node
dropdown.)nutree_tree[dropdown.id]
"""
