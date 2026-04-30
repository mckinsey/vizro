"""Shared constants for the chat feature.

Mirrors ``vizro._constants``. CSS class names correspond to styles defined in
``src/vizro_experimental/static/css/chat.css`` and ``chat_popup.css``.
"""

# -------------------- CSS Class Names --------------------

CSS_MESSAGE_BUBBLE = "chat-message-bubble"
CSS_USER_MESSAGE = "chat-user-message"
CSS_ASSISTANT_MESSAGE = "chat-assistant-message"
CSS_MESSAGE_WRAPPER = "chat-message-wrapper"
CSS_USER_TEXT = "chat-user-text"
CSS_ROOT = "chat-root"
CSS_HISTORY_SECTION = "chat-history-section"
CSS_HISTORY_CONTAINER = "chat-history-container"
CSS_INPUT_SECTION = "chat-input-section"
CSS_INPUT_INNER = "chat-input-inner"
CSS_LOADING_MESSAGE = "chat-loading-message"
CSS_FILE_PREVIEW = "chat-file-preview"
CSS_DATA_INFO = "chat-data-info"
CSS_BUTTON_ROW = "chat-button-row"
CSS_LEFT_BUTTONS = "chat-left-buttons"
CSS_EXAMPLE_QUESTION_ITEM = "chat-example-question-item"
CSS_EXAMPLE_MENU_DROPDOWN = "chat-example-menu-dropdown"
CSS_FILE_CHIP = "chat-file-chip"
CSS_FILE_CHIP_THUMB = "chat-file-chip-thumb"
CSS_FILE_CHIP_THUMB_ICON = "chat-file-chip-thumb-icon"
CSS_FILE_CHIP_TEXT = "chat-file-chip-text"
CSS_FILE_CHIP_TITLE = "chat-file-chip-title"
CSS_FILE_CHIP_SUBTITLE = "chat-file-chip-subtitle"
CSS_FILE_CHIP_REMOVE = "chat-file-chip-remove"
CSS_FILE_CHIP_UPLOADING = "chat-file-chip-uploading"
CSS_USER_ATTACHMENTS = "chat-user-attachments"

# -------------------- Inline-style constants --------------------

# Chat input controls: 36x36 hit target pairs with a 24px glyph (Vizro-core default size,
# see vizro-core figures.css). Smaller than 32 felt cramped next to the Figma reference.
ICON_BUTTON_SIZE = "36px"

BORDER_RADIUS = "0px"
COLOR_TEXT_SECONDARY = "var(--text-secondary)"
PLOT_WIDTH = "600px"
PLOT_HEIGHT = "400px"
