"""Styling constants for Chat model."""

# =============================================================================
# TOP LEVEL CONTAINERS
# =============================================================================

ROOT_CONTAINER = {
    "width": "100%",
    "height": "100%",
    "display": "flex",
    "flexDirection": "column",
}

MAIN_CONTAINER = {
    "display": "flex",
    "flexDirection": "column",
    "flex": "1",
    "width": "100%",
    "height": "100%",
}

# =============================================================================
# HISTORY SECTION (top half of chat)
# =============================================================================

HISTORY_SECTION = {
    "display": "flex",
    "justifyContent": "center",
    "width": "100%",
    "flex": "1",
    "overflow": "hidden",
}

HISTORY_CONTAINER = {
    "width": "100%",
    "paddingBottom": "20px",
    "paddingLeft": "5px",
    "maxWidth": "760px",
    "overflow": "auto",
}

MESSAGE_BUBBLE = {
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

CODE_BLOCK = {
    "position": "relative",
    "backgroundColor": "var(--surfaces-bg-card)",
    "borderRadius": "10px",
}

# =============================================================================
# INPUT SECTION (bottom half of chat)
# =============================================================================

INPUT_SECTION = {
    "display": "flex",
    "justifyContent": "center",
    "width": "100%",
    "marginTop": "auto",
}

INPUT_GROUP = {
    "borderRadius": "10px",
    "height": "80px",
    "backgroundColor": "var(--surfaces-bg-card)",
    "zIndex": "1",
    "width": "100%",
    "maxWidth": "760px",
}

INPUT_FIELD = {
    "height": "80px",  # This will be overridden by self.input_height
    "resize": "none",
    "borderBottomLeftRadius": "10px",
    "borderTopLeftRadius": "10px",
    "boxShadow": "none",
    "border": "1px solid var(--border-subtleAlpha01)",
} 
