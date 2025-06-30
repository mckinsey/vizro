"""Styling constants for the Vizro-AI chat component."""

CODE_BLOCK_CONTAINER_STYLE = {
    "position": "relative",
    "backgroundColor": "var(--surfaces-bg-card)",
    "borderRadius": "10px",
}

WRAPPER = {
    "width": "100%",
    "height": "100%",
    "display": "flex",
    "flexDirection": "column",
}

CHAT_CONTAINER_STYLE = {
    "display": "flex",
    "flexDirection": "column",
    "flex": "1",
    "width": "100%",
    "height": "100%",
}

CHAT_INPUT_WRAPPER_STYLE = {
    "display": "flex",
    "justifyContent": "center",
    "width": "100%",
    "marginTop": "auto",
}

CHAT_INPUT_CONTAINER_STYLE = {
    "borderRadius": "10px",
    "height": "80px",
    "backgroundColor": "var(--surfaces-bg-card)",
    "zIndex": "1",
    "width": "100%",
    "maxWidth": "760px",
}

CHAT_HISTORY_WRAPPER_STYLE = {
    "display": "flex",
    "justifyContent": "center",
    "width": "100%",
    "flex": "1",
    "overflow": "hidden",
}

CHAT_HISTORY_STYLE = {
    "width": "100%",
    "paddingBottom": "20px",
    "paddingLeft": "5px",
    "maxWidth": "760px",
    "overflow": "auto",
}

MESSAGE_STYLE = {
    "color": "var(--text-primary)",
    "padding": "10px 15px",
    "maxWidth": "96%",
    "marginLeft": "0",
    "marginRight": "auto",
    "marginBottom": "15px",
    "whiteSpace": "pre-wrap",
    "wordBreak": "break-word",
    "width": "fit-content",
    "minWidth": "100px",
    "lineHeight": "1.5",
    "letterSpacing": "0.2px",
    "borderRadius": "10px",
}

TEXTAREA_STYLE = {
    "height": "80px",  # This will be overridden by self.input_height
    "resize": "none",
    "borderBottomLeftRadius": "10px",
    "borderTopLeftRadius": "10px",
    "boxShadow": "none",
    "border": "1px solid var(--border-subtleAlpha01)",
} 
