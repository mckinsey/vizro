import inspect
import subprocess
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

MODEL_NAME = "model_name"
ACTIONS_CHAIN = "ActionsChain"
ACTION = "actions"


@dataclass
class PathReplacement:
    detect_path: str
    replace_path: str
    from_import: Callable


@dataclass
class CapturedCallableInfo:
    name: str
    module: str
    args: List[Tuple[str, Any]]
    code: Optional[str] = None


REPLACEMENT_STRINGS = [
    PathReplacement("plotly.express", "px.", lambda x, y: "import vizro.plotly.express as px"),
    PathReplacement("vizro.tables", "", lambda x, y: f"from {x} import {y}"),
    PathReplacement("vizro.figures", "", lambda x, y: f"from {x} import {y}"),
    PathReplacement("vizro.actions", "", lambda x, y: f"from {x} import {y}"),
    PathReplacement("vizro.charts", "", lambda x, y: f"from {x} import {y}"),
]

STANDARD_IMPORT_PATHS = {
    "import vizro.models as vm",
    "from vizro import Vizro",
    "from vizro.managers import data_manager",
    "from vizro.models.types import capture", #TODO: could make conditional based on content
}


def _format_and_lint(code_string: str):
    # Tracking https://github.com/astral-sh/ruff/issues/659 for proper python API
    # Good example: https://github.com/astral-sh/ruff/issues/8401#issuecomment-1788806462
    formatted = subprocess.check_output(
        ["ruff", "format", "--silent", "--isolated", "-"], input=code_string, encoding="utf-8"
    )
    linted = subprocess.check_output(
        ["ruff", "check", "--fix", "--exit-zero", "--silent", "--isolated", "-"], input=formatted, encoding="utf-8"
    )
    return linted


def _get_import_statements(captured_info: List[CapturedCallableInfo]) -> Set[str]:
    import_paths = set()
    for info in captured_info:
        for replacement in REPLACEMENT_STRINGS:
            if replacement.detect_path in info.module:
                import_paths.add(replacement.from_import(replacement.detect_path, info.name))
    return import_paths


def _get_callable_code_strings(captured_info: List[CapturedCallableInfo]) -> Set[str]:
    code_strings = set()
    for info in captured_info:
        if info.code is not None:
            code_strings.add(info.code)
    return code_strings


def _get_data_manager_code_strings(captured_info: List[CapturedCallableInfo]) -> Set[str]:
    return {
        f'# data_manager["{arg[1]}"] = ===> Fill in here <==='
        for info in captured_info
        for arg in info.args
        if arg[0] == "data_frame"
    }


def _clean_module_string(module_string: str) -> str:
    return next(
        (replacement.replace_path for replacement in REPLACEMENT_STRINGS if replacement.detect_path in module_string),
        "",
    )


def _repr_clean(info: CapturedCallableInfo) -> str:
    """Alternative __repr__ method with cleaned module paths."""
    args = ", ".join(f"{key}={value!r}" for key, value in info.args)
    module_path = f"{info.module}"
    modified_module_path = _clean_module_string(module_path)
    x = f"{modified_module_path}{info.name}({args})"
    return x


def _dict_to_python(model_data: Any, captured_info: Optional[List[CapturedCallableInfo]] = None) -> str:
    """Function to generate python string from pydantic model dict."""
    from vizro.models.types import CapturedCallable  # TODO: can we get rid of this?

    if captured_info is None:
        captured_info = []

    if isinstance(model_data, Dict):
        if MODEL_NAME in model_data:
            model_name = model_data.pop(MODEL_NAME)
            if model_name == ACTIONS_CHAIN:
                action_data = model_data[ACTION]
                if isinstance(action_data, List):
                    return ", ".join(_dict_to_python(item, captured_info) for item in action_data)
                else:
                    return _dict_to_python(action_data, captured_info)
            else:
                other_content = ", ".join(
                    f"{key}={_dict_to_python(value, captured_info)}" for key, value in model_data.items()
                )
                return f"vm.{model_name}({other_content})"
        else:
            return ", ".join(f"{key}={_dict_to_python(value, captured_info)}" for key, value in model_data.items())
    elif isinstance(model_data, List):
        return "[" + ", ".join(_dict_to_python(item, captured_info) for item in model_data) + "]"
    elif isinstance(model_data, CapturedCallable):
        info = CapturedCallableInfo(
            name=model_data._function.__name__,
            module=model_data._function.__module__,
            args=list(model_data._arguments.items()),
            code=inspect.getsource(model_data._function)
            if all(
                replacement.detect_path not in model_data._function.__module__ for replacement in REPLACEMENT_STRINGS
            )
            else None,
        )
        captured_info.append(info)
        return _repr_clean(info=info)

    return repr(model_data)
