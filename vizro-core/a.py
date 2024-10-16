import textwrap
from vizro.models.types import capture
from typing import Optional

function_string = textwrap.dedent(
    """
    @capture("graph")
    def chart_dynamic(data_frame, hover_data: Optional[list[str]] = None):
        return px.bar(data_frame, x="sepal_width", y="sepal_length", hover_data=hover_data)
    """
)

exec(function_string)
print(locals())
# print(locals()["chart_dynamic"])
