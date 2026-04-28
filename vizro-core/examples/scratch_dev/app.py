"""Scratch demo: Cascader vs Dropdown, hierarchical filters, set_control, and stress tests.

Page 2 tree size: set ``CASCADER_SHAPE`` to a tuple of positive ints (fan-out per level; last entry is leaf list
length). Dict keys / list values use letters ``a``, ``b``, ``c``, … by depth.

- **Page 1:** Gapminder 2007 scatter (two graphs). Top graph: ``vm.Filter(column=[...])`` with default hierarchical
  selector (implicit ``Cascader``, ``multi=True``). Bottom graph: same columns with explicit ``vm.Cascader(multi=False)``.
- **Page 2:** same comparison with page-level controls.
- **Page 3:** same four figure/parameter pairs, each parameter on a nested ``Container`` (outlined), 2x2 grid.
- **Page 4:** ``vm.Filter`` + hierarchical path columns in a DataFrame (same tree as page 2); echoes show the **filtered**
  ``data_frame`` (filters do not drive a ``.selected`` argument — use ``vm.Parameter`` for that, as on page 2).
- **Page 5:** ``set_control`` + ``Parameter`` with ``Cascader`` (single vs multi), driven by buttons.
- **Page 6:** stress cascaders built with ``_build_cascader_options`` (deep uneven shape and wide ``100 × 100``, ~10k+
  leaves each; aligned with ``vizro-dash-components/examples/pages/cascader_stress_test.py`` sizes).
"""

import vizro.actions as va
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro

df = px.data.iris()

static_notifications_page = vm.Page(
    title="static-notifications-page",
    layout=vm.Flex(),
    components=[
        vm.Button(
            id="success-notification-button",
            icon="check_circle",
            text="Success Notification",
            actions=[
                va.show_notification(
                    id="success-notification",
                    text="Operation completed successfully!",
                    variant="success",
                    auto_close=False,
                )
            ],
        ),
        vm.Button(
            id="warning-notification-button",
            icon="warning",
            text="Warning Notification",
            actions=[
                va.show_notification(
                    id="warning-notification",
                    text="Please review this warning message.",
                    variant="warning",
                    auto_close=False,
                )
            ],
        ),
        vm.Button(
            id="error-notification-button",
            icon="error",
            text="Error Notification",
            actions=[
                va.show_notification(
                    id="error-notification",
                    text="An error occurred during the operation.",
                    variant="error",
                    auto_close=False,
                )
            ],
        ),
        vm.Button(
            id="info-notification-button",
            icon="info",
            text="Info Notification",
            actions=[
                va.show_notification(
                    id="info-notification",
                    text="Here's some useful information for you.",
                    variant="info",
                    auto_close=False,
                )
            ],
        ),
        vm.Button(
            id="custom-notification-button",
            icon="celebration",
            text="Custom Notification",
            actions=[
                va.show_notification(
                    id="custom-notification",
                    text="Check out this new feature we've added!",
                    title="New Feature",
                    variant="success",
                    icon="celebration",
                    auto_close=False,
                )
            ],
        ),
        vm.Button(
            id="progress-notification-button",
            text="1. Show Loading",
            icon="hourglass_empty",
            actions=[
                va.show_notification(
                    id="update-notification",
                    text="Processing...",
                    title="Processing",
                    variant="progress",
                )
            ],
        ),
        vm.Button(
            id="update-notification-button",
            text="2. Update to Complete",
            icon="check_circle",
            actions=[
                va.update_notification(
                    notification="update-notification",
                    text="Your operation has been updated successfully.",
                    title="Complete",
                    variant="success",
                    auto_close=False,
                )
            ],
        ),
        vm.Button(
            id="link-notification-button",
            text="Markdown with Link",
            icon="link",
            actions=[
                va.show_notification(
                    id="link-notification",
                    text="This is a notification with a link to [Filters page](/filters-page-tabs--containers).",
                    title="Learn More",
                    auto_close=False,
                )
            ],
        ),
        vm.Button(
            id="auto-close-notification-button",
            text="Auto-Close",
            icon="close",
            actions=[
                va.show_notification(
                    id="auto-close-notification",
                    text="This notification will close automatically.",
                    title="Auto-Close",
                    variant="info",
                )
            ],
        ),
    ],
)

dashboard = vm.Dashboard(pages=[static_notifications_page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
