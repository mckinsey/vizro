"""The action loop creates all the required action callbacks and its components."""

from dash import html

from vizro.actions._action_loop._action_loop_utils import _get_actions_on_registered_pages
from vizro.actions._action_loop._build_action_loop_callbacks import _build_action_loop_callbacks
from vizro.actions._action_loop._get_action_loop_components import _get_action_loop_components


class ActionLoop:
    @classmethod
    def _create_app_callbacks(cls) -> html.Div:
        """Builds callbacks for the action loop and for each Action in the Dashboard and returns their components.

        Returns
            List of required components for the action loop and for each `Action` in the `Dashboard`.

        """
        return html.Div([cls._build_action_loop(), cls._build_actions_models()], id="app_components_div", hidden=True)

    @staticmethod
    def _build_action_loop():
        """Builds callbacks for the action loop and returns required components for the action loop mechanism to work.

        Returns
            List of required components for the action loop e.g. List[dcc.Store, html.Div].

        """
        _build_action_loop_callbacks()
        return _get_action_loop_components()

    @staticmethod
    def _build_actions_models():
        """Builds a callback for each `Action` model and returns required components for these callbacks.

        Returns
            List of required components for each `Action` in the `Dashboard` e.g. List[dcc.Download]

        """
        actions = _get_actions_on_registered_pages()
        return html.Div([action.build() for action in actions], id="app_action_models_components_div", hidden=True)
