"""Unit tests for ``vizro_experimental.chat.popup.popup``."""

import inspect

from vizro_experimental.chat.popup import popup as popup_module


class TestAddChatPopupWiring:
    def test_registers_loading_indicator_callback(self):
        src = inspect.getsource(popup_module.add_chat_popup)
        assert "_register_loading_indicator_callback" in src

    def test_registers_send_icon_toggle_callback(self):
        src = inspect.getsource(popup_module.add_chat_popup)
        assert "_register_send_icon_toggle_callback" in src
