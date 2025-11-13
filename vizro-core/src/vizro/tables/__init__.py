"""Built-in table functions, typically aliased as `vt` using `import vizro.tables as vt`.

Abstract: Usage documentation
    [How to use tables](../user-guides/table.md)
"""

from vizro.tables._dash_ag_grid import dash_ag_grid
from vizro.tables._dash_table import dash_data_table

__all__ = ["dash_ag_grid", "dash_data_table"]
