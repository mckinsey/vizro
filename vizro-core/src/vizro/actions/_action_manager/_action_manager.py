"""The action manager handles creation of all required actions callbacks."""

from vizro.actions._action_manager._build_action_loop_callbacks import _build_action_loop_callbacks
from vizro.actions._action_manager._get_action_loop_components import _get_action_loop_components
from vizro.managers import model_manager
from vizro.models import Action


class ActionManager:
    @classmethod
    def build(cls):
        """Builds callbacks for the action loop and for each Action in the Dashboard and returns their components.

        Returns:
            All required components for the action loop and for each Action in the Dashboard.
        """
        return cls._build_action_loop() + cls._build_action_models()

    @staticmethod
    def _build_action_loop():
        """Builds callbacks for the action loop and gets all required components.

        Returns:
            All required components for the action loop.
        """
        _build_action_loop_callbacks()
        return _get_action_loop_components()

    @staticmethod
    def _build_action_models():
        """Builds a callback for each Action model in the Dashboard and gets all required components.

        Returns:
            All required components for each action model in the Dashboard.
        """
        return [
            action_component
            for _, action in model_manager._items_with_type(Action)
            for action_component in action.build()
        ]
