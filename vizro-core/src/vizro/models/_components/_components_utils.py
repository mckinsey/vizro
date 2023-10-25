import logging

from vizro.managers import data_manager

logger = logging.getLogger(__name__)


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
