import logging
from typing import List, Literal

from dash import html
from pydantic import Field, PrivateAttr, validator

from vizro.managers import data_manager
from vizro.models import Action, VizroBaseModel
from vizro.models._action._actions_chain import _action_validator_factory
from vizro.models._models_utils import _log_call
from vizro.models.types import CapturedCallable

logger = logging.getLogger(__name__)


class Table(VizroBaseModel):
    """Wrapper for table components to visualize in dashboard.

    Args:
        type (Literal["table"]): Defaults to `"table"`.
        table (CapturedCallable): React object to be displayed.
        # actions (List[Action]): List of the Action objects, that allows to
        #     configure app interactions, triggered by affecting this component.
    """

    type: Literal["table"] = "table"
    table: CapturedCallable = Field(..., description="Table to be visualized on dashboard")
    actions: List[Action] = []

    # Component properties for actions and interactions
    _input_property: str = PrivateAttr("active_cell")
    _output_property: str = PrivateAttr("children")

    # validator
    set_actions = _action_validator_factory("active_cell")  # type: ignore[pydantic-field]

    @validator("table")
    def process_component_data_frame(cls, table, values):
        data_frame = table["data_frame"]

        # Enable running "iris" from the Python API and specification of "data_frame": "iris" through JSON.
        # In these cases, data already exists in the data manager and just needs to be linked to the component.
        if isinstance(data_frame, str):
            data_manager._add_component(values["id"], data_frame)
            return table

        # Standard case for df: pd.DataFrame.
        # Extract dataframe from the captured function and put it into the data manager.
        dataset_name = str(id(data_frame))

        logger.debug("Adding data to data manager for Graph with id %s", values["id"])
        # If the dataset already exists in the data manager then it's not a problem, it just means that we don't need
        # to duplicate it. Just log the exception for debugging purposes.
        try:
            data_manager[dataset_name] = data_frame
        except ValueError as exc:
            logger.debug(exc)

        data_manager._add_component(values["id"], dataset_name)

        # No need to keep the data in the captured function any more so remove it to save memory.
        # del table["data_frame"]
        return table

    # Convenience wrapper/syntactic sugar.
    def __call__(self, **kwargs):
        kwargs.setdefault("data_frame", data_manager._get_component_data(self.id))  # type: ignore[arg-type]
        return self.table(**kwargs)

    # Convenience wrapper/syntactic sugar.
    def __getitem__(self, arg_name: str):
        # pydantic discriminated union validation seems to try Graph["type"], which throws an error unless we
        # explicitly redirect it to the correct attribute.
        if arg_name == "type":
            return self.type
        return self.table[arg_name]

    @_log_call
    def build(self):
        data = data_manager._get_component_data(self.id)  # type: ignore
        additional_args = self.table._arguments.copy()
        additional_args.pop("data_frame", None)
        return html.Div(self.table._function(data_frame=data, **additional_args), id=self.id)
