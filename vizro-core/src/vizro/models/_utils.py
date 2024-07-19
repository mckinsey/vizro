import inspect
from dataclasses import dataclass
from typing import Optional, List, Dict

from vizro.models.types import CapturedCallable

MODEL_NAME = "model_name"

@dataclass
class CapturedCallableInfo:
    name: str
    import_path: str
    args: List
    code: Optional[str]


def transform_dict(d, captured_info=None):
    # Initialize the storage for CapturedCallable information if not already passed
    if captured_info is None:
        captured_info = []

    if isinstance(d, Dict):
        if MODEL_NAME in d:
            model_name = d.pop(MODEL_NAME)
            other_content = ", ".join(
                f"{key}={transform_dict(value, captured_info)}" for key, value in d.items()
            )
            return f"{model_name}({other_content})"
        else:
            return ", ".join(
                f"{key}={transform_dict(value, captured_info)}" for key, value in d.items()
            )
    elif isinstance(d, List):
        return "[" + ", ".join(transform_dict(item, captured_info) for item in d) + "]"
    elif isinstance(d, CapturedCallable):  # could also be dashboard ready figure?
        # Store the module of the _function attribute instead of printing it
        info = CapturedCallableInfo(
            name=d._function.__name__, import_path=d._function.__module__, args=list(d._arguments.items()),code=inspect.getsource(d._function)
        )
        captured_info.append(info)
        return d._repr_clean()

    return repr(d)  # Base case
