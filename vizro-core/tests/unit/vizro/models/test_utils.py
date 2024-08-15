import textwrap
from typing import List, Optional

import pytest
import vizro.models as vm
import vizro.plotly.express as px
from vizro.actions import export_data
from vizro.models._utils import _concatenate_code
from vizro.models.types import capture

extra_imports_string = "import vizro.models as vm\nimport pandas as pd"
code_string = "vm.Card(text='Foo')"
callable_defs_string = """def f():\n  return 'hi'"""
data_settings_string = """# data_manager["iris"] = ===> Fill in here <==="""

expected_assembled_linted_code = textwrap.dedent(
    """############ Imports ##############
import vizro.models as vm


####### Function definitions ######
def f():
    return "hi"


####### Data Manager Settings #####
#######!!! UNCOMMENT BELOW !!!#####
# from vizro.managers import data_manager
# data_manager["iris"] = ===> Fill in here <===


########### Model code ############
vm.Card(text="Foo")
"""
)


class TestCodeConcatenation:
    def test_concatenate_code(self):
        result = _concatenate_code(
            code=code_string,
            extra_imports=extra_imports_string,
            callable_defs=callable_defs_string,
            data_settings=data_settings_string,
        )
        assert result == expected_assembled_linted_code


@capture("graph")
def chart(data_frame, hover_data: Optional[List[str]] = None):
    return px.bar(data_frame, x="sepal_width", y="sepal_length", hover_data=hover_data)


@pytest.fixture
def page_pre_defined_actions():
    return vm.Page(
        title="Page 1",
        components=[
            vm.Graph(figure=px.bar("iris", x="sepal_width", y="sepal_length")),
            vm.Button(
                text="Export data",
                actions=[
                    vm.Action(function=export_data()),
                    vm.Action(function=export_data()),
                ],
            ),
        ],
    )


@pytest.fixture
def chart_dynamic():
    function_string = textwrap.dedent(
        """
        @capture("graph")
        def chart_dynamic(data_frame, hover_data: Optional[List[str]] = None):
            return px.bar(data_frame, x="sepal_width", y="sepal_length", hover_data=hover_data)
        """
    )

    local_scope = {}
    exec(function_string, globals(), local_scope)
    chart_dynamic = local_scope["chart_dynamic"]
    return chart_dynamic


expected_card = textwrap.dedent(
    """############ Imports ##############
import vizro.models as vm


########### Model code ############
model = vm.Card(text="Foo")
"""
)

expected_graph = textwrap.dedent(
    """############ Imports ##############
import vizro.plotly.express as px
import vizro.models as vm


####### Data Manager Settings #####
#######!!! UNCOMMENT BELOW !!!#####
# from vizro.managers import data_manager
# data_manager["iris"] = ===> Fill in here <===


########### Model code ############
model = vm.Graph(figure=px.bar(data_frame="iris", x="sepal_width", y="sepal_length"))
"""
)


expected_graph_with_callable = textwrap.dedent(
    """############ Imports ##############
import vizro.plotly.express as px
import vizro.models as vm
from vizro.models.types import capture
from typing import Optional, List


####### Function definitions ######
@capture("graph")
def chart(data_frame, hover_data: Optional[List[str]] = None):
    return px.bar(data_frame, x="sepal_width", y="sepal_length", hover_data=hover_data)


####### Data Manager Settings #####
#######!!! UNCOMMENT BELOW !!!#####
# from vizro.managers import data_manager
# data_manager["iris"] = ===> Fill in here <===


########### Model code ############
model = vm.Graph(figure=chart(data_frame="iris"))
"""
)


expected_actions_predefined = textwrap.dedent(
    """############ Imports ##############
import vizro.plotly.express as px
import vizro.models as vm
import vizro.actions as va


####### Data Manager Settings #####
#######!!! UNCOMMENT BELOW !!!#####
# from vizro.managers import data_manager
# data_manager["iris"] = ===> Fill in here <===


########### Model code ############
model = vm.Page(
    components=[
        vm.Graph(figure=px.bar(data_frame="iris", x="sepal_width", y="sepal_length")),
        vm.Button(
            text="Export data",
            actions=[
                vm.Action(function=va.export_data()),
                vm.Action(function=va.export_data()),
            ],
        ),
    ],
    title="Page 1",
)
"""
)


excepted_graph_dynamic = textwrap.dedent(
    """############ Imports ##############
import vizro.models as vm


####### Data Manager Settings #####
#######!!! UNCOMMENT BELOW !!!#####
# from vizro.managers import data_manager
# data_manager["iris"] = ===> Fill in here <===


########### Model code ############
model = vm.Graph(figure=chart_dynamic(data_frame="iris"))
"""
)

extra_callable = textwrap.dedent(
    """    @capture("graph")
    def extra(data_frame, hover_data: Optional[List[str]] = None):
        return px.bar(data_frame, x="sepal_width", y="sepal_length", hover_data=hover_data)
    """
)

expected_code_with_extra_callable = textwrap.dedent(
    """############ Imports ##############
import vizro.plotly.express as px
import vizro.models as vm
from vizro.models.types import capture


####### Function definitions ######
@capture("graph")
def extra(data_frame, hover_data: Optional[List[str]] = None):
    return px.bar(data_frame, x="sepal_width", y="sepal_length", hover_data=hover_data)


########### Model code ############
model = vm.Card(text="Foo")
"""
)


class TestPydanticPython:
    def test_to_python_basic(self):
        card = vm.Card(text="Foo")
        result = card._to_python()
        assert result == expected_card

    def test_to_python_data_manager(self):
        # Test if data manager code lines are included correctly in output
        graph = vm.Graph(figure=px.bar("iris", x="sepal_width", y="sepal_length"))
        result = graph._to_python()
        assert result == expected_graph

    def test_to_python_captured_callable_chart_plus_extra_imports(self):
        # Test if captured callable is included correctly in output
        # Test if extra imports are included correctly in output (typing yes, pandas no)
        graph = vm.Graph(figure=chart(data_frame="iris"))
        result = graph._to_python(extra_imports={"from typing import Optional, List", "import pandas as pd"})
        assert result == expected_graph_with_callable

    def test_to_python_pre_defined_actions(self, page_pre_defined_actions):
        # Test if pre-defined actions are included correctly in output, ie no ActionsChain model
        result = page_pre_defined_actions._to_python()
        assert result == expected_actions_predefined

    def test_to_python_no_source_code(self, chart_dynamic):
        # Check if to_python works if the source code is not available - here chart_dynamic is undefined
        graph = vm.Graph(figure=chart_dynamic(data_frame="iris"))
        result = graph._to_python()
        assert result == excepted_graph_dynamic

    def test_to_python_with_extra_callable(self):
        # Test if callable is included correctly in output
        card = vm.Card(text="Foo")
        result = card._to_python(extra_callable_defs={extra_callable})
        assert result == expected_code_with_extra_callable
