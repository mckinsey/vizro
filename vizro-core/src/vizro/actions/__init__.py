"""Built-in actions, typically aliased as `va` using `import vizro.actions as va`.

Abstract: Usage documentation
    [How to use actions](../user-guides/actions.md)
"""

from vizro.actions._export_data import export_data
from vizro.actions._filter_interaction import filter_interaction
from vizro.actions._notifications import show_notification, update_notification
from vizro.actions._set_control import set_controls

# TODO[1.0.0]: remove this import and the `set_control` `__all__` entry — the deprecated alias module is deleted.
from vizro.actions._set_control_legacy import set_control
from vizro.actions._update_targets import update_targets

__all__ = [
    "export_data",
    "filter_interaction",
    "set_control",
    "set_controls",
    "show_notification",
    "update_notification",
    "update_targets",
]
