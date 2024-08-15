import inspect
import subprocess
import textwrap
from dataclasses import dataclass
from typing import Any, List, Optional, Set

from vizro.managers import model_manager

MODEL_NAME = "model_name"
ACTIONS_CHAIN = "ActionsChain"
ACTION = "actions"

TO_PYTHON_TEMPLATE = """
############ Imports ##############
import vizro.plotly.express as px
import vizro.tables as vt
import vizro.models as vm
import vizro.actions as va
from vizro import Vizro
from vizro.models.types import capture
from vizro.managers import data_manager
{extra_imports}

{callable_defs}
{data_settings}

########### Model code ############
{code}
"""

CALLABLE_TEMPLATE = """
####### Function definitions ######
{callable_defs}
"""

DATA_TEMPLATE = """
####### Data Manager Settings #####
#######!!! UNCOMMENT BELOW !!!#####
# from vizro.managers import data_manager
{data_setting}
"""

@dataclass
class PathReplacement:
    original: str
    new: str

REPLACEMENT_STRINGS = [
    PathReplacement("plotly.express", "px."),
    PathReplacement("vizro.tables", "vt."),
    PathReplacement("vizro.figures", "vf."),
    PathReplacement("vizro.actions", "va."),
    PathReplacement("vizro.charts", "vc."),
]






def _format_and_lint(code_string: str) -> str:
    # Tracking https://github.com/astral-sh/ruff/issues/659 for proper python API
    # Good example: https://github.com/astral-sh/ruff/issues/8401#issuecomment-1788806462
    linted = subprocess.check_output(
        ["ruff", "check", "--fix", "--exit-zero", "--silent", "--isolated", "-"], input=code_string, encoding="utf-8"
    )
    formatted = subprocess.check_output(
        ["ruff", "format", "--silent", "--isolated", "-"], input=linted, encoding="utf-8"
    )
    return formatted


def _clean_module_string(module_string: str) -> str:
    return next(
        (replacement.new for replacement in REPLACEMENT_STRINGS if replacement.original in module_string),
        "",
    )


def _dict_to_python(object: Any) -> str:
    from vizro.models.types import CapturedCallable  # TODO: can we get rid of this?

    if isinstance(object, dict) and "__vizro_model__" in object:
        __vizro_model__ = object.pop("__vizro_model__")

        # This is required to back-engineer the actions chains. It is easier to handle in the string conversion here
        # than in the dict creation, because we end up with nested lists when being forced to return a list of actions.
        # If we handle it in dict of vm.BaseModel, then we created an unexpected dict return.
        if __vizro_model__ == ACTIONS_CHAIN:
            action_data = object[ACTION]
            # if isinstance(action_data, List):
            return ", ".join(_dict_to_python(item) for item in action_data)
            # else:
            #     return _dict_to_python(action_data)
        else:
            # This is very similar to doing repr but includes the vm. prefix and calls _object_to_python_code
            # rather than repr recursively.
            fields = ", ".join(f"{field_name}={_dict_to_python(value)}" for field_name, value in object.items())
            return f"vm.{__vizro_model__}({fields})"
    elif isinstance(object, dict):
        fields = ", ".join(f"{field_name}={_dict_to_python(value)}" for field_name, value in object.items())
        return "{" + fields + "}"
    elif isinstance(object, list):
        # Need to do this manually to avoid extra quotation marks that arise when doing repr(List).
        code_string = ", ".join(_dict_to_python(item) for item in object)
        return f"[{code_string}]"
    elif isinstance(object, CapturedCallable):
        return object._repr_clean()
    else:
        return repr(object)


def _concatenate_code(
    code: str,
    extra_imports: Optional[str] = None,
    callable_defs: Optional[str] = None,
    data_settings: Optional[str] = None,
) -> str:
    callable_defs = CALLABLE_TEMPLATE.format(callable_defs=callable_defs) if callable_defs else ""
    data_settings = DATA_TEMPLATE.format(data_setting=data_settings) if data_settings else ""
    unformatted_code = TO_PYTHON_TEMPLATE.format(
        code=code,
        extra_imports=extra_imports if extra_imports else "",
        callable_defs=callable_defs,
        data_settings=data_settings,
    )
    return _format_and_lint(unformatted_code)


def _extract_captured_callable_source() -> Set[str]:
    from vizro.models.types import CapturedCallable

    captured_callable_sources = set()
    for model_id in model_manager:
        for _, value in model_manager[model_id]:
            if isinstance(value, CapturedCallable) and all(replacement.original not in value._function.__module__ for replacement in REPLACEMENT_STRINGS):
                try:
                    source = textwrap.dedent(inspect.getsource(value._function))
                    captured_callable_sources.add(source)
                except OSError:
                    pass
    return captured_callable_sources


def _extract_captured_callable_data_info() -> Set[str]:
    from vizro.models.types import CapturedCallable

    return {
        f'# data_manager["{value._arguments["data_frame"]}"] = ===> Fill in here <==='
        for model_id in model_manager
        for _, value in model_manager[model_id]
        if isinstance(value, CapturedCallable)
        if "data_frame" in value._arguments
    }


if __name__ == "__main__":
    extra_imports = "import vizro.models as vm\nimport pandas as pd"
    code = "vm.Card(text='Foo')"
    callable_defs = """def f():
    return 'hi'
    """
    data_settings = """# data_manager["iris"] = ===> Fill in here <==="""
    print(
        _concatenate_code(
            code=code, extra_imports=extra_imports, callable_defs=callable_defs, data_settings=data_settings
        )
    )
