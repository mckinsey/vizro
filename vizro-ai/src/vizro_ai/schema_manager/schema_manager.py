"""Schema manager for prepare llm calls."""

import inspect
from typing import Callable, List, Union

try:
    from pydantic.v1 import BaseModel, Field, create_model
except ImportError:  # pragma: no cov
    from pydantic import BaseModel, Field, create_model


class SchemaManager:
    """Schema manager to register functions or pydantic models."""

    def __init__(self):
        """Initialize list for function descriptions json schema."""
        self._descriptions = []

    def register(self, obj: Union[Callable, BaseModel]):
        """Register a function or a Pydantic model and extract its parameters for a description schema.

        Args:
            obj (Union[Callable, BaseModel]): function or pydantic model to register

        """
        if inspect.isfunction(obj):
            annotations = obj.__annotations__
            fields = {name: (annotations[name], ...) for name in annotations}
            temp_model = create_model(obj.__name__, **fields)
            # TODO see other direct transfer function to json methods
            schema = temp_model.schema()

        elif issubclass(obj, BaseModel):
            schema = obj.schema()

            for key, prop in schema["properties"].items():
                # Remove 'title' from properties
                prop.pop("title", None)
                field = obj.__fields__.get(key)
                if field and field.field_info.description:
                    prop["description"] = field.field_info.description.split("\n")[0]
        else:
            raise ValueError("The target to be registered should be either Function or Pydantic BaseModel")

        description = obj.__doc__.split("\n")[0] if obj.__doc__ else ""
        name = obj.__name__

        self._descriptions.append(
            {
                "name": name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": schema["properties"],
                    "required": schema.get("required", []),
                },
            }
        )

        return obj

    def get_llm_kwargs(self, names: Union[str, List[str]]) -> dict:
        """Generate the llm_kwargs based on the function name for constructing LLMChain."""
        functions_to_use = [func for func in self._descriptions if func["name"] in names]
        if len(functions_to_use) < 1:
            raise ValueError(f"Function or Model {names} not registered!")
        return {"functions": functions_to_use, "function_call": {"name": names}}

    def prepare_format_instruction(self) -> str:
        """Generate non function call format instructions in prompt."""
        # This is for non function call reply
        # Example format that it should return with a function

        # FORMAT_INSTRUCTIONS = """The way you reply is by specifying a json blob.
        # Specifically, this json should have a `chart_type` key (with the name of the tool to use)
        # {{{{
        #   "chart_type": $chart_type,
        # }}}}

        raise NotImplementedError("prepare_format_instruction for non open AI function call haven't been implemented")


if __name__ == "__main__":
    # Initialize the manager
    openai_manager = SchemaManager()

    # Register functions
    @openai_manager.register
    def choose_chart_type(chart_type: str):
        """Choose chart is the best to describe the user request or given data."""
        pass

    # Register Pydantic models
    @openai_manager.register
    class PandasCode(BaseModel):
        """Code for data manipulate."""

        dataframe_code: str = Field(..., description="code for data manipulate")

    # or register via below, for example import model from vizro-core
    class Pages(BaseModel):
        """Code for data manipulate."""

        number_of_pages: int = Field(..., description="split into the suitable number of pages")

    openai_manager.register(Pages)

    # Retrieve the llm_kwargs
    llm_kwargs1 = openai_manager.get_llm_kwargs("PandasCode")
    llm_kwargs2 = openai_manager.get_llm_kwargs("Pages")
    llm_kwargs3 = openai_manager.get_llm_kwargs(["chart", "PandasCode"])

    print(llm_kwargs3)  # noqa: T201
