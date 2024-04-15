import logging
from functools import partial

from vizro.managers import data_manager
from vizro.models.types import CapturedCallable

try:
    from pydantic.v1 import validator
except ImportError:  # pragma: no cov
    from pydantic import validator

logger = logging.getLogger(__name__)


def _check_callable_mode(figure: CapturedCallable, mode: str) -> CapturedCallable:
    if mode != figure._mode:
        raise ValueError(f"CapturedCallable mode mismatch. Expected {mode} but got {figure._mode}.")
    return figure


def _callable_mode_validator_factory(mode: str):
    check_callable_mode = partial(_check_callable_mode, mode=mode)
    return validator("figure", allow_reuse=True)(check_callable_mode)


def _process_callable_data_frame(captured_callable, values):
    data_frame = captured_callable["data_frame"]

    # Enable running e.g. px.scatter("iris") from the Python API and specification of "data_frame": "iris" through JSON.
    # In these cases, data already exists in the data manager and just needs to be linked to the component.
    if isinstance(data_frame, str):
        data_manager._add_component(values["id"], data_frame)
        return captured_callable

    # Standard case for px.scatter(df: pd.DataFrame).
    # Extract dataframe from the captured function and put it into the data manager.
    dataset_name = str(id(data_frame))

    logger.debug("Adding data to data manager for Figure with id %s", values["id"])
    # If the dataset already exists in the data manager then it's not a problem, it just means that we don't need
    # to duplicate it. Just log the exception for debugging purposes.
    try:
        data_manager[dataset_name] = data_frame
    except ValueError as exc:
        logger.debug(exc)

    data_manager._add_component(values["id"], dataset_name)

    # No need to keep the data in the captured function any more so remove it to save memory.
    del captured_callable["data_frame"]
    return captured_callable
