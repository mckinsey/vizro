"""The action manager handles creation of all required actions callbacks."""

from typing import List, Union

from dash import dcc, html

from vizro.actions._action_loop._build_action_loop_callbacks import _build_action_loop_callbacks
from vizro.actions._action_loop._get_action_loop_components import _get_action_loop_components
from vizro.managers import model_manager
from vizro.models import Action


class ActionLoop:
    @classmethod
    def _create_app_callbacks(cls) -> List[Union[dcc.Store, html.Div, dcc.Download]]:
        """Builds callbacks for the action loop and for each Action in the Dashboard and returns their components.

        Returns:
            All required components for the action loop and for each Action in the Dashboard.
        """
        return cls._build_action_loop() + cls._build_actions_models()

    @staticmethod
    def _build_action_loop():
        """Builds callbacks for the action loop and returns required components for the action loop mechanism to work.

        Returns:
            List of all required components for the action loop. e.g. List of dcc.Store, html.Div components.
        """
        _build_action_loop_callbacks()
        return _get_action_loop_components()

    @staticmethod
    def _build_actions_models():
        """Builds a callback for Action model and returns required components for the Action model callback to work.

        Returns:
            List of all required components for each action model in the Dashboard. e.g. List of dcc.Download.
        """
        return [
            action_component
            for _, action in model_manager._items_with_type(Action)
            for action_component in action.build()
        ]
