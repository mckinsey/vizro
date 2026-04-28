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

page = vm.Page(
    title="Basic notification",
    components=[
        vm.Button(
            text="Show notification",
            actions=va.show_notification(text="This is a default notification!"),
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run(debug=True)
