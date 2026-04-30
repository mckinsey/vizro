"""Unit tests for ``vizro_experimental.chat`` (Chat model + base action helpers)."""

import base64
import inspect
from pathlib import Path

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pytest
from dash import dcc, html
from dash_iconify import DashIconify

from vizro_experimental.chat._constants import (
    CSS_ASSISTANT_MESSAGE,
    CSS_FILE_CHIP,
    CSS_FILE_CHIP_REMOVE,
    CSS_FILE_CHIP_UPLOADING,
    CSS_LOADING_MESSAGE,
    CSS_MESSAGE_BUBBLE,
    CSS_MESSAGE_WRAPPER,
)
from vizro_experimental.chat.actions._base_chat_action import (
    _BaseChatAction,
    _decoded_size,
    _file_meta_label,
    _format_size,
    _is_image_content,
    _loading_bubble,
    _register_loading_indicator_callback,
    _register_send_icon_toggle_callback,
)


def _data_url(mime: str, payload_bytes: bytes) -> str:
    return f"data:{mime};base64,{base64.b64encode(payload_bytes).decode()}"


def _walk(node):
    """Depth-first traversal yielding every Dash vnode in a subtree."""
    yield node
    children = getattr(node, "children", None)
    if children is None:
        return
    if not isinstance(children, (list, tuple)):
        children = [children]
    for child in children:
        yield from _walk(child)


def _collect_class_names(node) -> set[str]:
    return {token for vnode in _walk(node) for token in (getattr(vnode, "className", None) or "").split()}


def _collect_imgs(node) -> list[html.Img]:
    return [vnode for vnode in _walk(node) if isinstance(vnode, html.Img)]


def _find_iconify(node):
    return next((vnode for vnode in _walk(node) if isinstance(vnode, DashIconify)), None)


class _StubChat(_BaseChatAction):
    """Concrete stub so ``_file_chip`` can run without the action runtime."""

    def function(self, *args, **kwargs):  # type: ignore[override]
        raise NotImplementedError

    @property
    def outputs(self) -> list[str]:  # type: ignore[override]
        return []


@pytest.fixture()
def stub_chat():
    chat = _StubChat.__new__(_StubChat)
    chat._parent_model = type("P", (), {"id": "my-chat"})()
    return chat


class TestLoadingBubble:
    def test_outer_wrapper_has_message_wrapper_class(self):
        assert _loading_bubble().className == CSS_MESSAGE_WRAPPER

    def test_inner_div_has_bubble_assistant_and_loading_classes(self):
        inner = _loading_bubble().children
        for cls in (CSS_MESSAGE_BUBBLE, CSS_ASSISTANT_MESSAGE, CSS_LOADING_MESSAGE):
            assert cls in inner.className

    def test_contains_a_loader_component(self):
        loader = _loading_bubble().children.children
        assert isinstance(loader, dmc.Loader)


class TestLoadingIndicatorWiring:
    def test_main_chat_action_pre_build_registers_callback(self):
        src = inspect.getsource(_BaseChatAction.pre_build)
        assert "_register_loading_indicator_callback" in src

    def test_register_helper_appends_loading_bubble(self):
        src = inspect.getsource(_register_loading_indicator_callback)
        assert "_loading_bubble" in src


class TestStreamingChunkHandlerPreservesLoadingUX:
    """First streamed chunk must swap the loader for a real assistant bubble."""

    @classmethod
    def setup_class(cls):
        cls.js_source = (
            Path(__file__).parents[2] / "src" / "vizro_experimental" / "static" / "js" / "chat.js"
        ).read_text()

    def test_references_loading_class(self):
        assert CSS_LOADING_MESSAGE in self.js_source

    def test_has_first_chunk_replacement_branch(self):
        assert '"assistant"' in self.js_source
        assert "isLoadingPlaceholder" in self.js_source


class TestFormatSize:
    @pytest.mark.parametrize(
        "n,expected",
        [
            (0, ""),
            (-5, ""),
            (500, "500 B"),
            (1024, "1 KB"),
            (2048, "2 KB"),
            (1024 * 1024, "1.00 MB"),
            (int(1.28 * 1024 * 1024), "1.28 MB"),
        ],
    )
    def test_boundaries(self, n, expected):
        assert _format_size(n) == expected


class TestDecodedSize:
    def test_malformed_no_comma_returns_zero(self):
        assert _decoded_size("not-a-data-url") == 0

    def test_empty_returns_zero(self):
        assert _decoded_size("") == 0

    def test_recovers_original_byte_length(self):
        original = b"x" * 300
        url = _data_url("application/pdf", original)
        # Within one byte — base64 rounds to multiples of 3 bytes.
        assert abs(_decoded_size(url) - len(original)) <= 1

    def test_padding_is_subtracted(self):
        # 2 bytes → "aGk=" (1 padding char); padding must not inflate the answer.
        url = _data_url("text/plain", b"hi")
        assert _decoded_size(url) == 2


class TestIsImageContent:
    @pytest.mark.parametrize(
        "content,expected",
        [
            ("data:image/png;base64,abc", True),
            ("data:image/jpeg;base64,abc", True),
            ("data:application/pdf;base64,abc", False),
            ("data:text/csv;base64,abc", False),
            ("", False),
            ("not-a-data-url", False),
        ],
    )
    def test_prefix_detection(self, content, expected):
        assert _is_image_content(content) is expected


class TestFileMetaLabel:
    def test_ext_and_size_present(self):
        label = _file_meta_label("report.pdf", _data_url("application/pdf", b"x" * 1024))
        assert label.startswith("PDF ·")
        assert "KB" in label

    def test_ext_only_when_no_content(self):
        assert _file_meta_label("notes.txt", "") == "TXT"

    def test_size_only_when_no_ext(self):
        label = _file_meta_label("no-ext-file", _data_url("application/octet-stream", b"x" * 2048))
        assert label == "2 KB"

    def test_empty_when_nothing_available(self):
        assert _file_meta_label("no-ext", "") == ""


class TestFileChipRendering:
    def test_ready_chip_includes_remove_button(self, stub_chat):
        chip = stub_chat._file_chip({"filename": "x.txt", "content": ""}, index=0)
        assert CSS_FILE_CHIP_REMOVE in _collect_class_names(chip)

    def test_ready_chip_does_not_have_uploading_class(self, stub_chat):
        chip = stub_chat._file_chip({"filename": "x.txt", "content": ""}, index=0)
        assert CSS_FILE_CHIP_UPLOADING not in chip.className
        assert CSS_FILE_CHIP in chip.className

    def test_uploading_chip_hides_remove_button(self, stub_chat):
        chip = stub_chat._file_chip({"filename": "", "content": "", "status": "uploading"}, index=0)
        assert CSS_FILE_CHIP_REMOVE not in _collect_class_names(chip)

    def test_uploading_chip_has_uploading_class(self, stub_chat):
        chip = stub_chat._file_chip({"filename": "", "content": "", "status": "uploading"}, index=0)
        assert CSS_FILE_CHIP_UPLOADING in chip.className

    def test_image_chip_uses_img_thumbnail(self, stub_chat):
        src = _data_url("image/png", b"fake-png-bytes")
        chip = stub_chat._file_chip({"filename": "pic.png", "content": src}, index=0)
        imgs = _collect_imgs(chip)
        assert len(imgs) == 1
        assert imgs[0].src == src

    def test_document_chip_uses_icon_thumbnail(self, stub_chat):
        chip = stub_chat._file_chip(
            {"filename": "doc.pdf", "content": _data_url("application/pdf", b"x" * 16)}, index=0
        )
        assert not _collect_imgs(chip)
        assert _find_iconify(chip) is not None


class TestSendIconToggle:
    def test_main_chat_pre_build_registers_toggle(self):
        src = inspect.getsource(_BaseChatAction.pre_build)
        assert "_register_send_icon_toggle_callback" in src

    def test_toggle_callback_swaps_outline_and_filled(self):
        # Both icon names must appear so the branch can't silently collapse to one state.
        src = inspect.getsource(_register_send_icon_toggle_callback)
        assert "material-symbols-light:send-outline" in src
        assert "material-symbols-light:send'" in src or 'material-symbols-light:send"' in src


def _interactive_ids(node) -> set[str]:
    """Collect every string id attached to an interactive element (button or upload).

    Pattern-matching ids (dicts) are intentionally skipped — those buttons live inside
    string-id wrappers that carry the tooltip target.
    """
    ids: set[str] = set()
    for vnode in _walk(node):
        if not isinstance(vnode, (dmc.ActionIcon, dcc.Upload)):
            continue
        node_id = getattr(vnode, "id", None)
        if isinstance(node_id, str):
            ids.add(node_id)
    return ids


def _tooltip_targets(node) -> set[str]:
    """Collect every string `target` from dbc.Tooltip nodes in the tree."""
    return {
        vnode.target
        for vnode in _walk(node)
        if isinstance(vnode, dbc.Tooltip) and isinstance(getattr(vnode, "target", None), str)
    }


class TestChatComponentTooltipInvariant:
    """Every icon-only button in the Chat layout must be paired with a dbc.Tooltip.

    Guards against future button additions that ship without a discoverable label.
    """

    def _build_chat_layout(self, *, file_upload: bool, example_questions: list[str]):
        from vizro import Vizro

        from vizro_experimental.chat.models.chat import Chat

        Vizro._reset()
        chat = Chat(
            actions=[],
            file_upload=file_upload,
            placeholder="How can I help you?",
            example_questions=example_questions,
        )
        return html.Div([*chat._build_upload_stores(), chat._build_input_area()])

    @pytest.mark.parametrize(
        "file_upload,example_questions",
        [
            (True, ["Q1", "Q2"]),
            (False, []),
            (True, []),
            (False, ["Q1"]),
        ],
    )
    def test_every_button_has_a_tooltip(self, file_upload, example_questions):
        layout = self._build_chat_layout(file_upload=file_upload, example_questions=example_questions)
        button_ids = _interactive_ids(layout)
        tooltip_targets = _tooltip_targets(layout)
        missing = button_ids - tooltip_targets
        assert not missing, f"Chat buttons missing tooltips: {sorted(missing)}"


class TestPopupTooltipInvariant:
    """Every icon-only button in the chat popup surface must be paired with a dbc.Tooltip."""

    def _build_popup_layout(self):
        from vizro_experimental.chat.popup.popup import _build_chat_panel, _build_toggle_button

        return html.Div(
            [
                _build_chat_panel(chat_id="popup", placeholder="...", title="Assistant", streaming=True),
                _build_toggle_button(chat_id="popup"),
            ]
        )

    def test_every_button_has_a_tooltip(self):
        layout = self._build_popup_layout()
        button_ids = _interactive_ids(layout)
        tooltip_targets = _tooltip_targets(layout)
        missing = button_ids - tooltip_targets
        assert not missing, f"Popup buttons missing tooltips: {sorted(missing)}"

    def test_file_chip_remove_button_has_tooltip(self, stub_chat):
        # Pattern-id remove button is wrapped in a string-id html.Span; the tooltip targets that wrapper.
        chip = stub_chat._file_chip({"filename": "x.txt", "content": ""}, index=3)
        targets = _tooltip_targets(chip)
        wrapper_ids = {
            vnode.id
            for vnode in _walk(chip)
            if isinstance(vnode, html.Span) and isinstance(getattr(vnode, "id", None), str)
        }
        assert wrapper_ids & targets, "File chip remove button is not wrapped by a tooltip target"
