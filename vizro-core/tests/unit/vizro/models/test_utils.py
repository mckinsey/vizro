
from vizro.models._utils import _concatenate_code

extra_imports_string = "import vizro.models as vm\nimport pandas as pd"
code_string = "vm.Card(text='Foo')"
callable_defs_string = """def f():\n  return 'hi'"""
data_settings_string = """# data_manager["iris"] = ===> Fill in here <==="""

expected_assembled_linted_code = """############ Imports ##############
import vizro.models as vm


####### Function definitions ######
def f():
    return "hi"


####### Data Manager Settings #####
# #####!!! UNCOMMENT BELOW !!!#####
# data_manager["iris"] = ===> Fill in here <===


######### Dashboard code ##########
vm.Card(text="Foo")
"""

class TestCodeConcatenation:
    def test_concatenate_code(self):
        result = _concatenate_code(
            code=code_string,
            extra_imports=extra_imports_string,
            callable_defs=callable_defs_string,
            data_settings=data_settings_string,
        )
        assert result == expected_assembled_linted_code
