"""Vizro-AI agents.

This module contains [pre-configured Pydantic AI agents](https://ai.pydantic.dev/agents/).
Below you can find a list of all agents available and their respective response models/types instructions.
For more information on how to use those agents, see the
[Pydantic AI agents documentation](https://ai.pydantic.dev/agents/).
"""

from ._chart_agent import chart_agent

__all__ = ["chart_agent"]
