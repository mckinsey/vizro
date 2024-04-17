import logging
import uuid
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

    if isinstance(data_frame, str):
        # Named data source, which could be dynamic or static. This means px.scatter("iris") from the Python API and
        # specification of "data_frame": "iris" through JSON. In these cases, data already exists in the data manager
        # and just needs to be linked to the component.
        data_source_name = data_frame
    else:
        # Unnamed data source, which must be a pd.DataFrame and hence static data. This means px.scatter(pd.DataFrame())
        # and is only possible from the Python API. Extract dataframe from the captured function and put it into the
        # data manager.
        # Unlike with model_manager, it doesn't matter if the random seed is different across workers here. So long as
        # we always fetch static data from the data manager by going through the appropriate Figure component, the right
        # data source name will be fetched. It also doesn't matter if multiple Figures with the same underlying data
        # each have their own entry in the data manager, since the underlying pd.DataFrame will still be the same and
        # not copied into each one, so no memory is wasted.
        logger.debug("Adding data to data manager for Figure with id %s", values["id"])
        data_source_name = str(uuid.uuid4())
        data_manager[data_source_name] = data_frame

    data_manager._add_component(values["id"], data_source_name)
    # No need to keep the data in the captured function any more so remove it to save memory.
    del captured_callable["data_frame"]
    return captured_callable
