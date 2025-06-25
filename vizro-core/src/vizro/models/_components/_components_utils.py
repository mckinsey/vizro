import logging
import uuid

from vizro.managers import data_manager

logger = logging.getLogger(__name__)


def _process_callable_data_frame(captured_callable):
    # Possibly all this validator's functionality should move into CapturedCallable (or a subclass of it) in the
    # future. This would mean that data is added to the data manager outside the context of a dashboard though,
    # which might not be desirable.
    data_frame = captured_callable["data_frame"]

    if isinstance(data_frame, str):
        # Named data source, which could be dynamic or static. This means px.scatter("iris") from the Python API and
        # specification of "data_frame": "iris" through JSON. In these cases, data already exists in the data manager.
        return captured_callable

    # Unnamed data source, which must be a pd.DataFrame and hence static data. This means px.scatter(pd.DataFrame())
    # and is only possible from the Python API. Extract dataframe from the captured function and put it into the
    # data manager.
    # Unlike with model_manager, it doesn't matter if the random seed is different across workers here. So long as
    # we always fetch static data from the data manager by going through the appropriate Figure component, the right
    # data source name will be fetched. It also doesn't matter if multiple Figures with the same underlying data
    # each have their own entry in the data manager, since the underlying pd.DataFrame will still be the same and
    # not copied into each one, so no memory is wasted.
    # Replace the "data_frame" argument in the captured callable with the data_source_name for consistency with
    # dynamic data and to save memory. This way we always access data via the same interface regardless of whether it's
    # static or dynamic.
    data_source_name = str(uuid.uuid4())
    data_manager[data_source_name] = data_frame
    captured_callable["data_frame"] = data_source_name

    return captured_callable
