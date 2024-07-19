import inspect
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Set

MODEL_NAME = "model_name"


@dataclass
class PathReplacement:
    detect_path: str
    replace_path: str
    from_import: Callable


@dataclass
class CapturedCallableInfo:
    name: str
    module: str
    args: List
    code: Optional[str] = None


REPLACEMENT_STRINGS = [
    PathReplacement("plotly.express", "px.", lambda x, y: "import vizro.plotly.express as px"),
    PathReplacement("vizro.tables", "", lambda x, y: f"from {x} import {y}"),
    PathReplacement("vizro.figures", "", lambda x, y: f"from {x} import {y}"),
    PathReplacement("vizro.actions", "", lambda x, y: f"from {x} import {y}"),
    PathReplacement("vizro.charts", "", lambda x, y: f"from {x} import {y}"),
]

STANDARD_IMPORT_PATHS = {"import vizro.models as vm", "from vizro import Vizro"}


def _determine_import_paths(captured_info: List[CapturedCallableInfo]) -> Set[str]:
    import_paths = set()
    for info in captured_info:
        for replacement in REPLACEMENT_STRINGS:
            if replacement.detect_path in info.module:
                import_paths.add(replacement.from_import(replacement.detect_path, info.name))
    return import_paths

def _get_code_strings(captured_info: List[CapturedCallableInfo]) -> Set[str]:
    code_strings = set()
    for info in captured_info:
        if info.code is not None:
            code_strings.add(info.code)
    return code_strings

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


def transform_dict(d, captured_info=None):
    from vizro.models.types import CapturedCallable
    # Initialize the storage for CapturedCallable information if not already passed
    if captured_info is None:
        captured_info = []

    if isinstance(d, Dict):
        if MODEL_NAME in d:
            model_name = d.pop(MODEL_NAME)
            other_content = ", ".join(f"{key}={transform_dict(value, captured_info)}" for key, value in d.items())
            return f"{model_name}({other_content})"
        else:
            return ", ".join(f"{key}={transform_dict(value, captured_info)}" for key, value in d.items())
    elif isinstance(d, List):
        return "[" + ", ".join(transform_dict(item, captured_info) for item in d) + "]"
    elif isinstance(d, CapturedCallable):  # could also be dashboard ready figure?
        # Store the module of the _function attribute instead of printing it
        info = CapturedCallableInfo(
            name=d._function.__name__,
            module=d._function.__module__,
            args=list(d._arguments.items()),
            code=inspect.getsource(d._function)
            if all(replacement.detect_path not in d._function.__module__ for replacement in REPLACEMENT_STRINGS)
            else None,
        )
        captured_info.append(info)
        return _repr_clean(info=info)

    return repr(d)  # Base case
